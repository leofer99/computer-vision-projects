import os
import numpy as np
from ultralytics import YOLO

class HandDetector:
    """
    Wraps YOLO model and applies a buffer for smoothed hand centers + motion (dx, dy).
    """
    def __init__(self, model_path='yolov8n.pt', conf=0.5, buffer_size=5):
        self.model = YOLO(model_path)
        self.conf = conf
        self.buffer_size = buffer_size
        self.smooth_buffer = []   # list of lists per detected hand
        self.prev_positions = []  # list of (x,y) per detected hand

    def _ensure_buffers(self, n_hands):
        while len(self.smooth_buffer) < n_hands:
            self.smooth_buffer.append([])
        while len(self.prev_positions) < n_hands:
            self.prev_positions.append((0, 0))

    def predict(self, frame):
        """
        Returns list of hand dicts sorted left->right:
        {"cx","cy","w","h","dx","dy","label","index"}
        """
        results = self.model.predict(frame, conf=self.conf, verbose=False)
        if not results or not results[0].boxes:
            return []
        boxes = results[0].boxes.xywh.cpu().numpy()  # x_center, y_center, w, h
        if len(boxes) == 0:
            return []

        # Sort boxes by x-coordinate (left to right)  
        # Hand 1 is leftmost, Hand 2 is rightmost
        boxes_sorted = sorted(boxes, key=lambda b: b[0])
        n_hands = len(boxes_sorted)
        self._ensure_buffers(n_hands)

        hand_data = []
        for i, b in enumerate(boxes_sorted):
            x, y, w, h = b
            cx, cy = int(x), int(y)

            # Append current position to buffer
            buf = self.smooth_buffer[i]
            buf.append((cx, cy))
            
            if len(buf) > self.buffer_size:
                buf.pop(0)
            
            # Compute smoothed position
            avg_cx = int(np.mean([p[0] for p in buf]))
            avg_cy = int(np.mean([p[1] for p in buf]))

            # Compute dx/dy based on smoothed position
            dx = avg_cx - self.prev_positions[i][0]
            dy = avg_cy - self.prev_positions[i][1]
            self.prev_positions[i] = (avg_cx, avg_cy)

            # Save data
            label = "left" if n_hands > 1 and i == 0 else "right" if n_hands > 1 else "right"
            hand_data.append({
                "label": label,
                "index": i,
                "cx": avg_cx,
                "cy": avg_cy,
                "w": int(w),
                "h": int(h),
                "dx": int(dx),
                "dy": int(dy),
            })

        return hand_data
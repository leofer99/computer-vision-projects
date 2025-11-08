import os
import sys
import cv2

from src.hand_detector import HandDetector
from src.event_detector import EventDetector
from src.utils_visualizer import draw_rois, draw_hands, draw_event_text

# Configuration:
folder_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
video_path = os.path.join(folder_dir, 'tarefas_cima.mp4')
model_path = os.path.join(folder_dir, 'runs', 'detect', 'hands_detector_aug', 'weights', 'best.pt')
output_path = os.path.join(folder_dir, 'processed_video_output_no_ROI.mp4')

# Configure ROIs (left, top, right, bottom):
roi_piece = (700, 0, 1600, 900)
roi_probe = (800, 600, 1600, 900)
roi_box   = (0, 500, 1200, 900)
roi_mark = (1100, 600, 2000, 1300)

# Open video:
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print("Error: Unable to open video file")
    sys.exit(1)

fps = int(cap.get(cv2.CAP_PROP_FPS))
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Initialize VideoWriter for output:
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  
out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

# Initialize detectors:
detector = HandDetector(model_path, conf=0.5, buffer_size=5)
ed = EventDetector(roi_piece, roi_probe, roi_box, roi_mark, fps=fps, min_interval=2.0)


# Process video frames:
frame_idx = 0
while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame_idx += 1

    hand_data = detector.predict(frame)
    new_events = ed.update(hand_data, frame_idx, frame_height=frame.shape[0])

    # Draw ROIs, hands, and event text
    # draw_rois(frame, [
    #     (roi_piece, (255,0,0)), (roi_probe, (0,255,255)),
    #     (roi_box, (0,0,255)), (roi_mark, (255,255,0))
    # ])
    draw_hands(frame, hand_data)
    draw_event_text(frame, ed.events, fps, frame_idx)

    cv2.putText(frame, f"Time: {frame_idx/fps:.2f}s", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)
   
    # Write frame to output video
    out.write(frame)

    # Show live window
    cv2.imshow("Tracking", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
out.release()
cv2.destroyAllWindows()

# Save results
ed.save(os.path.join(folder_dir, "detected_events_1.json"))
print("Saved events:", ed.summary())
print(f"Video saved to: {output_path}")

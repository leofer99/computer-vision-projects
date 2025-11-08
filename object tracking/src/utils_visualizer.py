import cv2

def draw_rois(frame, rois):
    for roi, color in rois:
        x1,y1,x2,y2 = roi
        cv2.rectangle(frame, (x1,y1), (x2,y2), color, 2)

def draw_hands(frame, hand_data):
    for h in hand_data:
        x1 = int(h["cx"] - h.get("w",40)/2)
        y1 = int(h["cy"] - h.get("h",40)/2)
        x2 = int(h["cx"] + h.get("w",40)/2)
        y2 = int(h["cy"] + h.get("h",40)/2)
        cv2.rectangle(frame, (x1,y1), (x2,y2), (0,255,0), 2)
        cv2.circle(frame, (h["cx"], h["cy"]), 4, (0,255,0), -1)
        cv2.putText(frame, f'{h["label"]} dx={h["dx"]} dy={h["dy"]}', (x1, y1-8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,255), 1)

def draw_event_text(frame, events, fps, frame_idx):
    # show last timestamps for events for a short duration
    overlay_dur = 0.8

    EVENT_ORDER = ["pick_up", "probe_pass", "marking", "place_in_box"]
    COLORS = {
        "pick_up": (0, 0, 255),        # red
        "probe_pass": (0, 255, 255),   # yellow
        "marking": (255, 255, 0),      # cyan-ish (blue marker)
        "place_in_box": (0, 255, 0),   # green
    }

    y_start = 50
    y_step = 40

    cur_time = frame_idx / float(fps) if fps > 0 else 0.0
    x = frame.shape[1] // 2 - 150

    for idx, name in enumerate(EVENT_ORDER):
        lst = events.get(name, [])
        if not lst:
            continue
        last_t = lst[-1]
        if (cur_time - last_t) <= overlay_dur:
            color = COLORS.get(name, (0, 0, 255))
            text = name.replace("_", " ").upper() + "!"
            y = y_start + idx * y_step
            
            cv2.putText(frame, text, (x, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 3)
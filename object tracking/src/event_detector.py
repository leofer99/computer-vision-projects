import math

class EventDetector:
    """
    Encapsulates all event detection logic and state.
    Usage:
      ed = EventDetector(rois=..., fps=30)
      ed.update(hand_data, frame_idx)
      ed.events -> dict with timestamps lists
      ed.save(path)
    """
    def __init__(self, roi_piece, roi_probe, roi_box, roi_mark, fps=30, min_interval=2.0):
        self.roi_piece = roi_piece
        self.roi_probe = roi_probe
        self.roi_box = roi_box
        self.roi_mark = roi_mark
        self.fps = fps
        self.min_interval = min_interval

        self.events = {"pick_up": [], "probe_pass": [], "marking": [], "place_in_box": []}
        self.last_times = {"pick_up": None, "probe_pass": None, "marking": None, "place_in_box": None}
        self.last_event = []

    def inside_roi(self, x, y, roi):
        x1, y1, x2, y2 = roi
        return x1 <= x <= x2 and y1 <= y <= y2

    def event_allowed(self, current_event):

        has_pickup = len(self.events["pick_up"]) > 0
        has_box = len(self.events["place_in_box"]) > 0

        # Get timestamps for the most recent occurrences
        last_pickup = self.events["pick_up"][-1] if has_pickup else None
        last_box = self.events["place_in_box"][-1] if has_box else None

        # Pick-up is allowed if no pick-up has occurred yet,
        # or if the box placement happened after the last pick-up
        if current_event == "pick_up":
            if not has_pickup or (has_box and last_box > last_pickup):
                return True
            return False
    
        if current_event in ["probe_pass", "marking"]:
        # must have a pick_up, and no place_in_box yet for that same cycle
            if has_pickup and (not has_box or last_box < last_pickup):
                return True
            return False
        
        if current_event == "place_in_box":
         # must have a pick_up, and must not have already placed it
            if has_pickup and (not has_box or last_box < last_pickup):
                return True
            return False
        
        return False

    def _cooldown_ok(self, event_name, current_time, min_interval=None):
        last = self.last_times.get(event_name)
        interval = min_interval if min_interval is not None else self.min_interval

        return (last is None) or ((current_time - last) >= interval)

    def update(self, hand_data, frame_idx, frame_height=None):
        """
        Call once per frame. Updates event lists when detections occur.
        Returns list of (event_name, timestamp) newly detected this frame.
        """
        new = []
        t = frame_idx / float(self.fps)

        if not hand_data:
            return new

        # If there is only one hand, assumes it's the right hand
        left = hand_data[0] if len(hand_data) > 1 else None
        right = hand_data[1] if len(hand_data) > 1 else hand_data[0] 

        if left is not None and right is not None:

            # Pick-up Detection (left hand) 
            if self.event_allowed("pick_up") and self._cooldown_ok("pick_up", t):
                cx, cy, dx, dy = left["cx"], left["cy"], left["dx"], left["dy"]
            
                if self.inside_roi(cx, cy, self.roi_piece) and ((dy < -30) or (dy < -10 and dx > 30)):
                    self.events["pick_up"].append(t)
                    self.last_times["pick_up"] = t
                    new.append(("pick_up", t))

            # Probe Pass Detection (left+right)
            if self.event_allowed("probe_pass") and self._cooldown_ok("probe_pass", t)  and self._cooldown_ok("pick_up", t, min_interval=0.5):
                cx, cy = left["cx"], left["cy"]
                dx, dy = left["dx"], left["dy"]

                dist = math.hypot(left["cx"] - right["cx"], left["cy"] - right["cy"])
                condition_mov = (left["dy"] > 15) or (left["dy"] > 10 and left["dx"] > 10  )
                condition_dist = dist < 400

                if self.inside_roi(cx, cy, self.roi_probe) and condition_mov and condition_dist:
                    self.events["probe_pass"].append(t)
                    self.last_times["probe_pass"] = t
                    new.append(("probe_pass", t))

            # Marking Detection (right hand)
            if self.event_allowed("marking") and self._cooldown_ok("marking", t) and self._cooldown_ok("probe_pass", t, min_interval=1):
                
                dist = math.hypot(left["cx"] - right["cx"], left["cy"] - right["cy"])
                condition_dist = 200 < dist < 600
                condition_mov = 10 < abs(right["dy"]) #< 30
                if self.inside_roi(right["cx"], right["cy"], self.roi_mark) and  condition_mov and condition_dist:
                    self.events["marking"].append(t)
                    self.last_times["marking"] = t
                    new.append(("marking", t))

            # Place_in_box detection (left hand) - downward exit near bottom
            if self.event_allowed("place_in_box") and self._cooldown_ok("place_in_box", t):
                cx, cy, dx, dy = left["cx"], left["cy"], left["dx"], left["dy"]
                x1, y1, x2, y2 = self.roi_box

                frame_h = frame_height if frame_height is not None else y2
                bottom_exit = (dy > 15) and (cy > y2 - 10 or cy > frame_h - 20)
                
                if bottom_exit:
                    self.events["place_in_box"].append(t)
                    self.last_times["place_in_box"] = t
                    new.append(("place_in_box", t))

        return new

    def summary(self):
        return self.events

    def save(self, path):
        import json
        with open(path, "w") as f:
            json.dump(self.events, f, indent=4)

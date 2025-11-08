# Hand Motion Event Detection System

## Overview
This project implements a real-time hand motion tracking and event detection system using YOLOv8 and OpenCV. It can detect and analyze hand movements in video footage to recognize specific events like picking up objects, passing a probe through a piece, making a marking on the piece, and placing the piece in a box.

## Features
- Real-time hand detection and tracking using YOLOv8
- Motion smoothing with temporal buffer
- Event detection for four key actions:
  - Pick-up detection
  - Probe pass detection
  - Marking actions
  - Place-in-box detection
- Visual feedback with event notifications
- Performance metrics calculation

## Project Structure
```
├── challenge_hands/          # Dataset directory
│   ├── train/               # Training data
│   ├── val/                 # Validation data
│   ├── test/               # Test data
│   └── data.yaml           # Dataset configuration
├── src/
│   ├── hand_detector.py    # YOLO model wrapper
│   ├── event_detector.py   # Event detection logic
│   └── utils_visualizer.py # Visualization utilities
├── train_model.py          # Model training script
├── test_model_visual_oop.py # Visual testing script
├── split_train_test_val.py # Dataset splitting utility
└── detected_events.json    # Output events log
```

## Installation

1. Create and activate a conda environment:
```bash
conda create -n hand-detection python=3.8
conda activate hand-detection
```

2. Install PyTorch with CUDA support:
```bash
conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia
```

3. Install other dependencies:
```bash
pip install ultralytics opencv-python numpy scikit-learn pyyaml
```


### Dataset Preparation
1. Organize your hand detection dataset in YOLO format:
   - Images: `.jpg`, `.jpeg`, or `.png` files
   - Labels: `.txt` files with YOLO format annotations
   - Place in `challenge_hands/train/images` and `challenge_hands/train/labels`

2. Split dataset into train/val/test:
```bash
python split_train_test_val.py
```

3. Verify data.yaml configuration:
```yaml
path: path/to/challenge_hands  # update this
train: train/images
val: val/images
test: test/images
names:
  0: hand
```


### Training
1. Train the hand detection model:
```bash
python train_model.py
```
Training parameters can be modified in `train_model.py`:
```python
model.train(
    data=dataset_yaml,
    epochs=10,        # increase for better results
    imgsz=640,       # input resolution
    batch=8,         # reduce if GPU memory error
    name='hands_detector_aug',
)
```

### Testing
1. Run visual testing script:
```bash
python test_model_visual_oop.py
```

Controls:
- Press 'q' to quit
- Press 'p' to pause/resume
- Press 's' to save current frame


### Region of Interest (ROI) Settings
```python
# Adjust these in test_model_visual_oop.py
roi_piece = (700, 0, 1600, 900)    # Blue region
roi_probe = (800, 500, 1600, 900)   # Yellow region
roi_box = (0, 500, 1200, 900)       # Red region
roi_mark = (1100, 600, 2000, 1300)  # Marking area
```

### Event Detection Parameters
- Minimum interval between events: 2.0 seconds
- Motion thresholds in event_detector.py
- Temporal smoothing buffer size: 5 frames

## Event Detection Rules
### Event Rules
1. **Pick-up**: 
   - Left hand in piece region
   - Upward motion 
   - No recent pick-up event

2. **Probe Pass**:
   - Both hands in probe region
   - Downward motion
   - Small distance between the hands
   - No recent probe-pass event
   - No recent pick-up event (0.5s)

3. **Marking**:
   - Right hand in marking region
   - Vertical motion
   - Small distance between the hands
   - No recent marking event
   - No recent probe-pass event (1s)

4. **Place-in-box**:
   - Downward motion at bottom of frame
   - Previous pick-up event exists
   - No recent place-in-box event


### Event Log (detected_events.json)
```json
{
    "pick_up": [],
    "probe_pass": [],
    "marking": [],
    "place_in_box": []
}
```

### Performance Metrics
Run analysis:
```bash
python performance_metrics.py
```
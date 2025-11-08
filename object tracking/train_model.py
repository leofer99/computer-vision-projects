import os
import sys
import cv2

from ultralytics import YOLO


folder_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))

dataset_yaml = os.path.join(folder_dir, 'challenge_hands', 'data.yaml')
# hyp_yaml = os.path.join(folder_dir, 'hyp.custom.yaml')


# Load pretrained model
model = YOLO('yolov8n.pt')


# Train on your dataset
model.train(
    data=dataset_yaml,
    epochs=2, # increase epochs
    imgsz=640, # image size, defalut is 640 (+, +detail and + training time)
    batch=8, #batch size, (-, -GPU memory usage)
    name='hands_detector_aug',

)


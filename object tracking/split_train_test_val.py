import os
import shutil
from sklearn.model_selection import train_test_split

# Define paths
base_dir = os.path.abspath(os.path.dirname(__file__))
train_dir = os.path.join(base_dir, 'challenge_hands', 'train')
train_images = os.path.join(train_dir, 'images')
train_labels = os.path.join(train_dir, 'labels')

# Create validation and test directories
val_dir = os.path.join(base_dir, 'challenge_hands', 'val')
test_dir = os.path.join(base_dir, 'challenge_hands', 'test')

for dir_path in [val_dir, test_dir]:
    os.makedirs(os.path.join(dir_path, 'images'), exist_ok=True)
    os.makedirs(os.path.join(dir_path, 'labels'), exist_ok=True)

# Get all image files
image_files = [f for f in os.listdir(train_images) if f.endswith(('.jpg', '.jpeg', '.png'))]

# Split into train/val/test (70%/20%/10%)
train_files, other_files = train_test_split(image_files, test_size=0.3, random_state=42)
val_files, test_files = train_test_split(other_files, test_size=0.33, random_state=42)


# Function to move files (both image and its corresponding label)
def move_files(files, source_dir, dest_dir):
    for f in files:
        # Move image
        src_img = os.path.join(source_dir, 'images', f)
        dst_img = os.path.join(dest_dir, 'images', f)
        shutil.copy2(src_img, dst_img)
        
        # Move corresponding label file
        label_f = os.path.splitext(f)[0] + '.txt'
        src_label = os.path.join(source_dir, 'labels', label_f)
        dst_label = os.path.join(dest_dir, 'labels', label_f)
        if os.path.exists(src_label):
            shutil.copy2(src_label, dst_label)

# Move files to val and test directories
move_files(val_files, train_dir, val_dir)
move_files(test_files, train_dir, test_dir)

# Create/update data.yaml
yaml_content = f"""
path: {os.path.join(base_dir, 'challenge_hands')}  # dataset root dir
train: train/images  # train images (relative to 'path')
val: val/images      # val images (relative to 'path')
test: test/images    # test images (optional)

# Classes
names:
  0: hand
"""

with open(os.path.join(base_dir, 'challenge_hands', 'data.yaml'), 'w') as f:
    f.write(yaml_content)

print(f"Dataset split complete:")
print(f"Train: {len(train_files)} images")
print(f"Validation: {len(val_files)} images")
print(f"Test: {len(test_files)} images")
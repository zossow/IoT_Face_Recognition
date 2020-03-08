import cv2
import time
import argparse
import numpy as np
import matplotlib.pyplot as plt
from detector import FaceDetector
from nms import non_max_suppression
from skimage.transform import pyramid_reduce
from skimage.transform import pyramid_gaussian

# Read command-line arguments
ap = argparse.ArgumentParser()
ap.add_argument('-i', '--image', required=True, help='Path to the image')
ap.add_argument('-s', '--step', required=False,
                help='Window step size', default=32, type=int)
args = vars(ap.parse_args())

# Initialize sliding window parameters
step_size = args['step']
window_size = (128, 128)

# Initialize source/original image
src = plt.imread(args['image'])

# Initialize face detector
detector = FaceDetector('model/weights.pkl')


def sliding_window(image, step_size, window_size):
    """Slide a window across an image."""
    for y in range(0, image.shape[0], step_size):
        for x in range(0, image.shape[1], step_size):
            # Create window
            yield x, y, image[y:y+window_size[1], x:x+window_size[0]]


def display_image(image):
    """Display an image."""
    plt.axis('off')
    plt.imshow(image)
    # Save result
    plt.savefig('outputs/result.png')
    plt.show()


# Start detection process
boxes = []
scale_factor = 1
for img in pyramid_gaussian(np.copy(src), downscale=2, multichannel=True):
    # Break if the scaled image is smaller than the window
    if img.shape[0] < window_size[0] or img.shape[1] < window_size[1]:
        break

    for (x, y, window) in sliding_window(img, step_size, window_size):
        # Continue if window does not meet desired size
        if window.shape[0] < window_size[0] or window.shape[1] < window_size[1]:
            continue

        # Detect a face
        confidence = detector.detect(window)
        if confidence > 0:
            x1 = x * scale_factor
            y1 = y * scale_factor
            x2 = x1 + window_size[1] * scale_factor
            y2 = y1 + window_size[0] * scale_factor
            boxes.append((x1, y1, x2, y2, confidence))

    # Keep track of current scale factor
    scale_factor *= 2

# Check if there are detections
if len(boxes) == 0:
    print('No faces detected')
    exit()

# Apply non-maximum suppression
boxes = non_max_suppression(np.array(boxes), overlapThresh=0.3)

# Draw bounding boxes
clone = src.copy()
for box in boxes:
    x1, y1 = box[0], box[1]
    x2, y2 = box[2], box[3]
    cv2.rectangle(clone, (x1, y1), (x2, y2), (0, 255, 0), 2)

# Display final result
display_image(clone)
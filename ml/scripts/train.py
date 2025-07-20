import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np
import cv2
import os
import json

# Constants
IMAGE_SIZE = (128, 128)
OUTPUT_SIZE = 22  # Adjust to actual number of encoded parameters
DATA_DIR = 'data/'

# Encode a single settings JSON into a normalized numpy vector
def encode_settings(settings):
    vec = []

    bf = settings["bilateralFilter"]
    vec.append(1.0 if bf["disabledBilateralFilter"] else 0.0)
    vec.append(bf["pixelDiameter"] / 100.0)
    vec.append(bf["sigmaColor"] / 255.0)
    vec.append(bf["sigmaSpace"] / 255.0)

    vec.append(settings["blur"]["blurWidth"] / 100.0)

    at = settings["adaptiveThreshold"]
    vec.append(at["maxValue"] / 255.0)
    vec.append(at["blockSize"] / 100.0)

    cp = settings["cannyPaper"]
    vec.append(cp["firstThreshold"] / 255.0)
    vec.append(cp["secondThreshold"] / 255.0)

    ccp = settings["closeCornersPaper"]
    vec.append(ccp["kernelSize"] / 100.0)
    vec.append(ccp["iterations"] / 10.0)

    vec.append(settings["blurObject"]["blurWidth"] / 100.0)

    # objectThreshold
    ot = settings["objectThreshold"]
    vec.append(0.0 if ot["thresholdType"] == "binary" else 1.0)

    bs = ot["binarySettings"]
    vec.append(bs["threshold"] / 255.0)
    vec.append(bs["inverseThreshold"] / 255.0)
    vec.append(bs["maxValue"] / 255.0)

    ads = ot["adaptiveSettings"]
    vec.append(ads["maxValue"] / 255.0)
    vec.append(ads["blockSize"] / 100.0)

    co = settings["cannyObject"]
    vec.append(co["firstThreshold"] / 255.0)
    vec.append(co["secondThreshold"] / 255.0)

    cc = settings["closeCorners"]
    vec.append(cc["kernelSize"] / 100.0)
    vec.append(cc["iterations"] / 10.0)

    return np.array(vec, dtype=np.float32)

def find_image_path(sample_path):
    # Supported extensions
    for ext in ['jpg', 'jpeg', 'png']:
        candidate = os.path.join(sample_path, f'image.{ext}')
        if os.path.isfile(candidate):
            return candidate
    raise FileNotFoundError(f"No supported image found in {sample_path}")


# Example image loader
def load_image(path):
    img = cv2.imread(path)
    img = cv2.resize(img, IMAGE_SIZE)
    img = img / 255.0  # Normalize
    return img

# Dataset creation
def create_dataset(folder):
    images = []
    labels = []
    for sample_folder in os.listdir(DATA_DIR):
        sample_path = os.path.join(DATA_DIR, sample_folder)
        if os.path.isdir(sample_path):
            # TODO auto detect if the image is in png or jpeg (also jpg)
            img_path = find_image_path(sample_path)
            settings_path = os.path.join(sample_path, 'settings.json')
            
            # Load image
            img = load_image(img_path)
            images.append(img)

            # Load settings
            with open(settings_path, 'r') as f:
                settings_json = json.load(f)
                vec = encode_settings(settings_json["settings"])
                labels.append(vec)

    return np.array(images, dtype=np.float32), np.array(labels, dtype=np.float32)

# Load data
X, y = create_dataset(DATA_DIR)

print(f"Images shape: {X.shape}, Labels shape: {y.shape}")

# Build model
model = keras.Sequential([
    layers.Input(shape=(IMAGE_SIZE[0], IMAGE_SIZE[1], 3)),
    layers.Conv2D(32, (3,3), activation='relu'),
    layers.MaxPooling2D((2,2)),
    layers.Conv2D(64, (3,3), activation='relu'),
    layers.MaxPooling2D((2,2)),
    layers.Conv2D(128, (3,3), activation='relu'),
    layers.MaxPooling2D((2,2)),
    layers.Flatten(),
    layers.Dense(256, activation='relu'),
    layers.Dense(OUTPUT_SIZE, activation='linear')
])

model.compile(optimizer='adam', loss='mse', metrics=['mae'])
model.summary()

# Train
model.fit(X, y, epochs=20, batch_size=16, validation_split=0.2)

# Save
model.save('settings_predictor_model.keras')

# Convert to TensorFlow.js (run in terminal):
# tensorflowjs_converter --input_format=tf_saved_model --output_format=tfjs_graph_model settings_predictor_model tfjs_model/

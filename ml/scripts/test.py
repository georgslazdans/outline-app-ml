import tensorflow as tf
import numpy as np
import cv2
import json

# 🔧 Load your trained model
model = tf.keras.models.load_model('settings_predictor_model.keras')

IMAGE_SIZE = (128, 128)

import numpy as np

def decode_settings(vec):
    # Ensure input is a numpy array
    vec = np.array(vec)

    settings = {}

    i = 0

    settings["bilateralFilter"] = {
        "disabledBilateralFilter": True if vec[i] >= 0.5 else False,
        "pixelDiameter": int(vec[i+1] * 100),
        "sigmaColor": int(vec[i+2] * 255),
        "sigmaSpace": int(vec[i+3] * 255)
    }
    i += 4

    settings["blur"] = {
        "blurWidth": int(vec[i] * 100)
    }
    i += 1

    settings["adaptiveThreshold"] = {
        "maxValue": int(vec[i] * 255),
        "blockSize": int(vec[i+1] * 100),
        "c": 2  # Fixed as per your original
    }
    i += 2

    settings["cannyPaper"] = {
        "firstThreshold": int(vec[i] * 255),
        "secondThreshold": int(vec[i+1] * 255)
    }
    i += 2

    settings["closeCornersPaper"] = {
        "kernelSize": int(vec[i] * 100),
        "iterations": int(vec[i+1] * 10)
    }
    i += 2

    settings["blurObject"] = {
        "blurWidth": int(vec[i] * 100)
    }
    i += 1

    # objectThreshold
    threshold_type = "binary" if vec[i] < 0.5 else "adaptive"
    i += 1

    settings["objectThreshold"] = {
        "thresholdType": threshold_type,
        "binarySettings": {
            "threshold": int(vec[i] * 255),
            "inverseThreshold": int(vec[i+1] * 255),
            "maxValue": int(vec[i+2] * 255)
        },
        "adaptiveSettings": {
            "maxValue": int(vec[i+3] * 255),
            "blockSize": int(vec[i+4] * 100),
            "c": 2  # Fixed as per your original
        }
    }
    i += 5

    settings["cannyObject"] = {
        "firstThreshold": int(vec[i] * 255),
        "secondThreshold": int(vec[i+1] * 255)
    }
    i += 2

    settings["closeCorners"] = {
        "kernelSize": int(vec[i] * 100),
        "iterations": int(vec[i+1] * 10)
    }
    i += 2

    return settings


# 🔧 Load and preprocess test image
def load_image(path):
    img = cv2.imread(path)
    img = cv2.resize(img, IMAGE_SIZE)
    img = img / 255.0
    return img

test_img = load_image('data/multi_tools.jpg')
test_img = np.expand_dims(test_img, axis=0)  # Add batch dimension

# 🔧 Predict
predicted_params = model.predict(test_img)[0]  # Remove batch dimension

print("Raw predicted parameters:")
print(predicted_params)

decoded_json = decode_settings(predicted_params)

print(json.dumps(decoded_json, indent=2))

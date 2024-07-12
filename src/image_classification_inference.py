import numpy as np
import os
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator

screenshots_dir = './screenshots'
target_resolution = (480, 270)  # Resolution of 270p

# TODO: upload to huggingface
pretrained_model_path = 'menu_vs_match_model.h5'

 # Load the pretrained model
model = tf.keras.models.load_model(pretrained_model_path)

# Preprocess images
datagen = ImageDataGenerator(rescale=1./255)

def load_and_preprocess_image(file_path):
    img = tf.keras.preprocessing.image.load_img(file_path, target_size=target_resolution)
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    return datagen.standardize(img_array)

class_labels = ['in-match', 'in-menu']

for file in os.listdir(screenshots_dir):
    if file.endswith(('.png', '.jpg', '.jpeg')):
        file_path = os.path.join(screenshots_dir, file)
        img = load_and_preprocess_image(file_path)

        # Make prediction
        prediction = model.predict(img)
        print(prediction)
        
        # Get the class label with the highest probability
        predicted_class = np.argmax(prediction)
        status = class_labels[predicted_class]

        # Print the result
        print(f'The image {file} is predicted to be: {status}')
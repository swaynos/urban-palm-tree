import asyncio
import logging
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from huggingface_hub import hf_hub_download

import config

logger = logging.getLogger(__name__)

class ImageClassifier:

    def __init__(self, modelpath, filename, class_labels, target_resolution=(480, 270)):
        self.modelpath = hf_hub_download(modelpath, filename)
        self.model = tf.keras.models.load_model(self.modelpath)
        # Compile the loaded model specifying metrics
        self.model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

        self.class_labels = class_labels
        self.target_resolution = target_resolution
        self.datagen = ImageDataGenerator(rescale=1./255)

    async def classify_image(self, image_wrapper):
        logger.debug(f"Classifying image from latest screenshot using {self.modelpath}")
        img = await self.load_and_preprocess_image(image_wrapper)
        predictions = await asyncio.to_thread(self.model.predict, img)

        predicted_class = self.class_labels[np.argmax(predictions)]

        return predicted_class, predictions

    async def load_and_preprocess_image(self, image_wrapper):
        img_array = image_wrapper._imageArray
        
        # Check the number of channels; if 4, drop the alpha channel
        if img_array.shape[-1] == 4:
            img_array = img_array[..., :3]
        
        # Resize image if needed
        if img_array.shape[:2] != self.target_resolution:
            img_array = tf.image.resize(img_array, self.target_resolution).numpy()

        # Convert the image array to float32 for preprocessing
        img_array = img_array.astype(np.float32)

        img_array = np.expand_dims(img_array, axis=0)
        img_processed = await asyncio.to_thread(self.datagen.standardize, img_array)
        
        return img_processed

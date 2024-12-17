import asyncio
import logging
import numpy as np
import tensorflow as tf
from ultralytics import YOLO
from huggingface_hub import hf_hub_download

import config

logger = logging.getLogger(__name__)

class YoloImageClassifier:

    def __init__(self, modelpath, filename, target_resolution=(640, 640)):
        self.modelpath = hf_hub_download(modelpath, filename)
        self.model = YOLO(self.modelpath)

        self.target_resolution = target_resolution

    async def classify_image(self, image_wrapper):
        logger.debug(f"Classifying image from latest screenshot using {self.modelpath}")
        img = await self.load_and_preprocess_image(image_wrapper)
        
        results = self.model.predict(source=img, imgsz=640, conf=0.25)
        #predictions = await asyncio.to_thread(self.model.predict, img)

        predicted_classes = [self.class_labels[np.argmax(prediction)] for prediction in predictions]

        return predicted_classes

    async def load_and_preprocess_image(self, image_wrapper):
        img_array = image_wrapper._imageArray
        
        # Check the number of channels; if 4, drop the alpha channel
        if img_array.shape[-1] == 4:
            img_array = img_array[..., :3]
        
        # Resize image if needed
        img_array = tf.image.resize(img_array, self.target_resolution).numpy()

        # Normalize the image array
        img_array = img_array / 255.0

        img_array = np.expand_dims(img_array, axis=0)
        
        return img_array

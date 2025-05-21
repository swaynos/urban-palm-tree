import time
import aiofiles
import numpy as np
import base64
import cv2
import io
from PIL.Image import Image as PILImage
from PIL import Image


from skimage.metrics import structural_similarity as ssim

import utilities.config as config

image_format = "PNG"

def load_template_grayscale(template_name):
    """Load a grayscale template image from disk."""
    template = cv2.imread("screenshots/{}".format(template_name))
    return cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

# TODO: Unit Tests
class ImageWrapper:
    """A class to represent an image. Wraps a PIL Image and a MatLike which is used by OpenCV."""
    def __init__(self, image, saved_path=None):
        self._timestamp:float = time.time()

        if isinstance(image, PILImage):
            self._image = image
            self._imageArray = np.array(image)
        elif isinstance(image, np.ndarray):
            self._imageArray = image
            self._image = PILImage.fromarray(image)
        else:
            raise ValueError("Unsupported image type: must be a PIL.Image.Image or a numpy.ndarray")
        self.saved_path = saved_path

    @classmethod
    def load_image_from_file(self, file_path: str):
        """Load an image from a file and return an instance of ImageWrapper."""
        # Open image using PIL
        image = Image.open(file_path)
        return self(image)  # Return an instance of ImageWrapper with PIL Image

    def resize(self, width, height):
        self._image = self._image.resize((width, height), Image.LANCZOS)

    # Function to crop and resize the image to new size, while maintain the aspect ratio of 16x9
    def crop_and_resize_to_height(self, width, height):
        # TODO: Validate width, height are 16:9 aspect ratio?
        original_width, original_height = self._image.size

        aspect_ratio = 16 / 9

        # Calculate new dimensions maintaining the aspect ratio
        if original_width / original_height >= aspect_ratio:
            # Image is wider than 16:9
            new_height = original_height
            new_width = int(original_height * aspect_ratio)
        else:
            # Image is taller than 16:9
            new_width = original_width
            new_height = int(original_width / aspect_ratio)
        
        # Calculate the cropping box to crop from the center
        left = (original_width - new_width) / 2
        top = (original_height - new_height) / 2
        right = (original_width + new_width) / 2
        bottom = (original_height + new_height) / 2

        # Crop the image
        cropped_img = self._image.crop((left, top, right, bottom))
        
        # Resize the image to new size
        resized_img = cropped_img.resize((width, height), Image.LANCZOS)

        return resized_img

    # Image manipulation
    def to_bytes(self, image_format='JPEG', quality=85) -> bytes:
        """Convert a PIL Image to a compressed byte array."""
        img_byte_arr = io.BytesIO()
        
        # Convert to RGB if the image has an alpha channel
        if self._image.mode == 'RGBA':
            image_rgb = self._image.convert('RGB')
        else:
            image_rgb = self._image
        
        image_rgb.save(img_byte_arr, format=image_format, quality=quality)  # Save with compression
        img_byte_arr.seek(0)  # Seek to the beginning of the BytesIO buffer
        return img_byte_arr.getvalue()  # Return the byte array
    
    def scaled_as_base64(self, width=640, height=360, encoding ='utf-8'):
        """
        The scaled_as_base64 method scales the image (for better performance) 
        and then converts the image into a base64 encoded string.
        It takes the width and height, optional with defaults to 360p
        It takes an encoding parameter, which is optional and defaults to 'utf-8'.
        """
        # Scale the image
        scaled_image = self._image.resize((width, height))
        # Convert the image to bytes in memory
        image_bytes = io.BytesIO()
        scaled_image.save(image_bytes, format=image_format)
        image_base64 = base64.b64encode(image_bytes.getvalue()).decode(encoding)
        return image_base64

    def return_region_as_base64(self, x:int, y:int, width:int, height:int, encoding ='utf-8'):
        """
        Returns the base64 encoded string of the region defined by the coordinates.
        """
        # Crop the specified region
        deltaX = x+width
        deltaY = y+height
        cropped_img = self._image.crop((x, y, deltaX, deltaY))
        # Convert the image to bytes in memory
        image_bytes = io.BytesIO()
        cropped_img.save(image_bytes, format=image_format)

        image_base64 = base64.b64encode(image_bytes.getvalue()).decode(encoding)
        return image_base64

    # SSIM Comparisons
    # TODO: If SSIM is still needed for this project, consider caching the templates
    def compare_region_ssim(self, template_name:str, x:int, y:int, width:int, height:int):
        """
        Compares an image to a template using structural similarity (SSIM).
        
        Parameters:
            template_name (str): The name of the template file.
            x (int): The X coordinate of the top-left corner of the region to compare.
            y (int): The Y coordinate of the top-left corner of the region to compare.
            width (int): The width of the region to compare.
            height (int): The height of the region to compare.
        
        Returns:
            A float representing the similarity between the image and the template, with higher values indicating greater similarity.
        """
        # Crop the specified region
        cropped_img = self._imageArray[y:height+y, x:width+x]
        cropped_img_grayscale = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)
        cropped_template_grayscale = load_template_grayscale(template_name)[y:height+y, x:width+x]
      
        # Calculate SSIM
        ssim_score = ssim(cropped_template_grayscale, cropped_img_grayscale)

        return ssim_score

    def compare_ssim(self, template_name:str):
        """
        Compares an image to a template using structural similarity (SSIM).
        
        Parameters:
            template_name (str): The name of the template file.
        
        Returns:
            A float representing the similarity between the image and the template, with higher values indicating greater similarity.
        """
         
        gray_template = load_template_grayscale(template_name)

        # Convert the image to grayscale
        gray_image = cv2.cvtColor(self._imageArray, cv2.COLOR_BGR2GRAY)

        # Calculate SSIM
        ssim_score = ssim(gray_template, gray_image)

        return ssim_score
    
    # Pixel-by-Pixel Comparison
    def compare_grayscale_to_template(self, template_name):
        """
        Returns a similarity threshold, which could be used for comparisons.
        """
        gray_template = load_template_grayscale(template_name)

        # Convert the image to grayscale
        gray_image = cv2.cvtColor(self._imageArray, cv2.COLOR_BGR2GRAY)

        # Calculate the element-wise difference
        diff = np.abs(gray_template - gray_image)

        # Calculate the norm of the difference
        norm_diff = np.linalg.norm(diff)

        return norm_diff
    
    def compare_timestamp(self, timestamp):
        """
        Compares the timestamp of the image to a given timestamp.
        """
        timestamp_difference = timestamp - self._timestamp
        return timestamp_difference

    async def async_save_image(self, path: str):
        """
        Asynchronously saves an image to a file.
        
        Parameters:
            path (str): The path and filename of the output file.
        """
        if config.SAVE_SCREENSHOTS:
            # Save the image to a BytesIO buffer
            buffer = io.BytesIO()
            self._image.save(buffer, format=image_format)
            buffer.seek(0)

            # Write the buffer content to a file asynchronously
            async with aiofiles.open(path, 'wb') as out_file:
                await out_file.write(buffer.read())
                self.saved_path = path

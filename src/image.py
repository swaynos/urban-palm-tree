import numpy as np
import base64
import cv2
import io
from PIL import Image

from skimage.metrics import structural_similarity as ssim

def load_template_grayscale(template_name):
    """Load a grayscale template image from disk."""
    template = cv2.imread("screenshots/{}".format(template_name))
    return cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

# TODO: Cache templates
# TODO: Unit Tests
class ImageWrapper:
    """A class to represent an image. Wraps MatLike which is used by openCV.
    """
    def __init__(self, image: cv2.typing.MatLike):
        if isinstance(image, Image.Image):
            # TODO: Determine if we need to convert to numpy array? Can't we keep it as MatLike since that is what is expected in cv2?
            array = np.array(image)
            self._image = image
            self._imageArray = array
        else:
            # TODO: Set self._image from array
            self._imageArray = image

    def __getattr__(self, name):
        """Delegate access to the wrapped object's attributes."""
        return getattr(self._imageArray, name)

    # The scaled_as_base64 method scales the image (for better performance) 
    # and then converts the image into a base64 encoded string.
    # It takes the width and height, optional with defaults to 360p
    # It takes an encoding parameter, which is optional and defaults to 'utf-8'.
    def scaled_as_base64(self, width=640, height=360, encoding ='utf-8'):
        # Scale the image

        scaled_image = self._image.resize((width, height))
        # Convert the image to bytes in memory
        image_bytes = io.BytesIO()
        scaled_image.save(image_bytes, format="PNG")
        image_base64 = base64.b64encode(image_bytes.getvalue()).decode(encoding)
        return image_base64

    # SSIM
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
    
    # Pixel-by-Pixel Difference
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
import numpy as np
import cv2
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
            array = np.array(image)
            self._image = array
        else:
            self._image = image

    def __getattr__(self, name):
        """Delegate access to the wrapped object's attributes."""
        return getattr(self._image, name)

    # SSIM
    def compare_ssim(self, template_name):
        """
        Returns the structural similarity index of the image.
        SSIM, which compares structural patterns in the images rather than pixel values.
        """
        gray_template = load_template_grayscale(template_name)

        # Convert the image to grayscale
        gray_image = cv2.cvtColor(self._image, cv2.COLOR_BGR2GRAY)

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
        gray_image = cv2.cvtColor(self._image, cv2.COLOR_BGR2GRAY)

        # Calculate the element-wise difference
        diff = np.abs(gray_template - gray_image)

        # Calculate the norm of the difference
        norm_diff = np.linalg.norm(diff)

        return norm_diff
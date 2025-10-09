import cv2
import numpy as np

def upscale_and_sharpen(img, scale_factor=2, sharpen_amount=0.5, sharpen_radius=3):
    """
    Upscales an image using Lanczos interpolation and then applies an
    unsharp mask to enhance sharpness.

    :param img: The input image (as a numpy array).
    :param scale_factor: The factor by which to scale the image (e.g., 2 for 2x).
    :param sharpen_amount: The intensity of the sharpening. Good values are 0.5 to 1.5.
    :param sharpen_radius: The radius for the Gaussian blur used in the unsharp mask.
                           Smaller values (1-3) sharpen finer details.
    """
    # Get original dimensions and calculate new dimensions
    height, width = img.shape[:2]
    new_dimensions = (int(width * scale_factor), int(height * scale_factor))

    # 1. Upscale the image using a high-quality interpolator
    upscaled_img = cv2.resize(img, new_dimensions, interpolation=cv2.INTER_LANCZOS4)
    # If the image is grayscale, it needs to be converted to BGR for addWeighted
    if len(upscaled_img.shape) == 2:
        upscaled_img = cv2.cvtColor(upscaled_img, cv2.COLOR_GRAY2BGR)

    # 2. Apply sharpening using an unsharp mask
    # Create a blurred version of the upscaled image
    gaussian_blur = cv2.GaussianBlur(upscaled_img, (0, 0), sharpen_radius)
    
    # Subtract the blurred version from the upscaled version to get the "details"
    # and add them back to the upscaled image to sharpen it.
    # The formula is: sharpened = original * (1 + amount) + blurred * (-amount)
    sharpened_img = cv2.addWeighted(upscaled_img, 1 + sharpen_amount, gaussian_blur, -sharpen_amount, 0)

    return sharpened_img

img = cv2.imread('score_0.png', cv2.IMREAD_GRAYSCALE)
# dimensions = img.shape[0:2]
# dimensions = dimensions[::-1] # img.shape is (y, x) so reverse it to (x, y)
# scale_factor = 2
# new_x = int(dimensions[0] * scale_factor)
# new_y = int(dimensions[1] * scale_factor)   
# dimensions = (new_x, new_y)
# inter_nearest = cv2.resize(src=img, dsize=dimensions, interpolation=cv2.INTER_NEAREST)
# inter_linear = cv2.resize(src=img, dsize=dimensions, interpolation=cv2.INTER_LINEAR)
# inter_cubic = cv2.resize(src=img, dsize=dimensions, interpolation=cv2.INTER_CUBIC)
# inter_lanczos4 = cv2.resize(src=img, dsize=dimensions, interpolation=cv2.INTER_LANCZOS4)

# save the resized images to file
# cv2.imwrite('inter_nearest.png', inter_nearest)
# cv2.imwrite('inter_linear.png', inter_linear)
# cv2.imwrite('inter_cubic.png', inter_cubic)
# cv2.imwrite('inter_lanczos4.png', inter_lanczos4)

# Use custom upscaler
# THIS ONE IS BEST SO FAR
custom_upscaled = upscale_and_sharpen(img, scale_factor=2, sharpen_amount=0.5, sharpen_radius=3)
cv2.imwrite('custom_upscaled.png', custom_upscaled)

# More intense sharpening on finer details
# more_sharpened = upscale_and_sharpen(img, scale_factor=2, sharpen_amount=1.0, sharpen_radius=1)
# cv2.imwrite('custom_upscaled_more_sharp.png', more_sharpened)
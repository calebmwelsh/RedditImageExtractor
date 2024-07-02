import cv2 as cv
import cv2 as cv2


def rescaleFrame(frame, scale=0.75):
    # Images, Videos and Live Video
    width = int(frame.shape[1] * scale)
    height = int(frame.shape[0] * scale)

    dimensions = (width, height)

    return cv.resize(frame, dimensions, interpolation=cv.INTER_AREA)


def display_image(image, name, resize=0.2):
    # Display the image
    resized = rescaleFrame(image, scale=resize)
    cv.imshow(name, resized)


def find_scale_ratio(bigger_image, smaller_image):
    # Get the dimensions of the images
    height_bigger, width_bigger = bigger_image.shape[:2]
    height_smaller, width_smaller = smaller_image.shape[:2]

    # Calculate the scale ratio based on width
    scale_ratio = width_smaller / width_bigger

    if width_smaller < height_smaller:
        # Scale the dimensions of the bigger image to match the width of the smaller image
        new_width_bigger = width_smaller
        new_height_bigger = int(height_bigger * scale_ratio)
    else:
        # Scale the dimensions of the bigger image to match the height of the smaller image
        new_width_bigger = int(width_bigger * scale_ratio)
        new_height_bigger = height_smaller

    # Resize the bigger image to match the width of the smaller image
    resized_bigger_image = cv2.resize(
        bigger_image, (new_width_bigger, new_height_bigger)
    )

    # Check if the height needs adjustment
    height_difference = new_height_bigger - height_smaller
    if height_difference != 0:
        # Remove a pixel layer from the top and bottom alternately until the heights match
        iterations = abs(height_difference)
        for i in range(iterations):
            if height_difference > 0:
                resized_bigger_image = resized_bigger_image[1:, :]
            else:
                resized_bigger_image = resized_bigger_image[:-1, :]

            # Update the height difference
            height_difference = resized_bigger_image.shape[0] - height_smaller

            # Break if heights match
            if height_difference == 0:
                break

    return resized_bigger_image

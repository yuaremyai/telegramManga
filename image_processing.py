import cv2
import numpy as np
import search_title


def get_image(url):
    response = search_title.download_image(url)
    image = np.asarray(bytearray(response), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    return image


def cut_image(image):
    cutted_image = []
    max_size = 1080
    shape = image.shape[0]
    cuts_count = shape // max_size if shape % max_size < 400 else shape//max_size+1
    for i in range(cuts_count):
        if i + 1 == cuts_count:
            crop_img = image[i * max_size:shape, 0:image.shape[1]]
            cutted_image.append(crop_img)
            return cutted_image
        crop_img = image[i*max_size:(i+1)*max_size, 0:image.shape[1]]
        cutted_image.append(crop_img)


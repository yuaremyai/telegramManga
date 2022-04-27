import cv2
import numpy as np
from search_title import Search


def get_image(url):
    search = Search()
    response = search.download_image(url)
    image = np.asarray(bytearray(response), dtype="uint8")
    return image


def cut_image(image):
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    cutted_image = []
    max_size = 1080
    shape = image.shape[0]
    cuts_count = shape // max_size if shape % max_size < 400 else shape//max_size+1
    for i in range(cuts_count):
        if i + 1 == cuts_count:
            crop_img = image[i * max_size:shape, 0:image.shape[1]]
            encode = cv2.imencode(".jpg", crop_img)[1]
            data = np.array(encode)
            cutted_image.append(data.tobytes())
            return cutted_image
        crop_img = image[i*max_size:(i+1)*max_size, 0:image.shape[1]]
        encode = cv2.imencode(".jpg", crop_img)[1]
        data = np.array(encode)
        cutted_image.append(data.tobytes())

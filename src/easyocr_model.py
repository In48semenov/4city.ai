import io
import math
from typing import List

import cv2
import easyocr
import numpy as np
import uuid

class EasyOCRModel:
    """
    Класс модели EasyOCR
    """

    def __init__(self, lang_list: list = ['ru', 'en'],
                 text_threshold: float = 0.3,
                 gpu: bool = True,
                 paragraph: bool = True,
                 detail: int = 1,
                 decoder: str = 'greedy'):

        self.text_threshold = text_threshold
        self.paragraph = paragraph
        self.detail = detail
        self.decoder = decoder
        self.model = easyocr.Reader(lang_list=lang_list, gpu=gpu)
        """
        :lang_list: список языков для распознавания 
        :type lang_list: list
        :text_threshold: порог для детекции текста
        :type text_threshold: float
        :paragraph: метод объединения текста в один параграф.
        :type paragraph: bool
        :detail: метод для подробного вывода ответа моделью. detail=1 выводит 
        bbox.
        :type detail: bool
        :decoder: Тип декодера. Для русского языка доступен 'greedy'
        :type decoder: str
        """

    def _infer(self, image) -> List[str]:
        """
        Метод для детекции и распознования текста.
        :image: изображение в формате bytearray
        :type: bytearray
        """

        preds = self.model.readtext(image=image,
                                    text_threshold=self.text_threshold,
                                    paragraph=self.paragraph,
                                    detail=self.detail,
                                    decoder=self.decoder)

        return preds

    def _midpoint(self, x1, y1, x2, y2):
        x_mid = int((x1 + x2) / 2)
        y_mid = int((y1 + y2) / 2)
        return (x_mid, y_mid)

    def _inpaint_text(self, img, result):
        mask = np.zeros(img.shape[:2], dtype="uint8")

        max_sq = 0
        for bbox in result:
            coords = bbox[0]
            curr_sq = (coords[1][0] - coords[0][0]) * (coords[2][1] - coords[1][1])
            if max_sq < curr_sq:
                max_sq = curr_sq
                max_preds = bbox
                width = coords[1][0] - coords[0][0]
                height = coords[2][1] - coords[1][1]

            x0, y0 = coords[3]
            x1, y1 = coords[1]
            x2, y2 = coords[2]
            x3, y3 = coords[0]

            x_mid0, y_mid0 = self._midpoint(x1, y1, x2, y2)
            x_mid1, y_mi1 = self._midpoint(x0, y0, x3, y3)

            thickness = int(math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2))

            cv2.line(
                mask, (x_mid0, y_mid0), (x_mid1, y_mi1), 255, thickness
            )

            numpy_image = cv2.inpaint(img, mask, 7, cv2.INPAINT_NS)

        x = max_preds[0][0][0]
        y = max_preds[0][0][-1]
        self.signage_name_photo = cv2.resize(
            self.signage_name_photo, (width, height)
        )

        if x + self.signage_name_photo.shape[1] > numpy_image.shape[1]:
            x = numpy_image.shape[1] - self.signage_name_photo.shape[1]

        if y + self.signage_name_photo.shape[0] > numpy_image.shape[0]:
            y = numpy_image.shape[0] - self.signage_name_photo.shape[0]

        numpy_image[y:y + self.signage_name_photo.shape[0], x:x + self.signage_name_photo.shape[1]] = self.signage_name_photo


        return numpy_image

    def __call__(self, image, signage_name) -> str:
        """
        Извлечение текстов из изображения

        Arguments:
            path_to_image (str): Путь до изображения

        Returns:
            str: Извлеченный текст из изображения
        """

        self.signage_name_photo =  cv2.imread(signage_name)
        self.preds = self._infer(image)

        if len(self.preds) > 0:
            img = self._inpaint_text(image, self.preds)
            _, img = cv2.imencode('.jpg', img)
            image_output = io.BytesIO(img)
            image_output.name = f'{uuid.uuid4()}.jpg'
            image_output.seek(0)
            return image_output, self.preds  # М.б. Нужен текст, он лежит в preds
        else:
            return None, None

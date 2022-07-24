import base64
import binascii
import logging
import os

import cv2
import numpy as np

from face_similarity.utils.response_error import raise_error


class ApiUtil:
    """
    Class that makes available the methods that are used in the api.
    """

    @staticmethod
    def to_numpy(encoded) -> np.ndarray:
        """Convert base64 to numpy.
        Args:
            encoded (str): Base64 encoded string to decode.
        Returns:
            'np.ndarray: An ndimentional array of the input image.
        """
        np_res = None
        np_array = np.frombuffer(base64.b64decode(encoded), np.uint8)
        try:
            np_res = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        except cv2.error:
            raise_error(401)
        return np_res

    @staticmethod
    def is_base64(str_b64):
        """Check if str represents base64 format.
        Args:
            str_b64 (str): String containing base64 code.
        Returns:
            bool: True if input is base64 encoded, raise ValueError otherwise.
        """
        try:
            base64.b64decode(str_b64)
        except binascii.Error:
            raise_error(401)

    def is_valid_request(self, request) -> tuple:
        """Check if the request has the valid parameters and values.
        Args:
            request (Request): Object of the request.
        Returns:
            vector: (np.ndarray) an n dimensional array of the 64 image.
        """
        if not request.is_json:
            raise_error(400)
        result = request.get_json()
        # The request contains the correct parameters?
        if not all(key in result for key in ['img1', 'img2']):
            raise_error(404)
        # str represents base64?
        self.is_base64(result['img1'])
        self.is_base64(result['img2'])

        return result["img1"], result['img2']

    @staticmethod
    def environ_value(environ):
        """
        Get values from operating system environment.
        Args:
            environ: (str) Environment variable name.
        Returns:
            (str) Value of the environment variable.
        """
        try:
            return os.environ[environ]
        except KeyError:
            logging.getLogger('face_similarity.api').info(
                environ + ' > not found')
            raise_error(428)

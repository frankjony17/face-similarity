
import json
import logging
import time

from face_similarity.utils.api_util import ApiUtil
from face_similarity.service.requisitions_service import \
    RequisitionsService
from face_similarity.service.face_distance_service import \
    FaceDistanceService
from face_similarity.utils.response_error import raise_error


class FaceSimilarityService:
    """
    Class that makes available all the methods to make the integrations with
    the 'api-preprocess, api-face-detect, api-face-encoding' to obtain the
    vector of 128 dimensions from an image encoded in base 64.
    """
    face_endpoints = None  # Face Detect API (image/face-detect)
    rotate_endpoints = None  # Preprocess API (image/rotate-by-angle)
    encoding_endpoints = None  # Face Encoding API (image/face-encoding)

    def __init__(self):
        """
        Class Constructor.
        """
        self.utils = ApiUtil()
        self.face_distance_service = FaceDistanceService()

    def start_vector_comparison_task(self, base64_1, base64_2, loop):
        """
        Performs the necessary tasks to obtain the score of the distance
        between the vectors of two faces.
        Args:
            base64_1: (str) Containing base64 code from image 1.
            base64_2: (str) Containing base64 code from image 2.
            loop: (event_loop) Event loop in the current OS thread.
        Returns:
            (float) Percent of trust score.
        """
        self.reset()
        start_time = time.time()
        # Get faces from base64 images (base64_1, base64_2).
        face_detect_response = self.get_both_faces(base64_1, base64_2, loop)
        # Get vector for each face.
        vector_1, vector_2 = self.get_both_vectors(
            face_detect_response, base64_1, base64_2, loop)
        # Close loop.
        loop.close()
        # Get distance between vectors.
        distance = self.face_distance_service.face_distance(vector_1, vector_2)
        # Get confidence score as a percentage.
        confidence_score = \
            self.face_distance_service.convert_distance_to_percentage(distance)
        # Set logger for confidence_score.
        logging.getLogger('face_similarity.info').info({
            "similarity": confidence_score,
            "time": "%s seconds" % (time.time() - start_time)
        })
        return confidence_score

    def get_both_vectors(self, face_detect_, base64_1, base64_2, loop) -> ():
        """
        Obtain 128-dimensional vector through integration with
        api-face-encoding.
        Args:
            face_detect_: (list) List of response from api-face-detect.
                                    contains base64 bounding_box (base64_1,
                                    base64_2)
            base64_1: (str) Containing base64 code from image 1.
            base64_2: (str) Containing base64 code from image 2.
            loop: (event_loop) Event loop in the current OS thread.
        Returns:
            (tuple) 128 dimension vectors for each face.
        """
        bounding_box_1, bounding_box_2 = self.get_bounding_box(face_detect_)
        # Payload and url for 'Face Encoding API'.
        self.face_encoding_url_payload(
            base64_1, base64_2, bounding_box_1, bounding_box_2)
        # Star loop of requisitions.
        requisitions_service = RequisitionsService()
        encoding_response = requisitions_service.start_loop(
            loop, self.encoding_endpoints)
        # Get vector 1 ans 2.
        vector_1 = json.loads(encoding_response[0][1]["faces_encoding"])[0]
        vector_2 = json.loads(encoding_response[1][1]["faces_encoding"])[0]
        # Return vectors.
        return vector_1, vector_2

    def get_both_faces(self, base64_1, base64_2, loop):
        """
        Get face from an image in base64 code (base64_1, base64_2).
        Integration done with the api-face-detect.
        Args:
            base64_1: (str) Containing base64 code from image 1.
            base64_2: (str) Containing base64 code from image 2.
            loop: (event_loop) Event loop in the current OS thread.
        Returns:
            (list) list of response from api-face-detect.
        """
        requisitions_service = RequisitionsService()
        # Payload and url for 'Preprocess API'.
        self.pre_process_url_payload(base64_1, base64_2)
        # Rotate image at various angles (90, 180, 270).
        pre_pro_response = requisitions_service.start_loop(
            loop, self.rotate_endpoints)
        # Faces from rotated base 64 image.
        face_detect_response = self.get_faces_from_b64(
            base64_1, base64_2, pre_pro_response, loop)
        return face_detect_response

    def get_faces_from_b64(self, base64_1, base64_2, pre_process_resp, loop):
        """
        Get face from an image in base64 code, rotated at angles
        [0, 90. 180, 270]. Integration done with the api-face-detect.
        Args:
            base64_1: (str) Containing base64 code from image 1.
            base64_2: (str) Containing base64 code from image 2.
            pre_process_resp: (list) List of responses to requests made
                                     to the api-preprocess.
            loop: (event_loop) Event loop in the current OS thread.
        Returns:
            (list) Responses to requests made to the api-face-detect
                   (8 request).
        """
        requisitions_service = RequisitionsService()
        # Payload and url for 'Face Detection API'.
        pre_process_resp.append([200, {"b64_image": base64_1}, "img_1"])
        pre_process_resp.append([200, {"b64_image": base64_2}, "img_2"])
        self.face_detect_url_payload(pre_process_resp)
        # Rotate image at various angles (90, 180, 270)
        face_detect_response = requisitions_service.start_loop(
            loop, self.face_endpoints)
        return face_detect_response

    def face_detect_url_payload(self, pre_process_resp) -> None:
        """
        Process and get the url and the payload for each request to
        api-face-detect.
        Args:
            pre_process_resp: (list) Responses to requests made to
                                     api-face-detect (8 request).
        """
        self.face_endpoints = list()
        url, _ = self.get_face_detect_url_payload()
        # Append url and payload.
        for response in pre_process_resp:
            self.face_endpoints.append([
                url,
                {"image": response[1]["b64_image"], "cropped": False},
                response[2]
            ])

    def pre_process_url_payload(self, base64_1, base64_2) -> None:
        """
        Process and get the url and the payload for the request for each
        base64.
        Args:
            base64_1: (str) Containing base64 code from image 1.
            base64_2: (str) Containing base64 code from image 2.

        Returns:

        """
        url = self.utils.environ_value('PRE_PROCESS_URL')
        for angle in [90, 180, 270]:
            payload_base_1 = {"image": base64_1, "angle": angle}
            payload_base_2 = {"image": base64_2, "angle": angle}
            self.rotate_endpoints.append([url, payload_base_1, "img_1"])
            self.rotate_endpoints.append([url, payload_base_2, "img_2"])

    def get_face_detect_url_payload(self) -> tuple:
        """
        Get url and payload base for api-face-detect.
        Returns:
            (tuple) Url and payload.
        """
        payload_base = {"image": "", "cropped": False}
        url = self.utils.environ_value('FACE_DETECT_URL')
        return url, payload_base

    def face_encoding_url_payload(self, base64_1, base64_2, bounding_box_1,
                                  bounding_box_2):
        """
        Get url and payload base for each base64 image (base64_1, base64_2).
        Url for integration with api-face-encoding.
        Args:
            base64_1: (str) Containing base64 code from image 1.
            base64_2: (str) Containing base64 code from image 2.
            bounding_box_1: (list) Location of face from image 1.
            bounding_box_2: (list) Location of face from image 2.
        """
        url = self.utils.environ_value('FACE_ENCODING_URL')
        self.encoding_endpoints.append([url, {
            "b64_image": base64_1, "face_locations": bounding_box_1}, "img_1"])
        self.encoding_endpoints.append([url, {
            "b64_image": base64_2, "face_locations": bounding_box_2}, "img_2"])

    @staticmethod
    def get_bounding_box(face_detect_img) -> tuple:
        """
        Get bounding box from the requisition response to the api-face-detect.
        Args:
            face_detect_img: (list) Responses from api-face-detect. Location
                                    of faces (bounding box)
        Returns:
            (tuple) Bounding box from face of image 1 and face of image 1.
        """
        bounding_box_1, bounding_box_2, boxes, i = None, None, list(), 0
        # Image does not contain faces.
        if len(face_detect_img) == 0:
            raise_error(406)
        # Get bounding box for each image.
        for item in face_detect_img:
            if item[1]["number_of_faces"] > 0:
                boxes.append([item[1]["data"][0]["bounding_box"], item[2]])
                i = i + 1
            if i == 2:
                break
        # Each image contains a face.
        if (boxes[0][1] == "img_1" and boxes[1][1] == "img_2") or (
                boxes[0][1] == "img_2" and boxes[1][1] == "img_1"):
            bounding_box_1 = boxes[0][0]
            bounding_box_2 = boxes[1][0]
        else:
            raise_error(403)
        return bounding_box_1, bounding_box_2

    def reset(self):
        """
        Clean the variables.
        """
        self.face_endpoints = list()
        self.rotate_endpoints = list()
        self.encoding_endpoints = list()

    def __del__(self):
        """"
        Class destroyer.
        """
        self.reset()

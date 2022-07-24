
import numpy as np
import math


class FaceDistanceService:
    """
    Class that contains the methods to calculate the distance between
    the vectors resulting from two images.
    """

    @staticmethod
    def convert_distance_to_percentage(face_distances, threshold=0.6):
        """Calculates faces distance accuracy as a percentage.
        Args:
            face_distances: (float) Face distance.
            threshold: (float) Minimum distance error acceptable.
        Returns:
            (float) Percent of trust score.
        """
        if face_distances > threshold:
            threshold = (1.0 - threshold)
            # Linear value.
            lin_val = (1.0 - face_distances) / (threshold * 2.0)
        else:
            lin_val = 1.0 - (face_distances / (threshold * 2.0))
            result = ((1.0 - lin_val) * math.pow((lin_val - 0.5) * 2, 0.2))
            lin_val = lin_val + result
        return round(float(lin_val * 100), 2)

    @staticmethod
    def face_distance(vector_1, vector_2):
        """Calculate norm from faces encodings.
        Args:
            vector_1: (list) Faces encodings.
            vector_2: (list) Faces encodings.
        Returns:
            (float) Norm of the matrix.
        """
        vector_1 = np.array([vector_1])
        vector_2 = np.array([vector_2])
        # Return norm distance.
        return np.linalg.norm(vector_1 - vector_2, axis=1)

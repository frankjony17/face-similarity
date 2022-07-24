
import asyncio

from flask import Blueprint, jsonify, request

from face_similarity.service.face_similarity_service import \
    FaceSimilarityService

face_distance = Blueprint('face_distance', __name__)


@face_distance.route('/image/face-distance', methods=['POST'])
def face_distance_post():
    """Fase Similarity endpoint handler.
    Args:
        img1 (str): Base64 encoded image.
        img2 (str): Base64 encoded image.
    Returns:
        dict: The distance score.
    """
    similarity_service = FaceSimilarityService()
    base64_1, base64_2 = similarity_service.utils.is_valid_request(request)
    # Start loops.
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # Start similarity service and get trust score.
    confidence_score = similarity_service.start_vector_comparison_task(
        base64_1, base64_2, loop)
    # Return response.
    return jsonify({'similarity': confidence_score}), 200

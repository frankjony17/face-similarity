
from flask import Blueprint, abort, jsonify

error_handler = Blueprint('error_handler', __name__)


error_dict = {
    400: {'detail': 'Bad Request, wrong syntax, '
                    'the request could not be understood by the server.'},
    401: {'detail': 'Bad Request, wrong base64 format.'},
    403: {'detail': 'Bad Request, face not found, a face was not found in the '
                    'image'},
    404: {'detail': 'Bad Request, required parameters missing, parameters '
                    'wasn\'t found.'},
    405: {'detail': 'Server not Found, '
                    'Error connecting to remote APIs, failure connection.'},
    406: {'detail': 'Bad Request, base 64 image does not contain face.'},
    417: None,
    424: {'detail': 'External API error, 500 error in remote API, '
                    'check the logs to find the error: '
                    '[api-preprocess, api-face-detect, api-face-encoding, '
                    'ibi-comparacao-facial]'},
    428: {'detail': 'Pending configuration, '
                    'environment variable not configured [PRE_PROCESS_URL,'
                    ' FACE_DETECT_URL, FACE_ENCODING_URL, SCHEMES,'
                    ' IBI_FERRAMENTA, IBI_VERSAO_FERRAMENTA,'
                    ' IBI_QUANTIDADE_IDENTIFICADORES, IBI_TIMEOUT]'},
}


def raise_error(code, msg=None, api=None):
    """
    Abort error if the code status is greater than 200.
    Args:
        code: (int) Response status code.
        msg: (str) Message to be returned.
        api: (str) Endpoint, url or link of the required api.
    """
    if code > 200:
        if msg is not None:
            error_dict[code] = {"EXTERNAL_API_RESPONSE": msg, "url": api}
        abort(code)


def response(code):
    """Return response message according to request type of error.
    Args:
        code (int): Code of error.
    Returns:
        dict or None: Message and reason from request type of error.
    """
    return error_dict.get(code, None)


@error_handler.app_errorhandler(400)
def wrong_syntax(error):
    return jsonify(response(400)), 400


@error_handler.app_errorhandler(401)
def wrong_base64(error):
    return jsonify(response(401)), 400


@error_handler.app_errorhandler(403)
def face_not_found(error):
    return jsonify(response(403)), 400


@error_handler.app_errorhandler(404)
def required_parameters_missing(error):
    return jsonify(response(404)), 400


@error_handler.app_errorhandler(405)
def error_connecting_to_remote_api(error):
    return jsonify(response(405)), 400


@error_handler.app_errorhandler(406)
def more_than_one_face(error):
    return jsonify(response(406)), 400


@error_handler.app_errorhandler(424)
def external_api_error_500(error):
    return jsonify(response(424)), 424


@error_handler.app_errorhandler(428)
def not_configured(error):
    return jsonify(response(428)), 428


@error_handler.app_errorhandler(417)
def external_api_response_not_200(error):
    return jsonify(response(417)), 417

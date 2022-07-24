import logging
import os

from face_similarity import create_app
from face_similarity.utils.middleware_controller import \
    setup_metrics

app = create_app()
setup_metrics(app)


def start_server():
    port = int(os.environ.get('PORT', 9000))
    logging.getLogger('face_similarity.main').info(
        f'Face Similarity starting in port {port}.')
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('MODE') != 'prod',
            use_reloader=os.environ.get('MODE') != 'prod')


if __name__ == '__main__':
    start_server()

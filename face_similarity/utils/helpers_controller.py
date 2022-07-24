from flask import Blueprint, Response
from prometheus_client import (CONTENT_TYPE_LATEST, CollectorRegistry,
                               generate_latest, multiprocess)

helpers = Blueprint('helpers', __name__)


@helpers.route('/metrics')
def metrics():
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
    data = generate_latest(registry)
    return Response(data, mimetype=CONTENT_TYPE_LATEST)

import logging
import time

from flask import g, request
from prometheus_client import Counter, Gauge, Histogram


def setup_metrics(app):
    def before_request():
        if 'metric' not in request.path:
            g.start_time = time.time()
            http_concurrent_request_count.inc()
            content_length = request.content_length
            if content_length:
                http_request_size_bytes.labels(
                    request.method,
                    request.path).observe(content_length)

    def after_request(response):
        if 'metric' not in request.path:
            request_latency = time.time() - g.start_time
            logging.getLogger('face_similarity.middleware').debug(
                f'request_latency: {request_latency}')
            http_request_latency_ms.labels(
                request.method, request.path,
                response.status_code).observe(request_latency)

            http_concurrent_request_count.dec()

            http_request_count.labels(
                request.method, request.path,
                response.status_code).inc()

            resp_length = response.calculate_content_length()
            http_response_size_bytes.labels(
                request.method, request.path, response.status_code).observe(
                    0 if resp_length is None else resp_length)

        return response

    http_request_latency_ms = Histogram(
        'http_request_latency_ms', 'HTTP Request Latency',
        ['method', 'endpoint', 'http_status'],
        buckets=(1, 3, 10, 50, 100, 200, 500, float('inf')))

    http_request_size_bytes = Histogram(
        'http_request_size_bytes', 'HTTP request size in bytes',
        ['method', 'endpoint'])

    http_response_size_bytes = Histogram(
        'http_response_size_bytes', 'HTTP response size in bytes',
        ['method', 'endpoint', 'http_status'])

    http_request_count = Counter(
        'http_request_count', 'HTTP Request Count',
        ['method', 'endpoint', 'http_status'])

    http_concurrent_request_count = Gauge(
        'http_concurrent_request_count',
        'Flask Concurrent Request Count',
        multiprocess_mode='livesum')

    app.before_request(before_request)
    app.after_request(after_request)

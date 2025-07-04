from prometheus_client import start_http_server, Counter, Summary
import threading

# Metrics
ISSUES_CREATED = Counter("issues_created_total", "Total number of issues created")
REQUEST_TIME = Summary("request_processing_seconds", "Time spent processing request")


def start_metrics_server():
    # Run Prometheus metrics server on port 8001
    thread = threading.Thread(target=start_http_server, args=(8001,))
    thread.daemon = True
    thread.start()

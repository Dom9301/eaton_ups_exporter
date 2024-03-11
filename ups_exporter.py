import http.server
import socketserver
import time
import subprocess
import logging
from logging.handlers import RotatingFileHandler

# Configuration
HTTP_SERVER_PORT = 8111
UPDATE_INTERVAL = 15
UPS_NAME = "Eaton5E"
LOG_FILE = '/root/ups_metrics.log'
MAX_BYTES = 10000000  # 10 MB

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=MAX_BYTES, backupCount=5)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

# Metrics exporter in Prometheus format
def export_metric(metric_name, value, help_text=None, metric_type=None):
    metric = ""
    if help_text:
        metric += f"# HELP {help_text}\n"
    if metric_type:
        metric += f"# TYPE {metric_name} {metric_type}\n"
    metric += f"{metric_name} {value}\n"
    return metric

# Export all metrics from UPS
def export_all_metrics():
    # Run a single request to UPS to get all the metrics you need
    try:
        output = subprocess.check_output(["upsc", UPS_NAME]).decode().strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Error while retrieving metrics for UPS: '{UPS_NAME}': {e}")
        return ""

    # Analyze the output and create corresponding metrics
    metrics = ""
    for line in output.split('\n'):
        key, value = line.split(': ')
        metrics += export_metric(f"ups_{key.lower()}", value, f"{key} of the UPS", "gauge")
    return metrics

# Function to handle HTTP requests
class UPSMetricsHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(export_all_metrics().encode())

# Main function
def main():
    # Configure the HTTP server
    with socketserver.TCPServer(("", HTTP_SERVER_PORT), UPSMetricsHandler) as httpd:
        logger.info(f"Server started on {HTTP_SERVER_PORT}, using UPS '{UPS_NAME}'")
        try:
            # Starts the server and handles requests in a continuous loop
            httpd.serve_forever()
        except KeyboardInterrupt:
            logger.info("HTTP server shutdown")

if __name__ == "__main__":
    main()

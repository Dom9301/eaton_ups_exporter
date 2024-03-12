import http.server
import socketserver
import time
import subprocess
import logging
from logging.handlers import RotatingFileHandler
import datetime

# Logging settings
log_filename = '/path/to/ups_exporter.log'
log_max_size = 1024 * 1024 * 10  # 10 MB

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# RotatingFileHandler to handle log rotation
file_handler = RotatingFileHandler(log_filename, maxBytes=log_max_size, backupCount=5)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# Add log handler
logging.getLogger().addHandler(file_handler)

# Port on which the HTTP server will listen
PORT = 8111
# Metrics update interval in seconds
UPDATE_INTERVAL = 15

# Function to export a metric to Prometheus format
def export_metric(metric_name, value, help_text=None, metric_type=None):
    metric = ""
    if help_text:
        metric += f"# HELP {help_text}\n"
    if metric_type:
        metric += f"# TYPE {metric_name} {metric_type}\n"
    metric += f"{metric_name} {value}\n"
    return metric

# Export all metrics
def export_all_metrics():
    metrics = ""
    metrics += export_battery_status()
    metrics += export_output_voltage()
    metrics += export_load()
    metrics += export_ups_status()
    metrics += export_battery_duration()
    metrics += export_delay_start()
    metrics += export_delay_shutdown()
    return metrics

# Export Delay start
def export_delay_start():
    delay_start = subprocess.check_output(["upsc", "Eaton5E", "ups.delay.start"]).decode().strip()
    return export_metric("ups_delay_start", delay_start, "Battery delay start", "gauge")

# Export Delay shutdown
def export_delay_shutdown():
    delay_shutdown = subprocess.check_output(["upsc", "Eaton5E", "ups.delay.shutdown"]).decode().strip()
    return export_metric("ups_delay_shutdown", delay_shutdown, "Battery delay shutdown", "gauge")

# Export estimated battery life
def export_battery_duration():
    battery_duration = subprocess.check_output(["upsc", "Eaton5E", "battery.runtime"]).decode().strip()
    return export_metric("ups_battery_duration", battery_duration, "Battery estimated duration", "gauge")

# Export battery status
def export_battery_status():
    battery_status = subprocess.check_output(["upsc", "Eaton5E", "battery.charge"]).decode().strip()
    return export_metric("ups_battery_charge_percent", battery_status, "Battery charge level percentage", "gauge")

# Export the output voltage
def export_output_voltage():
    output_voltage = subprocess.check_output(["upsc", "Eaton5E", "output.voltage"]).decode().strip()
    return export_metric("ups_output_voltage_volts", output_voltage, "Output voltage of the UPS", "gauge")

# Export the load of the UPS
def export_load():
    load = subprocess.check_output(["upsc", "Eaton5E", "ups.load"]).decode().strip()
    return export_metric("ups_load_percent", load, "Load percentage of the UPS", "gauge")

# Exports the status of the UPS (current or battery)
def export_ups_status():
    ups_status = subprocess.check_output(["upsc", "Eaton5E", "ups.status"]).decode().strip()
    if ups_status == "OL":
        return export_metric("ups_power_status", "1", "Power status of the UPS (1 for on utility power, 0 for on battery)", "gauge")
    else:
        return export_metric("ups_power_status", "0", "Power status of the UPS (1 for on utility power, 0 for on battery)", "gauge")

# Function to handle HTTP requests
class UPSMetricsHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(export_all_metrics().encode())

# Main function
def main():
    try:
        # Log of the start of script execution
        logging.info('Start script execution.')
        # Configura il server HTTP
        with socketserver.TCPServer(("", PORT), UPSMetricsHandler) as httpd:
            print(f"Server started on the port {PORT}")
            try:
                # Starts the server and handles requests in a continuous loop
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("HTTP server shutdown")
    except Exception as e:
        # Error log
        logging.error(f'Error during script execution: {e}')

if __name__ == "__main__":
    main()

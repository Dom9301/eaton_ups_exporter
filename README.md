### I am in no way affiliated with Eaton and this is in no way an official exporter

# Ellipse ECO 800 UPS Exporter

This project implements an HTTP server that exports metrics from the Ellipse ECO 800 UPS (https://www.eaton.com/ch/en-gb/skuPage.EL800USBDIN.html) compatible with the Prometheus protocol. The metrics include information such as battery status, output voltage, load, UPS status, and more.

The HTTP server responds to GET requests by returning metrics in the Prometheus-compatible plaintext format.

## Dependencies

Make sure you have the following requirements installed before running the code:

    Python 3.x
    Python's http.server module
    Python's socketserver module

## Configuration

To configure the server and logging, change the following variables in the code:

    log_filename: Path to the log file.
    log_max_size: Maximum size of the log file before rotation.
    PORT: Port on which the HTTP server listens for requests.
    UPDATE_INTERVAL: Update interval of the metrics in seconds.

## Use

Make sure you have all dependencies installed.
Run the Python script ups_exporter.py.
The HTTP server starts listening on the specified port.
Use a browser or HTTP client to access the exposed metrics. For example, if the server is running on localhost on port 8111, you can access the metrics by visiting http://localhost:8111.

## Log

The code also implements event logging via the logging module. The logs are written to a file specified by the variables log_filename and log_max_size. If an error occurs during execution, the details are recorded in the log file.

### Nota sull'UPS

The code is configured to query a specific Ellipse ECO 800 UPS, in the code named Eaton5E. It should be compatible with at least the entire Eaton Ellipse ECO range, but make sure that your UPS is actually compatible and that the upsc commands work properly with your UPS before running the code.


import configparser
import os
import gradio as gr
import requests
import urllib3
from requests.auth import HTTPBasicAuth
from datetime import datetime, timezone, timedelta
import threading
import pyttsx3  # For text-to-speech

# Disable SSL certificate verification (not recommended for production)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Construct the absolute path to the config.ini file
config_path = os.path.join(os.path.dirname(__file__), 'config.ini')

# Initialize ConfigParser to read config.ini
config = configparser.ConfigParser()
config.read(config_path)

if 'Settings' not in config:
    raise KeyError("The 'Settings' section is missing from config.ini")

# Load configurations from the config.ini file
tts_alert_message = config['Settings']['tts_alert_message']
wait_time_seconds = int(config['Settings']['wait_time_seconds'])
url = config['Settings']['url']
host = config['Settings']['host']
user_agent = config['Settings']['user_agent']
content_type = config['Settings']['content_type']

# HTTP headers
headers = {
    "Host": host,
    "kbn-xsrf": "true",
    "Content-Type": content_type,
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Referer": "https://portal.dimon.telecomitalia.local:20443/s/flycbe/app/hydra_react",
    "User-Agent": user_agent,
}

# Initialize the text-to-speech engine
tts_engine = pyttsx3.init()

# Function to get today's date in the required format with fixed times


def get_today_date_range():
    today = datetime.now(timezone.utc).date()  # Use timezone-aware UTC date
    gte_timestamp = f"{today}T00:00:00.000Z"  # Start of day in UTC
    lte_timestamp = f"{today}T23:59:59.005Z"  # End of day in UTC
    return gte_timestamp, lte_timestamp


def fetch_kibana_logs(username, password):
    gte_timestamp, lte_timestamp = get_today_date_range()

    data = {
        "sort": [
            {"@timestamp": {"order": "desc",
                            "format": "strict_date_optional_time", "unmapped_type": "boolean"}},
            {"_doc": {"order": "desc", "unmapped_type": "boolean"}}
        ],
        "track_total_hits": True,
        "fields": [
            {"field": "*", "include_unmapped": "true"},
            {"field": "@timestamp", "format": "strict_date_optional_time"},
            {"field": "notification.data.modifierDate",
                "format": "strict_date_optional_time"},
            {"field": "notification.transition.end",
                "format": "strict_date_optional_time"},
            {"field": "notification.transition.start",
                "format": "strict_date_optional_time"},
            {"field": "sheetData.modifierDate",
                "format": "strict_date_optional_time"}
        ],
        "size": 1,
        "version": True,
        "_source": False,
        "query": {
            "bool": {
                "must": [{"query_string": {"query": "FLY_CBE WETIM", "analyze_wildcard": True, "time_zone": "Europe/Berlin"}}],
                "filter": [{
                    "range": {
                        "@timestamp": {
                            "format": "strict_date_optional_time",
                            "gte": gte_timestamp,
                            "lte": lte_timestamp
                        }
                    }
                }]
            }
        }
    }

    auth = HTTPBasicAuth(username, password)
    try:
        response = requests.post(url, headers=headers,
                                 json=data, auth=auth, verify=False)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        return f"HTTP error occurred: {http_err}"
    except requests.exceptions.RequestException as req_err:
        return f"Request error occurred: {req_err}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


def alert_sound():
    """Use pyttsx3 to alert the user when the notification status is red."""
    tts_engine.say(tts_alert_message)
    tts_engine.runAndWait()


# Modify the process_response_data function to return updated table rows
def process_response_data(response_data):
    try:
        hits = response_data.get('res', {}).get('hits', {}).get('hits', [])
        if hits:
            hit = hits[0].get('fields', {})
            color = hit.get('notification.transition.status.color', ['N/A'])[0]
            statement = hit.get('notification.data.statement', ['N/A'])[0]
            status = hit.get(
                'notification.transition.status.custom', ['N/A'])[0]
            name = hit.get('notification.data.name', ['Unnamed'])[0]
            timestamp_str = hit.get('@timestamp', ['N/A'])[0]

            log_timestamp = datetime.strptime(
                timestamp_str, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
            current_time = datetime.now(timezone.utc)

            if current_time - timedelta(seconds=wait_time_seconds) <= log_timestamp <= current_time:
                if color.lower() == 'red':
                    alert_sound()  # Trigger the text-to-speech alert
                    # Add row to the table when color is red
                    new_row = [name, color, statement, status]
                    return f"ALERT! Notification status color is RED for {name} at {timestamp_str}.", new_row
                else:
                    return f"Notification status color: {color}", None
            else:
                return f"Log entry is older than {wait_time_seconds/60} minute(s), skipping alert. Timestamp: {timestamp_str}", None
        else:
            return "No data found in the response.", None
    except Exception as e:  # Catch any exceptions and return the error message
        return f"Error processing response data: {str(e)}", None


# Control flag for stopping the monitoring thread
stop_monitoring = False

# Function to stop the Gradio server using threading


def stop_gradio_server():
    demo.close()

# Function to stop monitoring and trigger the server shutdown


def stop_monitoring_fn():
    global stop_monitoring

    if not stop_monitoring:  # Already stopped, notify the user
        return "Monitoring is not started yet, stopping is not possible.", gr.update(visible=True), gr.update(visible=True)
    else:
        stop_monitoring = True
        stop_gradio_server()  # Call the function to stop the server
        return "Monitoring stopped. Server will shut down.", gr.update(visible=True), gr.update(visible=True)

# Function to start monitoring
def start_monitoring(username, password):
    global stop_monitoring
    if not username or not password:  # Validate if username or password is empty
        return "Please provide both username and password to start monitoring.", gr.update(visible=True), gr.update(visible=True), gr.update(value=[])

    if not stop_monitoring:  # Ensure monitoring isn't already started
        stop_monitoring = True
        threading.Thread(target=monitor_logs_thread, args=(
            username, password), daemon=True).start()
        return f"Monitoring started for {username}.", gr.update(visible=True), gr.update(visible=True), gr.update(value=[])
    else:
        return "Monitoring is already started.", gr.update(visible=True), gr.update(visible=True), gr.update(value=[])


# Monitoring thread modified to append rows to the table
def monitor_logs_thread(username, password):
    global stop_monitoring
    table_rows = []
    while not stop_monitoring:
        response_data = fetch_kibana_logs(username, password)
        if isinstance(response_data, dict):
            result, new_row = process_response_data(response_data)
            print(result)
            if new_row:
                table_rows.append(new_row)
                table.update(value=table_rows)  # Update table with new rows
        else:
            print(response_data)
        threading.Event().wait(wait_time_seconds)


# Gradio Interface
with gr.Blocks(title="Hydra Monitoring App") as demo:
    gr.Markdown("# Welcome to Hydra Alarm Monitoring")
    gr.Markdown("### This app will automatically detect hydra alarms and notify user when an alarm is <span style='color:red;'><strong>RED</strong></span>.")
    gr.Markdown(
        "#### <span style='color:red;'>{ Note: Use <strong>DiMon username</strong> and password }</span>")

    with gr.Row():
        username_input = gr.Textbox(
            label="Username", placeholder="Enter your username")
        password_input = gr.Textbox(
            label="Password", placeholder="Enter your password", type="password")

    with gr.Row():
        start_button = gr.Button("Start Monitoring")
        stop_button = gr.Button("Stop Monitoring")

    output = gr.Textbox(label="Output")

    with gr.Row():
        table = gr.Dataframe(
            headers=["notification.data.name", "notification.transition.status.color", "notification.data.statement", "notification.transition.status.custom"],
            row_count=1
        )

    start_button.click(
        start_monitoring,
        inputs=[username_input, password_input],
        outputs=[output, start_button, stop_button, table]
    )

    stop_button.click(
        stop_monitoring_fn,
        inputs=[],
        outputs=[output, start_button, stop_button]
    )

demo.launch(share=True)

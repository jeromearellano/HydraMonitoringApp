# Hydra Monitoring Web App

This Python application monitors **Hydra alarms** and automatically notifies the user when an alarm status changes to **RED** using a web interface built with **Gradio**. The app can also provide voice alerts when a critical alarm is detected.

## Features

- Monitors specific **Hydra alarms** by querying **Kibana** logs.
- Provides **real-time** status updates on a web interface.
- Alerts the user with **text-to-speech** when an alarm status turns **RED**.
- Option to stop and start the monitoring process.
- Displays log details in a table format for quick insights.

## Installation

To install and run the app, follow these steps:

Follow these steps to set up the project on your local machine:

1. **Create a Project Folder**:
   Open your command prompt and navigate to your Desktop. Create a folder named `PyApp`.
   ```bash
      cd C:\Users\eid\Desktop
      mkdir PyApp
      cd PyApp
   ```

2. **Clone the Repository**:
   Clone the Hydra Monitoring App repository from GitHub.
   ```bash
   git clone https://github.com/jeromearellano/HydraMonitoringApp.git
   ```
3. **Navigate to the Project Directory**:
   Change to the project directory.
   ```bash
   cd HydraMonitoringApp
   ```
4. **Check Python Version**:
   Ensure you have Python installed. You can check your Python version with:
   ```bash
   python --version
   ```
5. **Create a Virtual Environment**:
   Create a virtual environment to manage dependencies.
   ```bash
   cd ..
   python -m venv env312
   ```
6. **Activate the Virtual Environment**:
   Navigate to the `Scripts` directory and activate the virtual environment.
   ```bash
   cd env312\Scripts
   activate
   ```
   Note: If using `cmd`, the command is just `activate`. For PowerShell, use `.\Activate.ps1`.

7. **Install Dependencies**:
   Now, navigate back to the `HydraMonitoringApp` directory and install the necessary dependencies.
   ```bash
   cd ..\..
   cd HydraMonitoringApp
   pip install .
   ```
## Configuration

You can configure the following parameters in the `config.ini` file:

```bash
[Settings] 
wait_time_seconds = 60
tts_alert_message = "Any alert message you like!" 
url = url_of_your_dimon
host = dimon_host 
user_agent = Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0 
content_type = application/json; charset=utf-8
```


### Explanation of Configurations:

- **`wait_time_seconds`**: Time interval (in seconds) between each monitoring check.
- **`tts_alert_message`**: Message to be spoken when a red alert is detected.
- **`url`**: The URL used to fetch logs from Kibana.
- **`host`**: The host for the Kibana API.
- **`user_agent`**: The user-agent string to be used in the requests.
- **`content_type`**: The content type for the API request.

## Usage

1. Open the app by running `python HydraMonitoringWebApp.py`. The Gradio web interface will launch in your browser.
2. Enter your **DiMon username** and **password** to start monitoring.
3. The app will fetch and display the latest log entries from **Kibana**.
4. If a **RED** status is detected, you will receive an audio alert.
5. You can stop the monitoring at any time by clicking the **Stop Monitoring** button.

## Dependencies

This project requires the following Python libraries:

- **Gradio**: For the web interface.
- **Requests**: For making HTTP requests to Kibana API.
- **Urllib3**: To handle SSL certificate warnings.
- **Pyttsx3**: For text-to-speech functionality.

Install all dependencies using the provided `requirements.txt` file.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contribution

Feel free to contribute by submitting pull requests. Any suggestions for improving the project are welcome!

---

### Notes

- Ensure that the Kibana URL and credentials are correctly set up in the `config.ini` file.
- This project disables SSL certificate verification for development purposes. For production, it is recommended to enable SSL verification.

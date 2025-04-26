import json
import os
from datetime import datetime

dir_name = "output"


def addToLogs(log):
    with open("logs.txt", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {log}\n")


def log_json(data: dict, directory: str = dir_name):
    os.makedirs(directory, exist_ok=True)

    file_count = len(
        [
            f
            for f in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, f)) and f.endswith(".json")
        ]
    )

    filename = os.path.join(directory, f"{file_count}.json")

    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

    print(f"Saved to {filename}")


def read_json(file_path):
    try:
        # Open the file and load its content as a dictionary
        with open(file_path, "r") as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON in file {file_path}: {e}")
        return None


def json_report(item):
    version = read_json("database_settings.json")["json_report_version"]
    FILE_PATH = f"report_{version}.json"

    if not os.path.exists(FILE_PATH):
        with open(FILE_PATH, "w") as f:
            json.dump([], f)

    with open(FILE_PATH, "r") as f:
        data = json.load(f)

    data.append(item)

    with open(FILE_PATH, "w") as f:
        json.dump(data, f, indent=4)


ERROR_LOG_FILE = "errors.json"


def load_errors():
    if os.path.exists(ERROR_LOG_FILE):
        with open(ERROR_LOG_FILE, "r") as f:
            return json.load(f)
    return []


def save_errors(errors):
    with open(ERROR_LOG_FILE, "w") as f:
        json.dump(errors, f, indent=4)


def format_error(e):
    return {"type": type(e).__name__, "message": str(e).split("\n")[0]}


def log_unique_error(e):
    error_entry = format_error(e)
    errors = load_errors()
    if error_entry not in errors:
        errors.append(error_entry)
        save_errors(errors)

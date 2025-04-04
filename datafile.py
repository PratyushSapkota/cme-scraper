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


def log_failed(idx):
    with open("failed.txt", "a") as f:
        f.write(f"{idx}\n")

import requests
from datafile import read_json, log_json
import json

data = requests.get("http://34.100.231.222:8000/report/v2")

reportData = data.json()
filtered = []

urls = read_json("urls.json")

for report in reportData["allData"]:
    if report["success"] == "false":
        filtered.append(urls[report["idx"]])

outputFile = read_json("database_settings.json")["urlFile"]
with open(outputFile, "w") as f:
    json.dump(filtered, f, indent=4)

print(f"Filtered {len(filtered)} data")

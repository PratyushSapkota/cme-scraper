from fastapi import FastAPI
from fastapi.responses import JSONResponse
import mysql.connector
import requests
from dotenv import load_dotenv
from datafile import read_json
import os

load_dotenv()

app = FastAPI()


# === RowCounter class ===
class RowCounter:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE"),
        )
        self.cursor = self.conn.cursor()

    def count_rows(self, table_name: str) -> int:
        self.cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`")
        result = self.cursor.fetchone()
        return result[0] if result else 0

    def close(self):
        self.cursor.close()
        self.conn.close()


# === FastAPI route ===
@app.get("/report")
def report():
    table_name = read_json("database_settings.json")["tableName"]
    row_counter = RowCounter()
    count = row_counter.count_rows(table_name)
    row_counter.close()

    json_report_file = read_json("database_settings.json")["json_report"]
    json_reports = read_json(json_report_file)
    failedCount = 0
    for report in json_reports:
        if report["success"] == "false":
            failedCount += 1

    data = {"db_count": count, "failed": failedCount, "allData": json_reports}
    return JSONResponse(content=data)


@app.get("/")
def default():
    return JSONResponse(content={"hello": "world"})

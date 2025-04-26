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

    def table_exists(self, table_name: str) -> bool:
        self.cursor.execute(
            """
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = %s AND table_name = %s
        """,
            (self.conn.database, table_name),
        )
        return self.cursor.fetchone()[0] == 1

    def close(self):
        self.cursor.close()
        self.conn.close()


# === FastAPI route ===
@app.get("/report/{param}")
def report(param: str):
    json_report_file = f"report_{param}.json"
    if not os.path.exists(json_report_file):
        return JSONResponse(content={"error": "report file not found"})

    table_name = param
    row_counter = RowCounter()

    if not row_counter.table_exists(table_name):
        return JSONResponse(content={"error": "table not found"})

    count = row_counter.count_rows(table_name)
    row_counter.close()

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


@app.get("/error/{param}")
def report_error(param: str):
    error_report_file = f"error_{param}.json"
    if not os.path.exists(error_report_file):
        return JSONResponse(content={"error": "report file not found"})
    table_name = param
    row_counter = RowCounter()

    if not row_counter.table_exists(table_name):
        return JSONResponse(content={"error": "table not found"})

    error_report = read_json(error_report_file)
    return JSONResponse(error_report)

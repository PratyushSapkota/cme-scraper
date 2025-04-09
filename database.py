import mysql.connector
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()


class TableRow:
    struct = {
        "product": "VARCHAR(255)",
        "url": "VARCHAR(255)",
        "volume_30": "FLOAT",
        "oi_30": "FLOAT",
        "last": "VARCHAR(255)",
        "ContractUnit": "VARCHAR(255)",
        "volume": "VARCHAR(255)",
        "oi": "VARCHAR(255)",
    }

    def __init__(self, table_name="data"):
        self.data = {col: None for col in self.struct}
        self.table_name = table_name

    def is_filled(self):
        notFilled = [key for key, value in self.data.items() if value is None]
        if not notFilled:
            return True
        print(f"Need to fill: {notFilled}")
        return False

    def clearRow(self):
        self.data = {col: None for col in self.struct}


class Database:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE"),
        )
        self.cursor = self.conn.cursor()
        print("Connected to Database")

    def create_table(self, row: TableRow):
        columns = ", ".join(f"`{col}` {typ}" for col, typ in row.struct.items())
        query = f"CREATE TABLE IF NOT EXISTS `{row.table_name}` (id INT AUTO_INCREMENT PRIMARY KEY, {columns})"
        self.cursor.execute(query)
        self.conn.commit()

    def insert_row(self, row: TableRow):
        self.create_table(row)

        if not row.is_filled():
            raise ValueError("TableRow has unfilled fields.")

        columns = ", ".join(f"`{col}`" for col in row.struct)
        placeholders = ", ".join(["%s"] * len(row.struct))
        values = tuple(row.data.values())
        query = f"INSERT INTO `{row.table_name}` ({columns}) VALUES ({placeholders})"
        self.cursor.execute(query, values)
        self.conn.commit()

    def fetch_all(self, table_name: str):
        if not table_name:
            raise ValueError("Table name must not be empty.")

        self.cursor.execute(f"SELECT * FROM `{table_name}`")
        return self.cursor.fetchall()

    def close(self):
        self.cursor.close()
        self.conn.close()

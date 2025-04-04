import sqlite3


class TableRow:
    struct = {
        "product": "TEXT",
        "url": "TEXT",
        "volume_30": "FLOAT",
        "oi_30": "FLOAT",
        "last": "TEXT",
        "ContractUnit": "TEXT",
        "volume": "TEXT",
        "oi": "TEXT",
    }

    def __init__(self, table_name="data"):
        self.data = {col: None for col in self.struct}
        self.table_name = table_name

    def is_filled(self):
        notFilled = []
        for key in self.data:
            if self.data[key] is None:
                notFilled.append(key)

        if len(notFilled) == 0:
            return True
        else:
            print(f"Need to fill: {notFilled}")
            return False


class Database:
    def __init__(self, db_file: str):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    def create_table(self, row: TableRow):
        columns = ", ".join(f"{col} {typ}" for col, typ in row.struct.items())
        query = f"CREATE TABLE IF NOT EXISTS {row.table_name} ({columns})"
        self.cursor.execute(query)
        self.conn.commit()

    def insert_row(self, row: TableRow):
        self.create_table(row)

        if not row.is_filled():
            raise ValueError("TableRow has unfilled fields.")

        columns = ", ".join(row.struct.keys())
        placeholders = ", ".join("?" for _ in row.struct)
        values = tuple(row.data.values())
        query = f"INSERT INTO {row.table_name} ({columns}) VALUES ({placeholders})"
        self.cursor.execute(query, values)
        self.conn.commit()

    def fetch_all(self, table_name: str):
        if not table_name:
            raise ValueError("Table name must not be empty.")

        self.cursor.execute(f"SELECT * FROM {table_name}")
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()

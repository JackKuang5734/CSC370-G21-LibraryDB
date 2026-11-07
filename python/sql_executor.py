import mysql.connector
from mysql.connector import Error

class SQLExecutor():

    LOCATION_ITEM_QUERY = """
SELECT
    it.item_title,
    it.item_author,
    it.item_type,
    CONCAT(SUM(CASE WHEN i.item_status = 'Available' THEN 1 ELSE 0 END), '/', COUNT(*))
FROM Item i
JOIN ItemType it
ON (i.item_type_id = it.item_type_id)
WHERE i.location_id = {location_id}
GROUP BY i.item_type_id
"""

    HOLD_QUERY = """
SELECT
    u.user_name,
    it.item_title,
    l.location_name,
    h.queue_number,
    h.hold_status,
    h.hold_created_date,
    h.hold_expiry_date
FROM Hold h
JOIN User u
ON h.user_id = u.user_id
JOIN Location l
ON h.location_id = l.location_id
JOIN ItemType it
ON h.item_type_id = it.item_type_id
"""

    LOAN_QUERY = """
SELECT
    u.user_name,
    it.item_title,
    loc.location_name,
    l.checkout_date,
    l.due_date,
    l.loan_status
FROM Loan l
JOIN User u
ON l.user_id = u.user_id
JOIN Location loc
ON l.location_id = loc.location_id
JOIN Item i
ON l.item_id = i.item_id
JOIN ItemType it
ON i.item_type_id = it.item_type_id
"""

    ITEM_QUERY = """
SELECT 
    it.item_title, 
    it.item_type, 
    l.location_name, 
    i.item_status
FROM Item i
JOIN ItemType it
ON i.item_type_Id = it.item_type_id
JOIN Location l
ON i.location_id = l.location_id
"""

    def __init__(self):
        try:
            with open("python/connection_info.txt", "r") as f:
                lines = [s.strip() for s in f.readlines()]
                host_arg, user_arg, password_arg, database_arg = lines[0], lines[1], lines[2], lines[3]
            
            self.connection = mysql.connector.connect(
                host=host_arg,
                user=user_arg,
                password=password_arg,
                database=database_arg
            )

            if self.connection.is_connected():
                self.cursor = self.connection.cursor()
            else:
                print("Could not connect")

        except Error as e:
            print(f"Error while connecting: {e}")

    def is_connected(self) -> bool:
        return self.connection.is_connected()

    def close(self):
        if 'connection' in locals() and self.connection.is_connected():
            self.connection.close()
            self.cursor.close()

    def query(self, query):
        if not self.connection.is_connected():
            return []
        
        self.cursor.execute(query)
        records = self.cursor.fetchall()
        return records

    def select(self, target, source):
        if not self.connection.is_connected():
            return []
        
        query = f"SELECT {target} FROM {source};"
        self.cursor.execute(query)
        records = self.cursor.fetchall()
        return records

    def get_users(self, show_id):
        if show_id:
            header = ("user_id", "user_name", "user_email", "user_status")
            rows = self.query("SELECT user_id, user_name, user_email, user_status FROM User")
        else:
            header = ("Username", "User Email", "User Status")
            rows = self.query("SELECT user_name, user_email, user_status FROM User")
        return SQLResult(header, rows)

    def get_holds(self, show_id):
        if show_id:
            header = ("hold_id", "item_type_id", "user_id", "location_id", "queue_number", "hold_created_date", "hold_expiry_date", "hold_status")
            rows = self.query("SELECT hold_id, item_type_id, user_id, location_id, queue_number, hold_created_date, hold_expiry_date, hold_status FROM Hold")
        else:
            header = ("User", "Title", "Location", "#", "Status", "Created", "Expires")
            rows = self.query(SQLExecutor.HOLD_QUERY)
        return SQLResult(header, rows)

    def get_loans(self, show_id):
        if show_id:
            header = ("loan_id", "item_id", "user_id", "location_id", "checkout_date", "due_date", "loan_status")
            rows = self.query("SELECT loan_id, item_id, user_id, location_id, checkout_date, due_date, loan_status FROM Loan")
        else:
            header = ("User", "Title", "Location", "Checkout Date", "Due Date", "Status")
            rows = self.query(SQLExecutor.LOAN_QUERY)
        return SQLResult(header, rows)

    def get_items(self):
        header = ("Item Title", "Type", "Location", "Status")
        rows = self.query(SQLExecutor.ITEM_QUERY)
        return SQLResult(header, rows)
    
    def get_items_from_location(self, location_id):
        header = ("Title", "Author", "Type", "Copies Available")
        rows = self.query(SQLExecutor.LOCATION_ITEM_QUERY.replace("{location_id}", str(location_id)))
        return SQLResult(header, rows)

    def get_item_types(self):
        header = ("item_title", "item_author", "item_release_date", "item_type")
        rows = self.query("SELECT item_title, item_author, item_release_date, item_type FROM ItemType")
        return SQLResult(header, rows)

    def get_locations(self, show_id):
        if show_id:
            header = ("location_id", "location_name", "address")
            rows = self.query("SELECT location_id, location_name, address FROM Location")
        else:
            header = ("Location", "Address")
            rows = self.query("SELECT location_name, address FROM Location")
        return SQLResult(header, rows)

    def get_genre(self, show_id):
        if show_id:
            header = ("genre_id", "genre_name")
            rows = self.query("SELECT genre_id, genre_name FROM Genre")
        else:
            header = ("Genre",)
            rows = self.query("SELECT genre_name FROM Genre")
        return SQLResult(header, rows)

class SQLResult():

    def __init__(self, header : tuple, rows : list[tuple]):
        self.header : tuple = header
        self.rows : list[tuple] = rows
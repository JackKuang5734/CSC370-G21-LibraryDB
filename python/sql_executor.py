import mysql.connector
from mysql.connector import Error

from data_objects import ItemType


class SQLResult():
    def __init__(self, header : tuple, rows : list[tuple], id_rows : list[tuple]|None=None):
        self.header : tuple = header
        self.rows : list[tuple] = rows
        self.links : tuple|None = ()
        self.id_rows : list[tuple]|None = id_rows
    
    def link_columns(self, links : tuple):
        self.links = links

class SQLExecutor():

    LOCATION_ITEM_QUERY = """
SELECT
    LEFT(it.item_title, 150),
    it.item_author,
    it.item_type,
    CONCAT(SUM(CASE WHEN i.item_status = 'Available' THEN 1 ELSE 0 END), '/', COUNT(*))
FROM Item i
JOIN ItemType it
ON (i.item_type_id = it.item_type_id)
WHERE i.location_id = {location_id}
GROUP BY i.item_type_id
"""

    LOCATION_ITEM_ID_QUERY = """
SELECT
    it.item_type_id,
    NULL,
    NULL,
    NULL
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

    USER_HOLD_QUERY = """
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
WHERE u.user_id = {user_id}
ORDER BY h.hold_created_date DESC
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

    MOST_LOANED_ITEMS = """
SELECT
    LEFT(it.item_title, 150),
    it.item_type,
    loc.location_name,
    COUNT(*)
FROM Item i
JOIN ItemType it
ON (i.item_type_id = it.item_type_id)
JOIN Location loc
ON (i.location_id = loc.location_id)
JOIN Loan l
ON (i.item_id = l.item_id)
GROUP BY i.item_id
HAVING COUNT(*) > 10
ORDER BY COUNT(*) DESC
"""

    LEAST_LOANED_ITEMS = """
SELECT
    LEFT(it.item_title, 150),
    it.item_type,
    loc.location_name,
    COUNT(*)
FROM Item i
JOIN ItemType it
ON (i.item_type_id = it.item_type_id)
JOIN Location loc
ON (i.location_id = loc.location_id)
JOIN Loan l
ON (i.item_id = l.item_id)
GROUP BY i.item_id
HAVING COUNT(*) <= 3
ORDER BY COUNT(*) ASC
"""

    MOST_HELD_ITEMS = """
SELECT
    LEFT(it.item_title, 150),
    it.item_type,
    COUNT(*)
FROM ItemType it
JOIN Hold h
ON (it.item_type_id = h.item_type_id)
GROUP BY it.item_type_id
HAVING COUNT(*) > 10
ORDER BY COUNT(*) DESC
"""

    LEAST_HELD_ITEMS = """
SELECT
    LEFT(it.item_title, 150),
    it.item_type,
    COUNT(*)
FROM ItemType it
JOIN Hold h
ON (it.item_type_id = h.item_type_id)
GROUP BY it.item_type_id
HAVING COUNT(*) <= 3
ORDER BY COUNT(*) ASC
"""

    POPULAR_GENRES = """
SELECT 
    g.genre_name,
    COUNT(*)
FROM Genre g
JOIN ItemGenre ig
ON (g.genre_id = ig.genre_id)
GROUP BY g.genre_id
HAVING COUNT(*) > 1
ORDER BY COUNT(*) DESC
"""


    ITEM_HOLD_HISTORY = """
SELECT
    u.user_name,
    LEFT(it.item_title, 150),
    l.location_name,
    h.hold_created_date,
    h.hold_status
FROM Hold h
JOIN ItemType it
ON (h.item_type_id = it.item_type_id)
JOIN User u 
ON (h.user_id = u.user_id)
JOIN Location l
ON (h.location_id = l.location_id)
WHERE h.item_type_id = {item_type_id}
ORDER BY h.hold_created_date DESC
"""

    ITEM_LOAN_HISTORY = """
SELECT
    u.user_name,
    LEFT(it.item_title, 150),
    loc.location_name,
    l.checkout_date,
    l.due_date,
    l.loan_status
FROM Loan l
JOIN Item i
ON (l.item_id = i.item_id)
JOIN ItemType it
ON (i.item_type_id = it.item_type_id)
JOIN User u 
ON (l.user_id = u.user_id)
JOIN Location loc
ON (l.location_id = loc.location_id)
WHERE l.item_id = {item_id}
ORDER BY l.checkout_date DESC
"""

    USER_HOLD_HISTORY = """
SELECT
    u.user_name,
    LEFT(it.item_title, 150),
    l.location_name,
    h.hold_created_date,
    h.hold_status
FROM Hold h
JOIN ItemType it
ON (h.item_type_id = it.item_type_id)
JOIN User u 
ON (h.user_id = u.user_id)
JOIN Location l
ON (h.location_id = l.location_id)
WHERE u.user_id = {user_id}
ORDER BY h.hold_created_date DESC
"""

    USER_LOAN_HISTORY = """
SELECT
    u.user_name,
    LEFT(it.item_title, 150),
    loc.location_name,
    l.checkout_date,
    l.due_date,
    l.loan_status
FROM Loan l
JOIN Item i
ON (l.item_id = i.item_id)
JOIN ItemType it
ON (i.item_type_id = it.item_type_id)
JOIN User u 
ON (l.user_id = u.user_id)
JOIN Location loc
ON (l.location_id = loc.location_id)
WHERE u.user_id = {user_id}
ORDER BY l.checkout_date DESC
"""

    def __init__(self):

        # If you don't want to used a connection info document, you can uncomment this, replace the strings with the information,
        # and comment the try except block further down
        # If you do this, make sure not to commit, so that you don't mess up anyone else

        # self.connection = mysql.connector.connect(
        #     host="hostname",
        #     user="username",
        #     password="password",
        #     database="database"
        # )

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

    def get_users(self) -> SQLResult:
        header = ("Username", "User Email", "User Status")
        rows = self.query("SELECT user_name, user_email, user_status FROM User")
        return SQLResult(header, rows)

    def get_holds(self) -> SQLResult:
        header = ("User", "Title", "Location", "#", "Status", "Created", "Expires")
        rows = self.query(SQLExecutor.HOLD_QUERY)
        return SQLResult(header, rows)

    def get_user_holds(self, user_id) -> SQLResult:
        header = ("User", "Title", "Location", "#", "Status", "Created", "Expires")
        rows = self.query(SQLExecutor.USER_HOLD_QUERY.replace("{user_id}", str(user_id)))
        return SQLResult(header, rows)

    def get_loans(self) -> SQLResult:
        header = ("User", "Title", "Location", "Checkout Date", "Due Date", "Status")
        rows = self.query(SQLExecutor.LOAN_QUERY)
        return SQLResult(header, rows)

    def get_items(self) -> SQLResult:
        header = ("Item Title", "Type", "Location", "Status")
        rows = self.query(SQLExecutor.ITEM_QUERY)
        return SQLResult(header, rows)
    
    def get_items_from_location(self, location_id) -> SQLResult:
        header = ("Title", "Author", "Type", "Copies Available")
        rows = self.query(SQLExecutor.LOCATION_ITEM_QUERY.replace("{location_id}", str(location_id)))
        id_rows = self.query(SQLExecutor.LOCATION_ITEM_ID_QUERY.replace("{location_id}", str(location_id)))
        return SQLResult(header, rows, id_rows)

    def get_item_types(self) -> SQLResult:
        header = ("item_title", "item_author", "item_release_date", "item_type")
        rows = self.query("SELECT item_title, item_author, item_release_date, item_type FROM ItemType")
        return SQLResult(header, rows)

    def get_most_loaned_items(self) -> SQLResult:
        header = ("Title", "Type", "Location", "Times loaned")
        rows = self.query(SQLExecutor.MOST_LOANED_ITEMS)
        return SQLResult(header, rows)

    def get_least_loaned_items(self) -> SQLResult:
        header = ("Title", "Type", "Location", "Times loaned")
        rows = self.query(SQLExecutor.LEAST_LOANED_ITEMS)
        return SQLResult(header, rows)

    def get_most_held_items(self) -> SQLResult:
        header = ("Title", "Type", "Times held")
        rows = self.query(SQLExecutor.MOST_HELD_ITEMS)
        return SQLResult(header, rows)

    def get_least_held_items(self) -> SQLResult:
        header = ("Title", "Type", "Times held")
        rows = self.query(SQLExecutor.LEAST_HELD_ITEMS)
        return SQLResult(header, rows)

    def get_locations(self) -> SQLResult:
        header = ("Location", "Address")
        rows = self.query("SELECT location_name, address FROM Location")
        return SQLResult(header, rows)

    def get_genres(self) -> SQLResult:
        header = ("Genre",)
        rows = self.query("SELECT genre_name FROM Genre")
        return SQLResult(header, rows)

    def get_popular_genres(self) -> SQLResult:
        header = ("Genre", "Number of items")
        rows = self.query(SQLExecutor.POPULAR_GENRES)
        return SQLResult(header, rows)
    
    def get_item_loan_history(self, item_id) -> SQLResult:
        header = ("User", "Title", "Location", "Checkout", "Return", "Status")
        rows = self.query(SQLExecutor.ITEM_LOAN_HISTORY.replace("{item_id}", str(item_id)))
        return SQLResult(header, rows)

    def get_item_hold_history(self, item_type_id) -> SQLResult:
        header = ("User", "Title", "Location", "Created", "Status")
        rows = self.query(SQLExecutor.ITEM_HOLD_HISTORY.replace("{item_type_id}", str(item_type_id)))
        return SQLResult(header, rows)

    def get_user_loan_history(self, user_id) -> SQLResult:
        header = ("User", "Title", "Location", "Checkout", "Return", "Status")
        rows = self.query(SQLExecutor.USER_LOAN_HISTORY.replace("{user_id}", str(user_id)))
        return SQLResult(header, rows)

    def get_user_hold_history(self, user_id) -> SQLResult:
        header = ("User", "Title", "Location", "Created", "Status")
        rows = self.query(SQLExecutor.USER_HOLD_HISTORY.replace("{user_id}", str(user_id)))
        return SQLResult(header, rows)


    def get_item_type_info(self, item_type_id) -> ItemType:
        data = self.query(f"SELECT it.item_title, it.item_author, it.item_publisher, it.item_type, it.item_release_date FROM ItemType it WHERE it.item_type_id = {item_type_id}")[0]
        genre_data = self.query(f"SELECT g.genre_name FROM Genre g JOIN ItemGenre ig ON (g.genre_id = ig.genre_id) WHERE ig.item_type_id = {item_type_id}")

        return ItemType(
            data[0],
            data[1],
            data[2],
            data[3],
            data[4],
            [t[0] for t in genre_data]
        )
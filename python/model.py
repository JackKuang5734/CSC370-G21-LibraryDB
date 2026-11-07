import re
from sql_executor import SQLExecutor, SQLResult

class Model:
    def __init__(self):
        self.sql = SQLExecutor()
        self.display_id = False

    def get_users(self) -> SQLResult:
        return self.sql.get_users(self.display_id)
    
    def get_holds(self) -> SQLResult:
        return self.sql.get_holds(self.display_id)
    
    def get_loans(self) -> SQLResult:
        return self.sql.get_loans(self.display_id)

    def get_item_types(self) -> SQLResult:
        return self.sql.get_item_types()

    def get_items(self, location_id : int|str|None = None) -> SQLResult:
        if location_id is None:
            return self.sql.get_items()
        else:
            return self.sql.get_items_from_location(str(location_id))

    def get_locations(self) -> SQLResult:
        return self.sql.get_locations(self.display_id)

    def get_genres(self) -> SQLResult:
        return self.sql.get_genre(self.display_id)

    def close(self):
        self.sql.close()
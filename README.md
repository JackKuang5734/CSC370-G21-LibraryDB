# CSC 370 Group 21 - Library Database

A MySQL-backed information system for running a library. It stores books, CDs, and audiobooks, tracks multiple copies across locations, and manages user loans and holds (including hold queues).

Built for CSC 370, Fall 2026. Team: Carmen Edora, Elliot Fox, Erica Ngo, Jack Kuang.

## What it does

The database is designed to support the following requirements:

- Store items of several types (book, CD, audiobook) with relevant attributes
- Store multiple physical or digital copies of the same title at different locations
- Keep current and historical loans and holds on each user account
- Keep holds in a queue per item type and location, with queue numbers
- Track hold status (waiting, ready for pickup, completed), hold created date, and hold expiry date
- Track loan status (ready for pickup, on loan, returned), checkout date, due date, and user

### Entities

| Table | Primary key | Description |
|---|---|---|
| `User` | `user_id` | A library account holder: name, email, account status |
| `ItemType` | `item_type_id` | A title-level record shared by all copies: title, author, publisher, media type, release date |
| `Item` | `item_id` | A single copy of an ItemType at a location, with a status |
| `Location` | `location_id` | A library branch: name and address |
| `Loan` | `loan_id` | A checkout of one item by one user, with checkout date, due date, and status |
| `Hold` | `hold_id` | A user's place in the queue for an item type at a location, with queue number, created and expiry dates, and status |
| `Genre` | `genre_id` | A genre name (unique) |
| `ItemGenre` | (`item_type_id`, `genre_id`) | Junction table linking item types to genres (many-to-many) |

### Relationships

- Each `Item` is a copy of one `ItemType` (`IsType`) and sits at one `Location`
- A `Loan` links a `User` to an `Item` (and records a `Location`)
- A `Hold` links a `User` to an `ItemType` at a `Location`
- `ItemGenre` links each `ItemType` to any number of `Genre` rows, and each `Genre` to any number of item types

### Functional dependencies

Each table's primary key determines every other attribute in that table:

```
user_id      -> user_name, user_email, user_status
loan_id      -> item_id, user_id, location_id, checkout_date, due_date, loan_status
hold_id      -> item_type_id, user_id, location_id, queue_number, hold_created_date, hold_expiry_date, hold_status
location_id  -> location_name, address
item_id      -> item_type_id, location_id, item_status
item_type_id -> item_title, item_author, item_publisher, item_type, item_release_date
genre_id     -> genre_name
```

ItemGenre has a composite key and no other attributes, so it has no non-trivial dependencies.

## Setup

These steps are for Ubuntu. Commands that start with `sudo mysql` use your Linux login password, not a MySQL password.

1. Requirements: MySQL 8.0 or later.
2. Clone the repo and move into it:
```
   git clone https://github.com/JackKuang5734/CSC370-G21-LibraryDB.git
   cd CSC370-G21-LibraryDB
```
3. Create the database:
```
   sudo mysql -e "CREATE DATABASE IF NOT EXISTS csc370;"
```
4. Run the schema script:
```
   sudo mysql csc370 < CSC370_PhaseOneLibraryDatabase.sql
```
5. Check that it worked. You should see 8 tables (Genre, Item, ItemGenre, ItemType, Location, User, Loan, Hold):
```
   sudo mysql csc370 -e "SHOW TABLES;"
```

### AI use
Claude (Anthropic) was used to help update the README to match the schema script and to draft the setup instructions; the team reviewed and tested the output.

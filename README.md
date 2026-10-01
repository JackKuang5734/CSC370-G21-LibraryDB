# CSC 370 Group 21 - Library Database

A MySQL-backed information system for running a library. It stores books, CDs, games, audiobooks, and e-books, tracks multiple copies across locations, and manages user loans and holds (including hold queues).

Built for CSC 370, Fall 2026. Team: Carmen Edora, Elliot Fox, Erica Ngo, Jack Kuang.

## What it does

The database is designed to support the following requirements:

- Store items of several types (book, CD, game, audiobook, e-book) with relevant attributes
- Store multiple physical or digital copies of the same title at different locations
- Keep current and historical loans and holds on each user account
- Keep holds in a queue per item type and location, with queue numbers
- Track hold status (available, not available, in transit, fulfilled), hold created date, and hold expiry date
- Track loan status (loaned, overdue, returned, lost), checkout date, due date, and user
- Store collections of books

## Data model

TO DO: add ERD? can i do that

### Entities

| Table | Primary key | Description |
|---|---|---|
| `User` | `user_id` | A library account holder: name, email, account status |
| `ItemType` | `item_type_id` | A title-level record shared by all copies: title, author, publisher, media type, genre, release date |
| `Item` | `item_id` | A single copy of an ItemType at a location, with a status |
| `Location` | `location_id` | A library branch: name and address |
| `Loan` | `loan_id` | A checkout of one item by one user, with checkout date, due date, and status |
| `Hold` | `hold_id` | A user's place in the queue for an item type at a location, with queue number, created and expiry dates, and status |

### Relationships

- Each `Item` is a copy of one `ItemType` (`IsType`) and sits at one `Location`
- A `Loan` links a `User` to an `Item` (and records a `Location`)
- A `Hold` links a `User` to an `ItemType` at a `Location`

### Functional dependencies

Each table's primary key determines every other attribute in that table:

```
user_id      -> user_name, user_email, user_status
loan_id      -> item_id, user_id, location_id, checkout_date, due_date, loan_status
hold_id      -> item_type_id, user_id, location_id, queue_number, hold_created_date, hold_expiry_date, hold_status
location_id  -> location_name, address
item_id      -> item_type_id, item_location_id, item_status
item_type_id -> item_title, item_author, item_publisher, item_type, item_genre, item_release_date
```

## Data sources

- Seattle Public Library open data (City of Seattle open data portal). TO DO: add more info (ask jack)

## Repository structure

TO DO: update once scripts are added!!

## Setup

TO DO: update

1. Requirements: MySQL [VERSION???]
2. Create the database:
3. Run the schema script:
4. Load the data:

## Verification

TO DO: describe the checks and how to run them

## AI use

TODO: record any AI assistance (tool, date, what it was used for, and how the output was checked or changed). For example: "Claude (Anthropic) was used to draft the initial README structure; the team reviewed and edited it."

## Version

Submission commit: something

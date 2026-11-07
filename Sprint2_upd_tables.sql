-- Adds missing functionality identified in Sprint 1

USE csc370;

ALTER TABLE Loan 
MODIFY COLUMN loan_status ENUM('ReadyForPickup', 'OnLoan', 'Returned', 'Overdue', 'Lost') NOT NULL;

ALTER TABLE Hold
MODIFY COLUMN hold_status ENUM('Waiting', 'ReadyForPickup', 'Completed', 'InTransit') NOT NULL;

ALTER TABLE ItemType
MODIFY COLUMN item_type ENUM('Book', 'CD', 'Audiobook', 'Ebook', 'Eaudiobook', 'VideoGame', 'DVD') NOT NULL;

ALTER TABLE Item
MODIFY COLUMN item_status ENUM('Available', 'OnLoan', 'OnHold', 'OutOfCirculation', 'Lost', 'InTransit') NOT NULL;

CREATE TABLE ItemCollection (
    collection_id INT AUTO_INCREMENT PRIMARY KEY,
    collection_name VARCHAR(255) NOT NULL,
    collection_desc VARCHAR(500) NULL
);

CREATE TABLE ItemTypeCollection (
    item_type_id INT NOT NULL,
    collection_id INT NOT NULL,
    series_position INT NULL,

    PRIMARY KEY (item_type_id, collection_id),
    UNIQUE (collection_id, series_position),
    FOREIGN KEY (item_type_id) REFERENCES ItemType(item_type_id),
    FOREIGN KEY (collection_id) REFERENCES ItemCollection(collection_id)
);


USE csc370;

CREATE TABLE ItemType (
    item_type_id INT AUTO_INCREMENT PRIMARY KEY,

    item_title VARCHAR(500) NOT NULL UNIQUE,
    item_author VARCHAR(255) NOT NULL,
    item_publisher VARCHAR(255) NOT NULL,
    item_type ENUM('Book', 'CD', 'Audiobook') NOT NULL,
    item_release_date DATE NULL
);

CREATE TABLE Location (
    location_id INT AUTO_INCREMENT PRIMARY KEY,
    location_name VARCHAR(255) NOT NULL,
    address VARCHAR(255) NOT NULL
);

CREATE TABLE Item (
    item_id INT PRIMARY KEY, 
    item_type_id INT NOT NULL,
    location_id INT NOT NULL,
    item_status ENUM('Available', 'OnLoan', 'OnHold', 'OutOfCirculation') NOT NULL,

    FOREIGN KEY (item_type_id) REFERENCES ItemType(item_type_id),
    FOREIGN KEY (location_id) REFERENCES Location(location_id)
);

CREATE TABLE User (
    user_id INT AUTO_INCREMENT Primary KEY,
    user_name VARCHAR(255) NOT NULL,
    user_email VARCHAR(255) NOT NULL,
    user_status ENUM('Active', 'Deleted') NOT NULL
);

CREATE TABLE LOAN (
    loan_id INT AUTO_INCREMENT PRIMARY KEY,
    item_id INT NOT NULL,
    user_id INT NOT NULL,
    location_id INT NOT NULL,
    checkout_date DATE NOT NULL,
    due_date DATE NOT NULL,
    loan_status ENUM('ReadyForPickup', 'OnLoan', 'Returned') NOT NULL,

    FOREIGN KEY (user_id) REFERENCES User(user_id),
    FOREIGN KEY (item_id) REFERENCES Item(item_id),
    FOREIGN KEY (location_id) REFERENCES Location(location_id)
);

CREATE TABLE HOLD (
    hold_id INT AUTO_INCREMENT PRIMARY KEY,
    item_type_id INT NOT NULL,
    user_id INT NOT NULL,
    location_id INT NOT NULL,

    queue_number INT NOT NULL,
    hold_created_date DATE NOT NULL,
    hold_expiry_date DATE NOT NULL,

    FOREIGN KEY (item_type_id) REFERENCES ItemType(item_type_id),
    FOREIGN KEY (user_id) REFERENCES User(user_id),
    FOREIGN KEY (location_id) REFERENCES Location(location_id),
     
    hold_status ENUM('Waiting', 'ReadyForPickup', 'Completed') NOT NULL
);

CREATE TABLE Genre (
    genre_id INT AUTO_INCREMENT PRIMARY KEY,
    genre_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE ItemGenre (
    item_type_id INT NOT NULL,
    genre_id INT NOT NULL,

    Primary KEY (item_type_id, genre_id),
    FOREIGN KEY (item_type_id) REFERENCES ItemType(item_type_id),
    FOREIGN KEY (genre_id) REFERENCES Genre(genre_id)
);

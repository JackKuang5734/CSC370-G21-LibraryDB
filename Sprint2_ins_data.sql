-- Inserts new data utilizing newly added functionality for Sprint 2

USE csc370;

-- Loan: 3 rows
INSERT INTO `Loan` (`loan_id`, `item_id`, `user_id`, `location_id`, `checkout_date`, `due_date`, `loan_status`) VALUES
  (4, 4, 1, 3, '2026-09-01', '2026-09-21', 'ReadyForPickup'),
  (5, 5, 2, 3, '2026-09-02', '2026-09-22', 'Overdue'),
  (6, 6, 3, 3, '2026-08-01', '2026-08-21', 'Lost');
  
-- Hold: 3 rows
INSERT INTO `Hold` (`hold_id`, `item_type_id`, `user_id`, `location_id`, `queue_number`, `hold_created_date`, `hold_expiry_date`, `hold_status`) VALUES
  (3, 1, 2, 2, 3, '2026-09-03', '2026-09-17', 'ReadyForPickup'),
  (4, 1, 2, 2, 4, '2026-09-03', '2026-09-17', 'Completed'),
  (5, 1, 3, 2, 5, '2026-09-04', '2026-09-18', 'InTransit');
  
-- ItemType: 3 rows
INSERT INTO `ItemType` (`item_type_id`, `item_title`, `item_author`, `item_publisher`, `item_type`, `item_release_date`) VALUES
  (101, 'Red Rising', 'Brown, Pierce', 'Penguin Random House', 'Ebook', '2014-01-28'),
  (102, 'Golden Son', 'Brown, Pierce', 'Penguin Random House', 'Eaudiobook', '2015-01-06'),
  (103, 'Morning Star', 'Brown, Pierce', 'Penguin Random House', 'DVD', '2016-02-09');
  
-- Item: 3 rows
INSERT INTO `Item` (`item_id`, `item_type_id`, `location_id`, `item_status`) VALUES
  (166, 101, 2, 'OutOfCirculation'),
  (167, 102, 2, 'Lost'),
  (168, 103, 2, 'InTransit');
  
-- ItemCollection: 3 rows
INSERT INTO `ItemCollection` (`collection_id`, `collection_name`, `collection_desc`) VALUES
  (1, 'Red Rising Saga', 'Science fiction series by Pierce Brown'),
  (2, 'Staff Picks', 'Titles recommended by library staff'),
  (3, 'Standalone Favourites', NULL);

-- ItemTypeCollection: 3 rows
INSERT INTO `ItemTypeCollection` (`item_type_id`, `collection_id`, `series_position`) VALUES
  (101, 1, 1),
  (102, 1, 2),
  (103, 1, 3);
  
COMMIT;


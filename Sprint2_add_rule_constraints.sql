USE csc370;

-- E08 and G01. Completed loan history has a NULL key and can repeat.
ALTER TABLE Loan
    ADD CONSTRAINT chk_loan_date_order CHECK (due_date >= checkout_date),
    ADD COLUMN blocking_item_id INT GENERATED ALWAYS AS (
        CASE WHEN loan_status IN ('ReadyForPickup', 'OnLoan', 'Overdue', 'Lost')
             THEN item_id END
    ) STORED,
    ADD UNIQUE KEY uq_loan_blocking_copy (blocking_item_id);

-- E09, E11 and G08. Completed holds release the open keys.
ALTER TABLE Hold
    ADD CONSTRAINT chk_hold_expiry_after_creation
        CHECK (hold_expiry_date > hold_created_date),
    ADD COLUMN open_hold_marker TINYINT GENERATED ALWAYS AS (
        CASE WHEN hold_status <> 'Completed' THEN 1 END
    ) STORED,
    ADD UNIQUE KEY uq_open_queue_position
        (item_type_id, location_id, queue_number, open_hold_marker);


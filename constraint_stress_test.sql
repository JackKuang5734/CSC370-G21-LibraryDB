-- CSC 370 Group 21 constraint stress tests for MySQL 8.0.16+
-- Requires the ORIGINAL sprint1_100_titles (1).sql import first, on a clean csc370 schema.
-- Safe in the supplied schema: fixtures and DML are inside a transaction that is ROLLED BACK.
-- Each test is executed within a SAVEPOINT. Test outcomes are saved to a TEMPORARY MEMORY table.
-- Declared E01-E20: expected to REJECT invalid changes and ACCEPT matching valid changes.
-- Business gaps G01-G13: expected behavior per requirements; they intentionally reveal gaps.
-- Runner repaired: matching delimiters; dynamically allocated fixture IDs; all 53 original probes retained.
-- Run: mysql -u root -p --default-character-set=utf8mb4 --table < CSC370_Constraint_Stress_Tests_MySQL8.sql > mysql_results.txt

USE `csc370`;
SET @csc370_old_sql_mode := @@SESSION.sql_mode;
SET SESSION sql_mode = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';
SET NAMES utf8mb4;
SET @csc370_old_foreign_key_checks := @@SESSION.foreign_key_checks;
SET SESSION foreign_key_checks = 1;

SELECT VERSION() AS mysql_version, @@SESSION.sql_mode AS session_sql_mode;

-- Preflight: expected seed counts and total FK orphan count.
SELECT 'User' AS entity, COUNT(*) AS rows_loaded FROM `User`
UNION ALL SELECT 'Location', COUNT(*) FROM `Location`
UNION ALL SELECT 'ItemType', COUNT(*) FROM `ItemType`
UNION ALL SELECT 'Genre', COUNT(*) FROM `Genre`
UNION ALL SELECT 'Item', COUNT(*) FROM `Item`
UNION ALL SELECT 'ItemGenre', COUNT(*) FROM `ItemGenre`
UNION ALL SELECT 'Loan', COUNT(*) FROM `Loan`
UNION ALL SELECT 'Hold', COUNT(*) FROM `Hold`;

SELECT SUM(orphan_rows) AS foreign_key_orphans FROM (
 SELECT COUNT(*) AS orphan_rows FROM `Item` c LEFT JOIN `ItemType` p ON c.item_type_id=p.item_type_id WHERE p.item_type_id IS NULL
 UNION ALL SELECT COUNT(*) FROM `Item` c LEFT JOIN `Location` p ON c.location_id=p.location_id WHERE p.location_id IS NULL
 UNION ALL SELECT COUNT(*) FROM `ItemGenre` c LEFT JOIN `ItemType` p ON c.item_type_id=p.   item_type_id WHERE p.item_type_id IS NULL
 UNION ALL SELECT COUNT(*) FROM `ItemGenre` c LEFT JOIN `Genre` p ON c.genre_id=p.genre_id WHERE p.genre_id IS NULL
 UNION ALL SELECT COUNT(*) FROM `Loan` c LEFT JOIN `Item` p ON c.item_id=p.item_id WHERE p.item_id IS NULL
 UNION ALL SELECT COUNT(*) FROM `Loan` c LEFT JOIN `User` p ON c.user_id=p.user_id WHERE p.user_id IS NULL
 UNION ALL SELECT COUNT(*) FROM `Loan` c LEFT JOIN `Location` p ON c.location_id=p.location_id WHERE p.location_id IS NULL
 UNION ALL SELECT COUNT(*) FROM `Hold` c LEFT JOIN `ItemType` p ON c.item_type_id=p.item_type_id WHERE p.item_type_id IS NULL
 UNION ALL SELECT COUNT(*) FROM `Hold` c LEFT JOIN `User` p ON c.user_id=p.user_id WHERE p.user_id IS NULL
 UNION ALL SELECT COUNT(*) FROM `Hold` c LEFT JOIN `Location` p ON c.location_id=p.location_id WHERE p.location_id IS NULL
) AS fk_orphans;

-- MEMORY tables do not roll back INSERTs, allowing us to retain a test log.
DROP TEMPORARY TABLE IF EXISTS csc370_test_results;
CREATE TEMPORARY TABLE csc370_test_results (
  case_id VARCHAR(8) NOT NULL,
  group_name VARCHAR(12) NOT NULL,
  rule_name VARCHAR(160) NOT NULL,
  case_type VARCHAR(16) NOT NULL,
  expected VARCHAR(8) NOT NULL,
  actual VARCHAR(8) NOT NULL,
  mysql_errno INT NULL,
  sqlstate_code VARCHAR(5) NULL,
  mysql_message VARCHAR(1024) NULL,
  verdict VARCHAR(22) NOT NULL,
  test_sql VARCHAR(1000) NOT NULL
) ENGINE=MEMORY;

DROP PROCEDURE IF EXISTS RunCSC370Test;
DELIMITER //
CREATE PROCEDURE RunCSC370Test (
    IN p_case_id VARCHAR(8),
    IN p_group VARCHAR(12),
    IN p_rule VARCHAR(160),
    IN p_case_type VARCHAR(16),
    IN p_sql TEXT,
    IN p_expected VARCHAR(8),
    IN p_error_codes VARCHAR(64)
)
BEGIN
    DECLARE v_error INT DEFAULT 0;
    DECLARE v_conditions INT DEFAULT 1;
    DECLARE v_prepared INT DEFAULT 0;
    DECLARE v_errno INT DEFAULT NULL;
    DECLARE v_sqlstate VARCHAR(5) DEFAULT '00000';
    DECLARE v_message VARCHAR(1024) DEFAULT '';
    DECLARE v_actual VARCHAR(8) DEFAULT 'ACCEPT';
    DECLARE v_verdict VARCHAR(22) DEFAULT 'PASS';

    SAVEPOINT csc370_casepoint;
    BEGIN
        -- ENUM truncation is error 1265 with warning-class SQLSTATE 01000 in strict mode.
        DECLARE CONTINUE HANDLER FOR SQLEXCEPTION, 1265
        BEGIN
            SET v_error = 1;
            GET STACKED DIAGNOSTICS v_conditions = NUMBER;
            GET STACKED DIAGNOSTICS CONDITION v_conditions
                v_sqlstate = RETURNED_SQLSTATE,
                v_errno = MYSQL_ERRNO,
                v_message = MESSAGE_TEXT;
        END;
        SET @csc370_test_sql = p_sql;
        PREPARE csc370_stmt FROM @csc370_test_sql;
        IF v_error = 0 THEN
            SET v_prepared = 1;
            EXECUTE csc370_stmt;
        END IF;
        IF v_prepared = 1 THEN
            DEALLOCATE PREPARE csc370_stmt;
        END IF;
    END;
    ROLLBACK TO SAVEPOINT csc370_casepoint;
    RELEASE SAVEPOINT csc370_casepoint;

    IF v_error = 1 THEN SET v_actual = 'REJECT'; END IF;
    IF v_actual <> p_expected THEN
        SET v_verdict = 'FAIL';
    ELSEIF p_expected = 'REJECT' AND p_error_codes IS NOT NULL
           AND FIND_IN_SET(CAST(v_errno AS CHAR CHARACTER SET utf8mb4) COLLATE utf8mb4_unicode_ci, p_error_codes COLLATE utf8mb4_unicode_ci) = 0 THEN
        SET v_verdict = 'WRONG_ERROR';
    END IF;

    INSERT INTO csc370_test_results (
        case_id, group_name, rule_name, case_type, expected,
        actual, mysql_errno, sqlstate_code, mysql_message, verdict, test_sql
    ) VALUES (
        p_case_id, p_group, p_rule, p_case_type, p_expected,
        v_actual, v_errno, v_sqlstate, v_message, v_verdict, p_sql
    );
END//
DELIMITER ;

-- Start fixtures. Each test itself is isolated with a savepoint.
-- Allocate fixture IDs above existing users and copies; preserve prior data.
SET @csc370_fixture_available = GREATEST(
    (SELECT COALESCE(MAX(user_id),0) FROM `User`),
    (SELECT COALESCE(MAX(item_id),0) FROM `Item`), 99002) + 1;
SET @csc370_fixture_deleted = @csc370_fixture_available + 1;
START TRANSACTION;
INSERT INTO `User` (user_id,user_name,user_status) VALUES (@csc370_fixture_available,'Stress unreferenced user','Active');
INSERT INTO `User` (user_id,user_name,user_status) VALUES (@csc370_fixture_deleted,'Stress deleted user','Deleted');
INSERT INTO `Item` (item_id,item_type_id,location_id,item_status) VALUES (@csc370_fixture_available,1,2,'Available');
INSERT INTO `Item` (item_id,item_type_id,location_id,item_status) VALUES (@csc370_fixture_deleted,1,2,'OutOfCirculation');

-- DECLARED CONSTRAINTS: 20 invalid + 20 matching valid statements.

-- E01: Duplicate user primary key
CALL RunCSC370Test('E01','DECLARED','Duplicate user primary key','invalid','INSERT INTO `User` (user_id,user_name,user_status) VALUES (1,''Duplicate Demo'',''Active'')','REJECT','1062');
CALL RunCSC370Test('E01','DECLARED','Duplicate user primary key','matching valid','INSERT INTO `User` (user_id,user_name,user_status) VALUES (94001,''New Demo'',''Active'')','ACCEPT',NULL);

-- E02: Composite ItemGenre primary key
CALL RunCSC370Test('E02','DECLARED','Composite ItemGenre primary key','invalid','INSERT INTO `ItemGenre` (item_type_id,genre_id) VALUES (1,76)','REJECT','1062');
CALL RunCSC370Test('E02','DECLARED','Composite ItemGenre primary key','matching valid','INSERT INTO `ItemGenre` (item_type_id,genre_id) VALUES (2,76)','ACCEPT',NULL);

-- E03: Unique item title
CALL RunCSC370Test('E03','DECLARED','Unique item title','invalid','INSERT INTO `ItemType` (item_type_id,item_title,item_type) SELECT 94003,item_title,''Book'' FROM `ItemType` WHERE item_type_id=1','REJECT','1062');
CALL RunCSC370Test('E03','DECLARED','Unique item title','matching valid','INSERT INTO `ItemType` (item_type_id,item_title,item_type) VALUES (94003,''CSC370 Unique Test Title 94003'',''Book'')','ACCEPT',NULL);

-- E04: Item references existing ItemType
CALL RunCSC370Test('E04','DECLARED','Item references existing ItemType','invalid','INSERT INTO `Item` (item_id,item_type_id,location_id) VALUES (94004,999999,2)','REJECT','1452');
CALL RunCSC370Test('E04','DECLARED','Item references existing ItemType','matching valid','INSERT INTO `Item` (item_id,item_type_id,location_id) VALUES (94004,1,2)','ACCEPT',NULL);

-- E05: Loan references existing user
CALL RunCSC370Test('E05','DECLARED','Loan references existing user','invalid','INSERT INTO `Loan` (loan_id,item_id,user_id,location_id,checkout_date,due_date,loan_status) VALUES (94005,1,999999,2,''2026-10-19'',''2026-11-02'',''OnLoan'')','REJECT','1452');
CALL RunCSC370Test('E05','DECLARED','Loan references existing user','matching valid','INSERT INTO `Loan` (loan_id,item_id,user_id,location_id,checkout_date,due_date,loan_status) VALUES (94005,1,1,2,''2026-10-19'',''2026-11-02'',''OnLoan'')','ACCEPT',NULL);

-- E06: Hold references existing branch
CALL RunCSC370Test('E06','DECLARED','Hold references existing branch','invalid','INSERT INTO `Hold` (hold_id,item_type_id,user_id,location_id,queue_number,hold_created_date,hold_expiry_date,hold_status) VALUES (94006,1,1,999999,94006,''2026-10-19'',''2026-11-01'',''Waiting'')','REJECT','1452');
CALL RunCSC370Test('E06','DECLARED','Hold references existing branch','matching valid','INSERT INTO `Hold` (hold_id,item_type_id,user_id,location_id,queue_number,hold_created_date,hold_expiry_date,hold_status) VALUES (94006,1,1,2,94006,''2026-10-19'',''2026-11-01'',''Waiting'')','ACCEPT',NULL);

-- E07: Loan checkout date is required
CALL RunCSC370Test('E07','DECLARED','Loan checkout date is required','invalid','INSERT INTO `Loan` (loan_id,item_id,user_id,location_id,checkout_date,due_date,loan_status) VALUES (94007,1,1,2,NULL,''2026-11-02'',''OnLoan'')','REJECT','1048');
CALL RunCSC370Test('E07','DECLARED','Loan checkout date is required','matching valid','INSERT INTO `Loan` (loan_id,item_id,user_id,location_id,checkout_date,due_date,loan_status) VALUES (94007,1,1,2,''2026-10-19'',''2026-11-02'',''OnLoan'')','ACCEPT',NULL);

-- E08: Loan due date must be >= checkout
CALL RunCSC370Test('E08','DECLARED','Loan due date must be >= checkout','invalid','INSERT INTO `Loan` (loan_id,item_id,user_id,location_id,checkout_date,due_date,loan_status) VALUES (94008,1,1,2,''2026-11-03'',''2026-11-02'',''OnLoan'')','REJECT','3819');
CALL RunCSC370Test('E08','DECLARED','Loan due date must be >= checkout','matching valid','INSERT INTO `Loan` (loan_id,item_id,user_id,location_id,checkout_date,due_date,loan_status) VALUES (94008,1,1,2,''2026-11-02'',''2026-11-03'',''OnLoan'')','ACCEPT',NULL);

-- E09: Hold expiry must be >= creation
CALL RunCSC370Test('E09','DECLARED','Hold expiry must be >= creation','invalid','INSERT INTO `Hold` (hold_id,item_type_id,user_id,location_id,queue_number,hold_created_date,hold_expiry_date,hold_status) VALUES (94009,1,1,2,94009,''2026-11-03'',''2026-11-02'',''Waiting'')','REJECT','3819');
CALL RunCSC370Test('E09','DECLARED','Hold expiry must be >= creation','matching valid','INSERT INTO `Hold` (hold_id,item_type_id,user_id,location_id,queue_number,hold_created_date,hold_expiry_date,hold_status) VALUES (94009,1,1,2,94009,''2026-11-02'',''2026-11-03'',''Waiting'')','ACCEPT',NULL);

-- E10: Queue number must be positive
CALL RunCSC370Test('E10','DECLARED','Queue number must be positive','invalid','INSERT INTO `Hold` (hold_id,item_type_id,user_id,location_id,queue_number,hold_created_date,hold_expiry_date,hold_status) VALUES (94010,1,1,2,0,''2026-10-19'',''2026-11-01'',''Waiting'')','REJECT','3819');
CALL RunCSC370Test('E10','DECLARED','Queue number must be positive','matching valid','INSERT INTO `Hold` (hold_id,item_type_id,user_id,location_id,queue_number,hold_created_date,hold_expiry_date,hold_status) VALUES (94010,1,1,2,94010,''2026-10-19'',''2026-11-01'',''Waiting'')','ACCEPT',NULL);

-- E11: Same-title branch queue position unique
CALL RunCSC370Test('E11','DECLARED','Same-title branch queue position unique','invalid','INSERT INTO `Hold` (hold_id,item_type_id,user_id,location_id,queue_number,hold_created_date,hold_expiry_date,hold_status) VALUES (94011,1,1,2,1,''2026-10-19'',''2026-11-01'',''Waiting'')','REJECT','1062');
CALL RunCSC370Test('E11','DECLARED','Same-title branch queue position unique','matching valid','INSERT INTO `Hold` (hold_id,item_type_id,user_id,location_id,queue_number,hold_created_date,hold_expiry_date,hold_status) VALUES (94011,1,1,2,94011,''2026-10-19'',''2026-11-01'',''Waiting'')','ACCEPT',NULL);

-- E12: Referenced user cannot be deleted
CALL RunCSC370Test('E12','DECLARED','Referenced user cannot be deleted','invalid','DELETE FROM `User` WHERE user_id=1','REJECT','1451');
CALL RunCSC370Test('E12','DECLARED','Referenced user cannot be deleted','matching valid',REPLACE(REPLACE('DELETE FROM `User` WHERE user_id=99001','99001',@csc370_fixture_available),'99002',@csc370_fixture_deleted),'ACCEPT',NULL);

-- E13: Item ENUM rejects unrecognized status
CALL RunCSC370Test('E13','DECLARED','Item ENUM rejects unrecognized status','invalid','UPDATE `Item` SET item_status=''Destroyed'' WHERE item_id=1','REJECT','1265,1366');
CALL RunCSC370Test('E13','DECLARED','Item ENUM rejects unrecognized status','matching valid','UPDATE `Item` SET item_status=''OnHold'' WHERE item_id=1','ACCEPT',NULL);

-- E14: Item location cannot be NULL
CALL RunCSC370Test('E14','DECLARED','Item location cannot be NULL','invalid','UPDATE `Item` SET location_id=NULL WHERE item_id=1','REJECT','1048');
CALL RunCSC370Test('E14','DECLARED','Item location cannot be NULL','matching valid','UPDATE `Item` SET location_id=2 WHERE item_id=1','ACCEPT',NULL);

-- E15: Referenced copy cannot be deleted
CALL RunCSC370Test('E15','DECLARED','Referenced copy cannot be deleted','invalid','DELETE FROM `Item` WHERE item_id=1','REJECT','1451');
CALL RunCSC370Test('E15','DECLARED','Referenced copy cannot be deleted','matching valid',REPLACE(REPLACE('DELETE FROM `Item` WHERE item_id=99001','99001',@csc370_fixture_available),'99002',@csc370_fixture_deleted),'ACCEPT',NULL);

-- E16: ItemGenre references existing genre
CALL RunCSC370Test('E16','DECLARED','ItemGenre references existing genre','invalid','INSERT INTO `ItemGenre` (item_type_id,genre_id) VALUES (1,999999)','REJECT','1452');
CALL RunCSC370Test('E16','DECLARED','ItemGenre references existing genre','matching valid','INSERT INTO `ItemGenre` (item_type_id,genre_id) VALUES (2,76)','ACCEPT',NULL);

-- E17: Loan ENUM restricts invalid status
CALL RunCSC370Test('E17','DECLARED','Loan ENUM restricts invalid status','invalid','UPDATE `Loan` SET loan_status=''Destroyed'' WHERE loan_id=1','REJECT','1265,1366');
CALL RunCSC370Test('E17','DECLARED','Loan ENUM restricts invalid status','matching valid','UPDATE `Loan` SET loan_status=''Returned'' WHERE loan_id=1','ACCEPT',NULL);

-- E18: Hold ENUM restricts invalid status
CALL RunCSC370Test('E18','DECLARED','Hold ENUM restricts invalid status','invalid','UPDATE `Hold` SET hold_status=''Destroyed'' WHERE hold_id=1','REJECT','1265,1366');
CALL RunCSC370Test('E18','DECLARED','Hold ENUM restricts invalid status','matching valid','UPDATE `Hold` SET hold_status=''ReadyForPickup'' WHERE hold_id=1','ACCEPT',NULL);

-- E19: Media ENUM restricts invalid category
CALL RunCSC370Test('E19','DECLARED','Media ENUM restricts invalid category','invalid','UPDATE `ItemType` SET item_type=''Magazine'' WHERE item_type_id=1','REJECT','1265,1366');
CALL RunCSC370Test('E19','DECLARED','Media ENUM restricts invalid category','matching valid','UPDATE `ItemType` SET item_type=''CD'' WHERE item_type_id=1','ACCEPT',NULL);

-- E20: Genre name is unique
CALL RunCSC370Test('E20','DECLARED','Genre name is unique','invalid','INSERT INTO `Genre` (genre_id,genre_name) SELECT 94020,genre_name FROM `Genre` WHERE genre_id=76','REJECT','1062');
CALL RunCSC370Test('E20','DECLARED','Genre name is unique','matching valid','INSERT INTO `Genre` (genre_id,genre_name) VALUES (94020,''CSC370 Stress Test Genre 94020'')','ACCEPT',NULL);

-- MISSING / INCOMPLETE BUSINESS CONSTRAINTS: 13 diagnostic probes.

-- G01: Prevent a second active loan of an already loaned copy
CALL RunCSC370Test('G01','MISSING','Prevent a second active loan of an already loaned copy','gap probe','INSERT INTO `Loan` (loan_id,item_id,user_id,location_id,checkout_date,due_date,loan_status) VALUES (95001,1,2,2,''2026-10-19'',''2026-11-02'',''OnLoan'')','REJECT',NULL);

-- G02: Cannot loan an OutOfCirculation copy
CALL RunCSC370Test('G02','MISSING','Cannot loan an OutOfCirculation copy','gap probe',REPLACE(REPLACE('INSERT INTO `Loan` (loan_id,item_id,user_id,location_id,checkout_date,due_date,loan_status) VALUES (95002,99002,1,2,''2026-10-19'',''2026-11-02'',''OnLoan'')','99001',@csc370_fixture_available),'99002',@csc370_fixture_deleted),'REJECT',NULL);

-- G03: Deleted user cannot borrow
CALL RunCSC370Test('G03','MISSING','Deleted user cannot borrow','gap probe',REPLACE(REPLACE('INSERT INTO `Loan` (loan_id,item_id,user_id,location_id,checkout_date,due_date,loan_status) VALUES (95003,99001,99002,2,''2026-10-19'',''2026-11-02'',''OnLoan'')','99001',@csc370_fixture_available),'99002',@csc370_fixture_deleted),'REJECT',NULL);

-- G04: Prevent duplicate active holds by same user
CALL RunCSC370Test('G04','MISSING','Prevent duplicate active holds by same user','gap probe','INSERT INTO `Hold` (hold_id,item_type_id,user_id,location_id,queue_number,hold_created_date,hold_expiry_date,hold_status) VALUES (95004,1,2,2,95004,''2026-10-19'',''2026-11-01'',''Waiting'')','REJECT',NULL);

-- G05: Active loan cannot coexist with Available item
CALL RunCSC370Test('G05','MISSING','Active loan cannot coexist with Available item','gap probe','UPDATE `Item` SET item_status=''Available'' WHERE item_id=1','REJECT',NULL);

-- G06: Loan branch must agree with copy branch
CALL RunCSC370Test('G06','MISSING','Loan branch must agree with copy branch','gap probe',REPLACE(REPLACE('INSERT INTO `Loan` (loan_id,item_id,user_id,location_id,checkout_date,due_date,loan_status) VALUES (95006,99001,1,1,''2026-10-19'',''2026-11-02'',''OnLoan'')','99001',@csc370_fixture_available),'99002',@csc370_fixture_deleted),'REJECT',NULL);

-- G07: Hold queue order must honor creation dates
CALL RunCSC370Test('G07','MISSING','Hold queue order must honor creation dates','gap probe','INSERT INTO `Hold` (hold_id,item_type_id,user_id,location_id,queue_number,hold_created_date,hold_expiry_date,hold_status) VALUES (95007,1,1,2,3,''2026-01-01'',''2026-11-01'',''Waiting'')','REJECT',NULL);

-- G08: Hold expiry should be strictly after creation
CALL RunCSC370Test('G08','MISSING','Hold expiry should be strictly after creation','gap probe','INSERT INTO `Hold` (hold_id,item_type_id,user_id,location_id,queue_number,hold_created_date,hold_expiry_date,hold_status) VALUES (95008,1,1,2,95008,''2026-10-19'',''2026-10-19'',''Waiting'')','REJECT',NULL);

-- G09: Required Overdue loan status should be accepted
CALL RunCSC370Test('G09','MISSING','Required Overdue loan status should be accepted','gap probe','UPDATE `Loan` SET loan_status=''Overdue'' WHERE loan_id=1','ACCEPT',NULL);

-- G10: Required Lost loan status should be accepted
CALL RunCSC370Test('G10','MISSING','Required Lost loan status should be accepted','gap probe','UPDATE `Loan` SET loan_status=''Lost'' WHERE loan_id=1','ACCEPT',NULL);

-- G11: Required InTransit hold status should be accepted
CALL RunCSC370Test('G11','MISSING','Required InTransit hold status should be accepted','gap probe','UPDATE `Hold` SET hold_status=''InTransit'' WHERE hold_id=1','ACCEPT',NULL);

-- G12: Required Game media type should be accepted
CALL RunCSC370Test('G12','MISSING','Required Game media type should be accepted','gap probe','UPDATE `ItemType` SET item_type=''Game'' WHERE item_type_id=1','ACCEPT',NULL);

-- G13: Required Ebook media type should be accepted
CALL RunCSC370Test('G13','MISSING','Required Ebook media type should be accepted','gap probe','UPDATE `ItemType` SET item_type=''Ebook'' WHERE item_type_id=1','ACCEPT',NULL);

-- Before rolling back the fixture transaction, query the non-transactional temp results.
SELECT COUNT(*) AS recorded_tests FROM csc370_test_results; -- expected: 53
SELECT case_id, group_name, rule_name, case_type, expected, actual,
       mysql_errno, sqlstate_code, mysql_message, verdict
FROM csc370_test_results
ORDER BY group_name DESC, case_id, FIELD(case_type,'invalid','matching valid','gap probe');

SELECT group_name, COUNT(*) AS tests_run,
       SUM(verdict='PASS') AS passed,
       SUM(verdict='FAIL') AS failed,
       SUM(verdict='WRONG_ERROR') AS wrong_error
FROM csc370_test_results GROUP BY group_name;

-- Protect the original data. The MEMORY result table remains available until disconnect.
ROLLBACK;

SELECT 'AFTER ROLLBACK' AS phase, COUNT(*) AS user_rows FROM `User`;
SELECT 'AFTER ROLLBACK' AS phase, COUNT(*) AS item_rows FROM `Item`;
SELECT 'AFTER ROLLBACK' AS phase, COUNT(*) AS loan_rows FROM `Loan`;
SELECT 'AFTER ROLLBACK' AS phase, COUNT(*) AS hold_rows FROM `Hold`;

DROP PROCEDURE IF EXISTS RunCSC370Test;
SET SESSION sql_mode = @csc370_old_sql_mode;
SET SESSION foreign_key_checks = @csc370_old_foreign_key_checks;


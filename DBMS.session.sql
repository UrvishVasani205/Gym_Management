-- Create Database
CREATE DATABASE IF NOT EXISTS gym_management;
USE gym_management;

-- Enable support for triggers and procedures
SET GLOBAL event_scheduler = ON;

-- USER Table
CREATE TABLE IF NOT EXISTS USER (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,  -- Storing hashed password
    email VARCHAR(100) UNIQUE NOT NULL,
    wallet_balance DECIMAL(10,2) DEFAULT 1000.00,  -- Initial balance 1000 units
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ADMIN Table
CREATE TABLE IF NOT EXISTS ADMIN (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    wallet_balance DECIMAL(10,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- SUBSCRIPTION Table
CREATE TABLE IF NOT EXISTS SUBSCRIPTION (
    subscription_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    remaining_days INT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    status ENUM('active', 'expired', 'cancelled') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES USER(user_id),
    CONSTRAINT valid_dates CHECK (end_date >= start_date),
    CONSTRAINT valid_remaining_days CHECK (remaining_days >= 0)
);

-- TRANSACTION Table
CREATE TABLE IF NOT EXISTS TRANSACTION (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    subscription_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    transaction_type ENUM('subscription_purchase', 'refund') DEFAULT 'subscription_purchase',
    status ENUM('pending', 'completed', 'failed') DEFAULT 'pending',
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES USER(user_id),
    FOREIGN KEY (subscription_id) REFERENCES SUBSCRIPTION(subscription_id)
);

-- ATTENDANCE Table
CREATE TABLE IF NOT EXISTS ATTENDANCE (
    attendance_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    subscription_id INT NOT NULL,
    attendance_date DATE NOT NULL,
    is_present BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES USER(user_id),
    FOREIGN KEY (subscription_id) REFERENCES SUBSCRIPTION(subscription_id),
    UNIQUE KEY unique_attendance (user_id, attendance_date)
);

-- SUBSCRIPTION_LOG Table
CREATE TABLE IF NOT EXISTS SUBSCRIPTION_LOG (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    subscription_id INT NOT NULL,
    action_type VARCHAR(50) NOT NULL,
    old_remaining_days INT,
    new_remaining_days INT,
    triggered_by VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subscription_id) REFERENCES SUBSCRIPTION(subscription_id)
);

-- TRANSACTION_LOG Table
CREATE TABLE IF NOT EXISTS TRANSACTION_LOG (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_id INT NOT NULL,
    action_type VARCHAR(50) NOT NULL,
    old_status VARCHAR(20),
    new_status VARCHAR(20),
    triggered_by VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (transaction_id) REFERENCES TRANSACTION(transaction_id)
);

-- Procedure to check subscription overlap
DELIMITER //
CREATE PROCEDURE IF NOT EXISTS check_subscription_overlap(
    IN p_user_id INT,
    IN p_start_date DATE,
    IN p_end_date DATE,
    OUT p_has_overlap BOOLEAN
)
BEGIN
    SELECT EXISTS (
        SELECT 1 FROM SUBSCRIPTION
        WHERE user_id = p_user_id
        AND is_active = TRUE
        AND status = 'active'
        AND ((start_date BETWEEN p_start_date AND p_end_date)
        OR (end_date BETWEEN p_start_date AND p_end_date)
        OR (start_date <= p_start_date AND end_date >= p_end_date))
    ) INTO p_has_overlap;
END //
DELIMITER ;

-- Procedure to create new subscription
DELIMITER //
CREATE PROCEDURE IF NOT EXISTS create_subscription(
    IN p_user_id INT,
    IN p_start_date DATE,
    IN p_end_date DATE
)
BEGIN
    DECLARE subscription_cost DECIMAL(10,2);
    DECLARE user_balance DECIMAL(10,2);
    DECLARE new_subscription_id INT;
    DECLARE has_overlap BOOLEAN;
    DECLARE days_count INT;

    -- Start transaction
    START TRANSACTION;

    -- Check for overlap
    CALL check_subscription_overlap(p_user_id, p_start_date, p_end_date, has_overlap);
    IF has_overlap THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Subscription overlap detected';
    END IF;

    -- Calculate days and cost
    SET days_count = DATEDIFF(p_end_date, p_start_date) + 1;
    SET subscription_cost = days_count * 1.00;

    -- Check user balance
    SELECT wallet_balance INTO user_balance FROM USER WHERE user_id = p_user_id FOR UPDATE;
    IF user_balance < subscription_cost THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Insufficient balance';
    END IF;

    -- Create subscription
    INSERT INTO SUBSCRIPTION (user_id, start_date, end_date, remaining_days)
    VALUES (p_user_id, p_start_date, p_end_date, days_count);

    SET new_subscription_id = LAST_INSERT_ID();

    -- Create transaction
    INSERT INTO TRANSACTION (user_id, subscription_id, amount)
    VALUES (p_user_id, new_subscription_id, subscription_cost);

    -- Update balances
    UPDATE USER SET wallet_balance = wallet_balance - subscription_cost
    WHERE user_id = p_user_id;

    UPDATE ADMIN SET wallet_balance = wallet_balance + subscription_cost
    WHERE admin_id = 1;

    COMMIT;
END //
DELIMITER ;

-- Event to update remaining days daily
DELIMITER //
CREATE EVENT IF NOT EXISTS update_remaining_days_daily
ON SCHEDULE EVERY 1 DAY
STARTS CURRENT_TIMESTAMP
DO
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE curr_subscription_id INT;
    DECLARE curr_remaining_days INT;

    DECLARE subscription_cursor CURSOR FOR
        SELECT subscription_id, remaining_days
        FROM SUBSCRIPTION
        WHERE is_active = TRUE AND status = 'active';

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    OPEN subscription_cursor;

    subscription_loop: LOOP
        FETCH subscription_cursor INTO curr_subscription_id, curr_remaining_days;
        IF done THEN
            LEAVE subscription_loop;
        END IF;

        IF curr_remaining_days > 0 THEN
            UPDATE SUBSCRIPTION
            SET remaining_days = remaining_days - 1
            WHERE subscription_id = curr_subscription_id;

            INSERT INTO SUBSCRIPTION_LOG (
                subscription_id,
                action_type,
                old_remaining_days,
                new_remaining_days,
                triggered_by
            )
            VALUES (
                curr_subscription_id,
                'daily_update',
                curr_remaining_days,
                curr_remaining_days - 1,
                'system'
            );

            IF curr_remaining_days - 1 = 0 THEN
                UPDATE SUBSCRIPTION
                SET status = 'expired', is_active = FALSE
                WHERE subscription_id = curr_subscription_id;
            END IF;
        END IF;
    END LOOP;

    CLOSE subscription_cursor;
END //
DELIMITER ;

-- Trigger for transaction status updates
DELIMITER //
CREATE TRIGGER IF NOT EXISTS after_transaction_update
AFTER UPDATE ON TRANSACTION
FOR EACH ROW
BEGIN
    IF NEW.status != OLD.status THEN
        INSERT INTO TRANSACTION_LOG (
            transaction_id,
            action_type,
            old_status,
            new_status,
            triggered_by
        )
        VALUES (
            NEW.transaction_id,
            'status_update',
            OLD.status,
            NEW.status,
            'system'
        );
    END IF;
END //
DELIMITER ;

-- Active Subscriptions View
CREATE OR REPLACE VIEW active_subscriptions_view AS
SELECT
    s.subscription_id,
    u.username,
    u.email,
    s.start_date,
    s.end_date,
    s.remaining_days,
    s.status
FROM SUBSCRIPTION s
JOIN USER u ON s.user_id = u.user_id
WHERE s.is_active = TRUE;

-- Transaction History View
CREATE OR REPLACE VIEW transaction_history_view AS
SELECT
    t.transaction_id,
    u.username,
    t.amount,
    t.transaction_type,
    t.status,
    t.transaction_date
FROM TRANSACTION t
JOIN USER u ON t.user_id = u.user_id;

-- Attendance Tracking View
CREATE OR REPLACE VIEW attendance_tracking_view AS
SELECT
    a.attendance_date,
    u.username,
    s.subscription_id,
    a.is_present
FROM ATTENDANCE a
JOIN USER u ON a.user_id = u.user_id
JOIN SUBSCRIPTION s ON a.subscription_id = s.subscription_id;

-- Indexes for optimization
CREATE INDEX IF NOT EXISTS idx_subscription_dates ON SUBSCRIPTION(start_date, end_date);
CREATE INDEX IF NOT EXISTS idx_transaction_date ON TRANSACTION(transaction_date);
CREATE INDEX IF NOT EXISTS idx_attendance_date ON ATTENDANCE(attendance_date);

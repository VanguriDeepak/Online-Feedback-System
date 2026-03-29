-- ============================================================
-- Online Feedback System — SQLite Database Schema
-- ============================================================
-- Database: feedback.db
-- Table:    feedbacks
-- Author:   Member 3 (Database)
-- ============================================================

-- -----------------------------------------------------------
-- TABLE: feedbacks
-- -----------------------------------------------------------
-- Stores all user-submitted feedback entries.
-- Fields:
--   id      → auto-incrementing primary key
--   name    → name of the person submitting feedback
--   message → the feedback text / comment
--   rating  → star rating from 1 to 5
-- -----------------------------------------------------------

DROP TABLE IF EXISTS feedbacks;

CREATE TABLE feedbacks (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    name    TEXT    NOT NULL,
    message TEXT    NOT NULL,
    rating  INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5)
);

-- -----------------------------------------------------------
-- SAMPLE INSERT QUERIES
-- -----------------------------------------------------------

INSERT INTO feedbacks (name, message, rating)
    VALUES ('Alice Smith', 'The website is really easy to use!', 5);

INSERT INTO feedbacks (name, message, rating)
    VALUES ('Bob Johnson', 'I had some issues finding what I needed.', 3);

INSERT INTO feedbacks (name, message, rating)
    VALUES ('Charlie Brown', 'Great service entirely. The staff was super helpful. Keep it up!', 5);

INSERT INTO feedbacks (name, message, rating)
    VALUES ('David Lee', 'The login page gave me an error once, but overall fine.', 4);

INSERT INTO feedbacks (name, message, rating)
    VALUES ('Eva Martinez', 'Average experience. Could improve the response time.', 3);

INSERT INTO feedbacks (name, message, rating)
    VALUES ('Frank White', 'Absolutely loved the clean interface and fast performance!', 5);

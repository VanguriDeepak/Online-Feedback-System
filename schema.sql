-- ============================================================
-- Student Task / To-Do Manager — SQLite Database Schema
-- ============================================================
-- Database: task_manager.db
-- Tables:   Users, Tasks
-- Relationship: Tasks.user_id → Users.id (One-to-Many)
-- ============================================================

-- Enable foreign key enforcement (SQLite has it OFF by default)
PRAGMA foreign_keys = ON;

-- -----------------------------------------------------------
-- TABLE 1: Users
-- -----------------------------------------------------------
-- Stores registered student accounts.
-- Each user can own multiple tasks (1:N relationship).
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS Users (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT    NOT NULL UNIQUE,
    password TEXT    NOT NULL
);

-- -----------------------------------------------------------
-- TABLE 2: Tasks
-- -----------------------------------------------------------
-- Stores to-do items belonging to a user.
-- status defaults to 'Pending' and can be set to 'Completed'.
-- deadline is stored as TEXT in ISO-8601 format (YYYY-MM-DD).
-- ON DELETE CASCADE: deleting a user removes their tasks too.
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS Tasks (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id  INTEGER NOT NULL,
    title    TEXT    NOT NULL,
    deadline TEXT,
    status   TEXT    NOT NULL DEFAULT 'Pending'
                     CHECK (status IN ('Pending', 'Completed')),
    FOREIGN KEY (user_id) REFERENCES Users (id)
        ON DELETE CASCADE
);

-- -----------------------------------------------------------
-- SAMPLE INSERT QUERIES
-- -----------------------------------------------------------

-- Insert sample users
INSERT INTO Users (username, password) VALUES ('alice',   'alice123');
INSERT INTO Users (username, password) VALUES ('bob',     'bob456');
INSERT INTO Users (username, password) VALUES ('charlie', 'charlie789');

-- Insert sample tasks for alice (user_id = 1)
INSERT INTO Tasks (user_id, title, deadline, status)
    VALUES (1, 'Complete Math Assignment',  '2026-04-05', 'Pending');
INSERT INTO Tasks (user_id, title, deadline, status)
    VALUES (1, 'Read Chapter 4 - DBMS',    '2026-04-02', 'Pending');
INSERT INTO Tasks (user_id, title, deadline, status)
    VALUES (1, 'Submit Lab Report',         '2026-03-30', 'Completed');

-- Insert sample tasks for bob (user_id = 2)
INSERT INTO Tasks (user_id, title, deadline, status)
    VALUES (2, 'Prepare Presentation',      '2026-04-10', 'Pending');
INSERT INTO Tasks (user_id, title, deadline, status)
    VALUES (2, 'Online Quiz - Python',      '2026-04-01', 'Completed');

-- Insert sample tasks for charlie (user_id = 3)
INSERT INTO Tasks (user_id, title, deadline, status)
    VALUES (3, 'Group Project Meeting',     '2026-04-03', 'Pending');

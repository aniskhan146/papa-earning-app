CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    balance REAL NOT NULL,
    lifetime_points REAL NOT NULL,
    history TEXT NOT NULL,
    last_ad_time REAL NOT NULL,
    last_daily_bonus TEXT
);

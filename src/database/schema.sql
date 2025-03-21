-- STOCK METADATA
CREATE TABLE IF NOT EXISTS stock_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT UNIQUE NOT NULL,
    company_name TEXT,
    exchange TEXT,
    sector TEXT,
    industry TEXT,
    currency TEXT,
    metadata_fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- STOCK PRICES
CREATE TABLE IF NOT EXISTS stock_prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_id INTEGER NOT NULL,
    interval TEXT NOT NULL,
    date DATE NOT NULL,
    open REAL,
    close REAL,
    high REAL,
    low REAL,
    volume INTEGER,
    dividends REAL,
    splits REAL,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES stock_metadata (id),
    UNIQUE (stock_id, interval, date)
);

-- ECONOMIC SERIES METADATA
CREATE TABLE IF NOT EXISTS economic_series (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    series_id TEXT NOT NULL,
    title TEXT,
    frequency TEXT,
    units TEXT,
    seasonal_adjustment TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (source, series_id)
);

-- ECONOMIC DATA WITH REVISIONS
CREATE TABLE IF NOT EXISTS economic_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    economic_series_id INTEGER NOT NULL,
    date DATE NOT NULL,
    realtime_start DATE NOT NULL,
    realtime_end DATE NOT NULL,
    value REAL NOT NULL,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (economic_series_id) REFERENCES economic_series (id),
    UNIQUE (economic_series_id, date, realtime_start)
);

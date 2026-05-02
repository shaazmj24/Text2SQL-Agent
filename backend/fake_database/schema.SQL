--- Users table 
CREATE TABLE users (
    id              SERIAL PRIMARY KEY,
    name            TEXT NOT NULL,
    email           VARCHAR(254) UNIQUE NOT NULL,
    country         TEXT,
    source          TEXT,                        -- how they found this product (google, referral, internet, etc)
    plan            TEXT DEFAULT 'free',         -- free, basic, pro, 
    is_paying       BOOLEAN DEFAULT FALSE,
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMP DEFAULT NOW(),     -- when they signed up
    last_seen_at    TIMESTAMP,                   -- last login or activity
    updated_at      TIMESTAMP DEFAULT NOW()      -- when this record was last changed
);

 
-- Orders table
CREATE TABLE orders (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER REFERENCES users(id),   -- one user can have many orders
    plan_type       TEXT,                            -- pro_monthly, enterprise_annual, etc
    price           DECIMAL(10,2),
    currency        TEXT DEFAULT 'USD',
    order_status    TEXT DEFAULT 'pending',          -- pending, completed, cancelled
    is_refunded     BOOLEAN DEFAULT FALSE,
    refunded_at     TIMESTAMP,                       -- null until refund happens
    created_at      TIMESTAMP DEFAULT NOW()
);


-- subscriptions table
CREATE TABLE subscrip (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER REFERENCES users(id),   -- whose subscription this is
    plan_type       TEXT,                            -- free, pro_monthly, enterprise_annual
    price           DECIMAL(10,2),                  -- what they pay per cycle
    currency        TEXT DEFAULT 'USD',
    sub_status      TEXT DEFAULT 'active',           -- active, cancelled, expired
    auto_renew      BOOLEAN DEFAULT TRUE,            -- most users leave this on
    started_at      TIMESTAMP DEFAULT NOW(),
    ends_at         TIMESTAMP,                       -- calculated when inserted
    updated_at      TIMESTAMP DEFAULT NOW()          -- changes on upgrade/downgrade/cancel
);


-- events table
CREATE TABLE events (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER REFERENCES users(id),
    event_type  TEXT,
    page        TEXT,
    created_at  TIMESTAMP DEFAULT NOW()
);



DROP TABLE IF EXISTS tracking_events;
DROP TABLE IF EXISTS shipments;
DROP TABLE IF EXISTS users;
CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,email TEXT NOT NULL UNIQUE,password_hash TEXT NOT NULL,role TEXT NOT NULL DEFAULT 'customer' CHECK(role IN ('customer','admin')),created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE shipments (id INTEGER PRIMARY KEY AUTOINCREMENT,tracking_id TEXT NOT NULL UNIQUE,user_id INTEGER NOT NULL,sender_name TEXT NOT NULL,sender_phone TEXT NOT NULL,receiver_name TEXT NOT NULL,receiver_phone TEXT NOT NULL,pickup_address TEXT NOT NULL,delivery_address TEXT NOT NULL,package_description TEXT NOT NULL,weight REAL NOT NULL,status TEXT NOT NULL DEFAULT 'Pending',estimated_delivery TEXT,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
CREATE TABLE tracking_events (id INTEGER PRIMARY KEY AUTOINCREMENT,shipment_id INTEGER NOT NULL,status TEXT NOT NULL,location TEXT NOT NULL,note TEXT,event_time TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(shipment_id) REFERENCES shipments(id) ON DELETE CASCADE);
CREATE INDEX idx_shipments_tracking ON shipments(tracking_id);
CREATE INDEX idx_shipments_user ON shipments(user_id);

-- LOPUTH JOSEEPH OMEGA - Database Initialization
-- SQLite Setup for Development/Testing

-- Create tables
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(100),
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'viewer' CHECK (role IN ('admin', 'operator', 'viewer')),
    disabled BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp BIGINT NOT NULL,
    event VARCHAR(50) NOT NULL,
    details TEXT,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS commands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp BIGINT NOT NULL,
    command TEXT NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp BIGINT NOT NULL,
    activeProtections INTEGER,
    threatsNeutralized INTEGER,
    ghostCount BIGINT,
    polymorphicShifts INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS firewall_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_ip VARCHAR(45),
    destination_ip VARCHAR(45),
    port INTEGER,
    action VARCHAR(10) CHECK (action IN ('allow', 'deny')),
    protocol VARCHAR(10) DEFAULT 'TCP',
    enabled BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS threat_detections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    threat_type VARCHAR(50),
    severity VARCHAR(20) CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    source_ip VARCHAR(45),
    target_ip VARCHAR(45),
    description TEXT,
    metadata TEXT,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved BOOLEAN DEFAULT 0
);

CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id VARCHAR(255),
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    changes TEXT,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_disabled ON users(disabled);
CREATE INDEX IF NOT EXISTS idx_timestamp ON logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_event ON logs(event);
CREATE INDEX IF NOT EXISTS idx_cmd_timestamp ON commands(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON metrics(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_firewall_action ON firewall_rules(action);
CREATE INDEX IF NOT EXISTS idx_firewall_port ON firewall_rules(port);
CREATE INDEX IF NOT EXISTS idx_threat_severity ON threat_detections(severity);
CREATE INDEX IF NOT EXISTS idx_threat_detected ON threat_detections(detected_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_log(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_log(action);

-- Insert default admin user (password: letmein)
INSERT OR IGNORE INTO users (username, full_name, hashed_password, role)
VALUES ('admin', 'Omega Administrator', '$pbkdf2-sha256$260000$dXE4RnRFMVV5Vm01ZGZkUA$JFd1JVD9L.qKBfC8rPJxL1bvH7jPHP2Jlh7eH5xnQGw', 'admin');

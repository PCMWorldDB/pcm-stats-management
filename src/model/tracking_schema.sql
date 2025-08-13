CREATE TABLE tbl_cyclists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pcm_id VARCHAR(255) NOT NULL,
    name VARCHAR(511) NOT NULL,
    first_cycling_id VARCHAR(255),
    UNIQUE (pcm_id)
);

CREATE TABLE tbl_changes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(511) NOT NULL,
    description TEXT NULL,
    author VARCHAR(511) DEFAULT 'Unknown',
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (name)
);

CREATE TABLE tbl_change_stat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cyclist_id INT NOT NULL,
    change_id INT NOT NULL,
    stat_name VARCHAR(32) NOT NULL,
    stat_value INT NOT NULL,
    version INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cyclist_id) REFERENCES tbl_cyclists(id),
    FOREIGN KEY (change_id) REFERENCES tbl_changes(id),
    UNIQUE (cyclist_id, stat_name, version)
);

-- Export view that joins all tables for comprehensive data analysis
CREATE VIEW vw_tracking_export AS
SELECT 
    c.pcm_id,
    c.name AS cyclist_name,
    c.first_cycling_id,
    ch.name AS change_name,
    ch.description AS change_description,
    ch.author AS change_author,
    ch.date AS change_date,
    csh.stat_name,
    csh.stat_value,
    csh.version AS stat_version
FROM 
    tbl_change_stat_history csh
    INNER JOIN tbl_cyclists c ON csh.cyclist_id = c.id
    INNER JOIN tbl_changes ch ON csh.change_id = ch.id
ORDER BY 
    ch.date desc,
    c.pcm_id, 
    csh.stat_name,
    csh.version;
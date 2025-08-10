CREATE TABLE tbl_cyclists (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pcm_id VARCHAR(255) NOT NULL,
    name VARCHAR(511) NOT NULL,
    first_cycling_id VARCHAR(255),
    UNIQUE (pcm_id)
);

CREATE TABLE tbl_changes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(511) NOT NULL,
    description TEXT NULL,
    author VARCHAR(511) DEFAULT 'Unknown',
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (name)
);

CREATE TABLE tbl_change_stat_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
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
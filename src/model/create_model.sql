CREATE TABLE cyclists (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    pcm_id VARCHAR(255) NOT NULL,
    first_cycling_id VARCHAR(255)
);

CREATE TABLE updates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    author VARCHAR(255) DEFAULT 'Unknown',
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_name VARCHAR(255),
    UNIQUE (name)
);

CREATE TABLE stat_updates_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cyclist_id INT NOT NULL,
    update_id INT NOT NULL,
    stat_name VARCHAR(255) NOT NULL,
    stat_value INT NOT NULL,
    version INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cyclist_id) REFERENCES cyclists(id),
    FOREIGN KEY (update_id) REFERENCES updates(id),
    UNIQUE (cyclist_id, stat_name, version)
);
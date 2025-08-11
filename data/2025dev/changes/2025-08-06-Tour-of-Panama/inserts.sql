-- Generated SQL INSERT statements for 2025-08-06-Tour-of-Panama
-- Review before executing

INSERT INTO tbl_changes (name, description, author, date)
VALUES ('2025-08-06-Tour-of-Panama', 'Tour of Panama 2025 updates', 'PCM Database Team', '2025-08-06');

INSERT INTO tbl_cyclists (pcm_id, name, first_cycling_id)
VALUES ('1', 'F. Archibold', NULL);
INSERT INTO tbl_change_stat_history (cyclist_id, change_id, stat_name, stat_value, version)
VALUES (
    (SELECT id FROM tbl_cyclists WHERE pcm_id = '1'),
    (SELECT id FROM tbl_changes WHERE name = '2025-08-06-Tour-of-Panama'),
    'cob',
    61,
    COALESCE(
        (SELECT MAX(version) + 1 
         FROM tbl_change_stat_history csh 
         JOIN tbl_cyclists c ON csh.cyclist_id = c.id 
         WHERE c.pcm_id = '1' AND csh.stat_name = 'cob'), 
        1
    )
);
INSERT INTO tbl_change_stat_history (cyclist_id, change_id, stat_name, stat_value, version)
VALUES (
    (SELECT id FROM tbl_cyclists WHERE pcm_id = '1'),
    (SELECT id FROM tbl_changes WHERE name = '2025-08-06-Tour-of-Panama'),
    'prl',
    85,
    COALESCE(
        (SELECT MAX(version) + 1 
         FROM tbl_change_stat_history csh 
         JOIN tbl_cyclists c ON csh.cyclist_id = c.id 
         WHERE c.pcm_id = '1' AND csh.stat_name = 'prl'), 
        1
    )
);
INSERT INTO tbl_change_stat_history (cyclist_id, change_id, stat_name, stat_value, version)
VALUES (
    (SELECT id FROM tbl_cyclists WHERE pcm_id = '1'),
    (SELECT id FROM tbl_changes WHERE name = '2025-08-06-Tour-of-Panama'),
    'spr',
    68,
    COALESCE(
        (SELECT MAX(version) + 1 
         FROM tbl_change_stat_history csh 
         JOIN tbl_cyclists c ON csh.cyclist_id = c.id 
         WHERE c.pcm_id = '1' AND csh.stat_name = 'spr'), 
        1
    )
);
INSERT INTO tbl_change_stat_history (cyclist_id, change_id, stat_name, stat_value, version)
VALUES (
    (SELECT id FROM tbl_cyclists WHERE pcm_id = '1'),
    (SELECT id FROM tbl_changes WHERE name = '2025-08-06-Tour-of-Panama'),
    'res',
    65,
    COALESCE(
        (SELECT MAX(version) + 1 
         FROM tbl_change_stat_history csh 
         JOIN tbl_cyclists c ON csh.cyclist_id = c.id 
         WHERE c.pcm_id = '1' AND csh.stat_name = 'res'), 
        1
    )
);
INSERT INTO tbl_change_stat_history (cyclist_id, change_id, stat_name, stat_value, version)
VALUES (
    (SELECT id FROM tbl_cyclists WHERE pcm_id = '1'),
    (SELECT id FROM tbl_changes WHERE name = '2025-08-06-Tour-of-Panama'),
    'rec',
    40,
    COALESCE(
        (SELECT MAX(version) + 1 
         FROM tbl_change_stat_history csh 
         JOIN tbl_cyclists c ON csh.cyclist_id = c.id 
         WHERE c.pcm_id = '1' AND csh.stat_name = 'rec'), 
        1
    )
);
INSERT INTO tbl_change_stat_history (cyclist_id, change_id, stat_name, stat_value, version)
VALUES (
    (SELECT id FROM tbl_cyclists WHERE pcm_id = '1'),
    (SELECT id FROM tbl_changes WHERE name = '2025-08-06-Tour-of-Panama'),
    'hil',
    69,
    COALESCE(
        (SELECT MAX(version) + 1 
         FROM tbl_change_stat_history csh 
         JOIN tbl_cyclists c ON csh.cyclist_id = c.id 
         WHERE c.pcm_id = '1' AND csh.stat_name = 'hil'), 
        1
    )
);
INSERT INTO tbl_change_stat_history (cyclist_id, change_id, stat_name, stat_value, version)
VALUES (
    (SELECT id FROM tbl_cyclists WHERE pcm_id = '1'),
    (SELECT id FROM tbl_changes WHERE name = '2025-08-06-Tour-of-Panama'),
    'att',
    68,
    COALESCE(
        (SELECT MAX(version) + 1 
         FROM tbl_change_stat_history csh 
         JOIN tbl_cyclists c ON csh.cyclist_id = c.id 
         WHERE c.pcm_id = '1' AND csh.stat_name = 'att'), 
        1
    )
);

INSERT INTO tbl_cyclists (pcm_id, name, first_cycling_id)
VALUES ('2', 'G. Rojas Campos', NULL);
INSERT INTO tbl_change_stat_history (cyclist_id, change_id, stat_name, stat_value, version)
VALUES (
    (SELECT id FROM tbl_cyclists WHERE pcm_id = '2'),
    (SELECT id FROM tbl_changes WHERE name = '2025-08-06-Tour-of-Panama'),
    'dh',
    64,
    COALESCE(
        (SELECT MAX(version) + 1 
         FROM tbl_change_stat_history csh 
         JOIN tbl_cyclists c ON csh.cyclist_id = c.id 
         WHERE c.pcm_id = '2' AND csh.stat_name = 'dh'), 
        1
    )
);
INSERT INTO tbl_change_stat_history (cyclist_id, change_id, stat_name, stat_value, version)
VALUES (
    (SELECT id FROM tbl_cyclists WHERE pcm_id = '2'),
    (SELECT id FROM tbl_changes WHERE name = '2025-08-06-Tour-of-Panama'),
    'spr',
    40,
    COALESCE(
        (SELECT MAX(version) + 1 
         FROM tbl_change_stat_history csh 
         JOIN tbl_cyclists c ON csh.cyclist_id = c.id 
         WHERE c.pcm_id = '2' AND csh.stat_name = 'spr'), 
        1
    )
);

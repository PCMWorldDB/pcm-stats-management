-- Generated SQL INSERT statements for 2025-08-06-test
-- Review before executing

-- Step 1: tbl_changes and tbl_cyclists
INSERT INTO tbl_changes (name, description, author, date)
VALUES ('2025-08-06-test', 'run test-B', 'neal', '2025-08-13');

INSERT INTO tbl_cyclists (pcm_id, name, first_cycling_id)
VALUES ('1', 'Axel Froner', NULL);

INSERT INTO tbl_cyclists (pcm_id, name, first_cycling_id)
VALUES ('4', 'Valentin Madouas', NULL);

-- Step 2: tbl_change_stat_history
INSERT INTO tbl_change_stat_history (cyclist_id, change_id, stat_name, stat_value, version)
VALUES (
    (SELECT id FROM tbl_cyclists WHERE pcm_id = '1'),
    (SELECT id FROM tbl_changes WHERE name = '2025-08-06-test'),
    'cob',
    30,
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
    (SELECT id FROM tbl_changes WHERE name = '2025-08-06-test'),
    'prl',
    30,
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
    (SELECT id FROM tbl_cyclists WHERE pcm_id = '4'),
    (SELECT id FROM tbl_changes WHERE name = '2025-08-06-test'),
    'dh',
    30,
    COALESCE(
        (SELECT MAX(version) + 1 
         FROM tbl_change_stat_history csh 
         JOIN tbl_cyclists c ON csh.cyclist_id = c.id 
         WHERE c.pcm_id = '4' AND csh.stat_name = 'dh'), 
        1
    )
);
INSERT INTO tbl_change_stat_history (cyclist_id, change_id, stat_name, stat_value, version)
VALUES (
    (SELECT id FROM tbl_cyclists WHERE pcm_id = '4'),
    (SELECT id FROM tbl_changes WHERE name = '2025-08-06-test'),
    'spr',
    30,
    COALESCE(
        (SELECT MAX(version) + 1 
         FROM tbl_change_stat_history csh 
         JOIN tbl_cyclists c ON csh.cyclist_id = c.id 
         WHERE c.pcm_id = '4' AND csh.stat_name = 'spr'), 
        1
    )
);

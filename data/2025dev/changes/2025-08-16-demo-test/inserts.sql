-- Generated SQL INSERT statements for 2025-08-16-demo-test
-- Review before executing

-- Step 1: tbl_changes and tbl_cyclists
INSERT INTO tbl_changes (name, description, author, date)
VALUES ('2025-08-16-demo-test', 'demo test', 'neal', '2025-08-15');

INSERT INTO tbl_cyclists (pcm_id, name, first_cycling_id)
VALUES ('301', 'Chris Froome', NULL);

-- Step 2: tbl_change_stat_history
INSERT INTO tbl_change_stat_history (cyclist_id, change_id, stat_name, stat_value, version)
VALUES (
    (SELECT id FROM tbl_cyclists WHERE pcm_id = '301'),
    (SELECT id FROM tbl_changes WHERE name = '2025-08-16-demo-test'),
    'mm',
    45,
    COALESCE(
        (SELECT MAX(version) + 1 
         FROM tbl_change_stat_history csh 
         JOIN tbl_cyclists c ON csh.cyclist_id = c.id 
         WHERE c.pcm_id = '301' AND csh.stat_name = 'mm'), 
        1
    )
);
INSERT INTO tbl_change_stat_history (cyclist_id, change_id, stat_name, stat_value, version)
VALUES (
    (SELECT id FROM tbl_cyclists WHERE pcm_id = '301'),
    (SELECT id FROM tbl_changes WHERE name = '2025-08-16-demo-test'),
    'cob',
    90,
    COALESCE(
        (SELECT MAX(version) + 1 
         FROM tbl_change_stat_history csh 
         JOIN tbl_cyclists c ON csh.cyclist_id = c.id 
         WHERE c.pcm_id = '301' AND csh.stat_name = 'cob'), 
        1
    )
);
INSERT INTO tbl_change_stat_history (cyclist_id, change_id, stat_name, stat_value, version)
VALUES (
    (SELECT id FROM tbl_cyclists WHERE pcm_id = '301'),
    (SELECT id FROM tbl_changes WHERE name = '2025-08-16-demo-test'),
    'prl',
    90,
    COALESCE(
        (SELECT MAX(version) + 1 
         FROM tbl_change_stat_history csh 
         JOIN tbl_cyclists c ON csh.cyclist_id = c.id 
         WHERE c.pcm_id = '301' AND csh.stat_name = 'prl'), 
        1
    )
);

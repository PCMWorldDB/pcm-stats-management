-- Generated SQL INSERT statements for 2025-08-06-test
-- Review before executing

INSERT INTO tbl_changes (name, description, author, date)
VALUES ('2025-08-06-test', 'test update', 'neal', '2025-08-06');

INSERT INTO tbl_cyclists (pcm_id, name, first_cycling_id)
VALUES ('1', 'Axel Froner', NULL);
INSERT INTO tbl_change_stat_history (cyclist_id, change_id, stat_name, stat_value, version)
VALUES (
    (SELECT id FROM tbl_cyclists WHERE pcm_id = '1'),
    (SELECT id FROM tbl_changes WHERE name = '2025-08-06-test'),
    'cob',
    78,
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
    78,
    COALESCE(
        (SELECT MAX(version) + 1 
         FROM tbl_change_stat_history csh 
         JOIN tbl_cyclists c ON csh.cyclist_id = c.id 
         WHERE c.pcm_id = '1' AND csh.stat_name = 'prl'), 
        1
    )
);

INSERT INTO tbl_cyclists (pcm_id, name, first_cycling_id)
VALUES ('4', 'Valentin Madouas', NULL);
INSERT INTO tbl_change_stat_history (cyclist_id, change_id, stat_name, stat_value, version)
VALUES (
    (SELECT id FROM tbl_cyclists WHERE pcm_id = '4'),
    (SELECT id FROM tbl_changes WHERE name = '2025-08-06-test'),
    'dh',
    78,
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
    78,
    COALESCE(
        (SELECT MAX(version) + 1 
         FROM tbl_change_stat_history csh 
         JOIN tbl_cyclists c ON csh.cyclist_id = c.id 
         WHERE c.pcm_id = '4' AND csh.stat_name = 'spr'), 
        1
    )
);

-- List of columns contains at least one not null value
SET group_concat_max_len = 4294967295; -- to overcome default 1KB limitation

SELECT CONCAT(
         'SELECT * FROM ('
       ,  GROUP_CONCAT(
            CONCAT(
              'SELECT ', QUOTE(TABLE_NAME), ' AS `table`,',
              QUOTE(COLUMN_NAME), ' AS `column`, ',
              QUOTE(COLUMN_TYPE), ' AS `type`, ',
              'COUNT(NULLIF(`', REPLACE(COLUMN_NAME, '`', '``'), '`, "")) AS `not_null_rows` ',
              'FROM `', REPLACE(TABLE_NAME, '`', '``'), '`'
            )
            SEPARATOR ' UNION ALL '
         )
       , ') t WHERE `not_null_rows` > 0'
       )
INTO   @sql
FROM   INFORMATION_SCHEMA.COLUMNS
WHERE  TABLE_SCHEMA = DATABASE();

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;


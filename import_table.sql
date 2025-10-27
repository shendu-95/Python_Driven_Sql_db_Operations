-- COPY suppliers
-- FROM 'D:\SQL_OPs_PY_DRIVEN\Data\suppliers.csv'
-- WITH(FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'UTF8');

COPY suppliers
FROM 'D:\SQL_OPs_PY_DRIVEN\Data\products.csv'
WITH(FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'UTF8');



Select * from products;
SELECT * from reorders;
Select * from shipments;
select * from stock_entries;
select * from suppliers;


-- 1 Total Suppliers:
select count(*) as total_suppliers from suppliers;

-- 2 Total Products:
select count(*) as total_products from products;

-- 3 Total Categories dealing:
select count(DISTINCT category) as total_categories from products;

-- 4 Total Sales value made in last 3 month (stock_quantity * price)
select round(sum(abs(se.change_quantity * pe.price)),2) as "Sales by last 3 Months"
from products as pe 
left join stock_entries se 
on pe.product_id = se.product_id
where se.change_type like "Sale"
and
se.entry_date >= 
(
select date_sub(max(se.entry_date),interval 3 month)
from stock_entries
);

-- 5 Total Restocks Value (Last 3 Months)
select round(sum(abs(se.change_quantity * pe.price)),2) as "Restock Value by last 3 Months"
from products as pe 
left join stock_entries se 
on pe.product_id = se.product_id
where se.change_type = 'Restock'
and
se.entry_date >= 
(
select date_sub(max(se.entry_date),interval 3 month)
from stock_entries
);

-- 6 Below Reorder and no Pending Reorders
select count(distinct product_id)
from products
where stock_quantity < reorder_level
and 
product_id not in
(select distinct product_id from reorders where status = 'Pending' 
);

-- 7 Suppliers and their Contact Details
Select supplier_name, contact_name, email, phone from suppliers;

-- 8 Product with their suppliers and current stock
select p.product_name, s.supplier_name, p.stock_quantity, p.reorder_level from products as p
left join suppliers as s on
p.supplier_id = s.supplier_id 
order by p.product_name ASC;

-- 9 Product needing reorder
select product_id, product_name, stock_quantity, reorder_level 
from products 
where stock_quantity < reorder_level;


-- 10 Add New product in the Database
DELIMITER $$
create procedure AddNewProductManualID(
    in p_name varchar(255),
    in p_category varchar(100),
    in p_price decimal(10, 2),
    in p_stock int,
    in p_reorder int, 
    in p_supplier int
    )
Begin 
 declare new_prod_id INT;
 
 start transaction;
 
 # make changes in product table
 insert into products(product_name, category, price, stock_quantity, reorder_level, supplier_id)
 values(p_name, p_category, p_price, p_stock, p_reorder, p_supplier);
 
 SET new_prod_id = LAST_INSERT_ID();
 
 # make changes in shipment table
insert into shipments(product_id, supplier_id, quantity_received, shipment_date)
values(new_prod_id, p_supplier , p_stock, curdate());


# Making changes in Stock_entries
insert into stock_entries( product_id, change_quantity, change_type, entry_date)
values(new_prod_id, p_stock, 'Restock', curdate());
commit;

end $$
DELIMITER ;


-- 11 Product History
create or replace view product_inventory_history as
with pih as(
select product_id, 
"Shipment" as record_type,
shipment_date as record_date, 
quantity_received as quantity,
null change_type
from shipments
UNION ALL 
select 
product_id, 
"Stock Entry" as record_type,
entry_date as record_date,
change_quantity as quantity,
change_type
from stock_entries
)
select 
pih.product_id,  
pih.record_type,
pih.record_date,
pih.quantity,
pih.change_type,
p.supplier_id
from pih 
join products p on 
pih.product_id = p.product_id;


select* from product_inventory_history
where product_id = 123
order by record_date desc;
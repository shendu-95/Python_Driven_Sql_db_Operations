-- Create 'suppliers' first since 'products' references it
CREATE TABLE IF NOT EXISTS PUBLIC.suppliers
(
    supplier_id INT PRIMARY KEY,
    supplier_name VARCHAR(100),
    contact_name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(100),
    address VARCHAR(255)
);

-- Create 'products' next, as it references 'suppliers'
CREATE TABLE IF NOT EXISTS PUBLIC.products
( 
    product_id INT PRIMARY KEY,
    product_name VARCHAR(255),
    category VARCHAR(100),
    price NUMERIC(10, 2),  -- Specified precision and scale
    stock_quantity INT,
    reorder_level INT,
    supplier_id INT,
    FOREIGN KEY(supplier_id) REFERENCES public.suppliers (supplier_id)
);

-- The remaining tables reference 'products' or 'suppliers'
CREATE TABLE IF NOT EXISTS PUBLIC.reorders
( 
    reorder_id INT PRIMARY KEY,
    product_id INT,
    reorder_quantity INT,
    reorder_date DATE,
    reorder_status VARCHAR(50),  -- Renamed 'status' and used VARCHAR
    FOREIGN KEY(product_id) REFERENCES public.products (product_id)
);

CREATE TABLE IF NOT EXISTS PUBLIC.shipments
(
    shipment_id INT PRIMARY KEY,
    product_id INT,
    supplier_id INT,
    quantity_received INT,
    shipment_date DATE,
    FOREIGN KEY(product_id) REFERENCES public.products (product_id),
    FOREIGN KEY(supplier_id) REFERENCES public.suppliers (supplier_id)
);

CREATE TABLE IF NOT EXISTS PUBLIC.stock_entries
(
    entry_id INT PRIMARY KEY,
    product_id INT,
    change_quantity NUMERIC,
    change_type VARCHAR(50), -- Changed from TEXT
    entry_date DATE,
    FOREIGN KEY(product_id) REFERENCES public.products (product_id)
);
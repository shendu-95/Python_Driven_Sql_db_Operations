import mysql.connector 

def connect_to_db():
    return mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "admin@1995",
    database = "dummy_project"
)

def get_basics_info(cursor):
    queries = {
        "Total Suppliers": "SELECT COUNT(*) AS count FROM suppliers",

        "Total Products": "SELECT COUNT(*) AS count FROM products",

        "Total Categories Dealing": "SELECT COUNT(DISTINCT category) AS count FROM products",

        "Total Sale Value (Last 3 Months)": """
        SELECT ROUND(SUM(ABS(se.change_quantity) * p.price), 2) AS total_sale
        FROM stock_entries se
        JOIN products p ON se.product_id = p.product_id
        WHERE se.change_type = 'Sale'
        AND se.entry_date >= (
        SELECT DATE_SUB(MAX(se.entry_date), INTERVAL 3 MONTH) FROM stock_entries)
        """,

        "Total Restock Value (Last 3 Months)": """
        SELECT ROUND(SUM(se.change_quantity * p.price), 2) AS total_restock
        FROM stock_entries se
        JOIN products p ON se.product_id = p.product_id
        WHERE se.change_type = 'Restock'
        AND se.entry_date >= (
        SELECT DATE_SUB(MAX(se.entry_date), INTERVAL 3 MONTH) FROM stock_entries)
        """,

        "Below Reorder & No Pending Reorders": """
        SELECT COUNT(*) AS below_reorder
        FROM products 
        WHERE stock_quantity < reorder_level
        AND product_id NOT IN (
        SELECT DISTINCT product_id FROM reorders WHERE status = 'Pending')
        """
    }
    
    result = {}
    for label, query in queries.items():
       cursor.execute(query)
       row = cursor.fetchone()
       result[label]=list(row.values())[0]
    return result


def get_additional_tables(cursor):
    queries = {
        "Suppliers Contact Details": "SELECT supplier_name, contact_name, email, phone FROM suppliers",

        "Products with Supplier and Stock": """
            SELECT 
                p.product_name,
                s.supplier_name,
                p.stock_quantity,
                p.reorder_level
            FROM products p
            JOIN suppliers s ON p.supplier_id = s.supplier_id
            ORDER BY p.product_name ASC
        """,

        "Products Needing Reorder": """
            SELECT product_name, stock_quantity, reorder_level
            FROM products
            WHERE stock_quantity <= reorder_level
        """
    }

    tables={}
    for label, query in queries.items():
       cursor.execute(query)
       tables[label]=cursor.fetchall()
    return tables

def add_new_manual_id(cursor, db, p_name, p_category, p_price, p_stock, p_reorder, p_supplier):
    proc_call = "call AddNewProductManualID(%s, %s, %s, %s, %s, %s)"
    params = (p_name, p_category, p_price, p_stock, p_reorder, p_supplier)
    cursor.execute(proc_call, params)
    db.commit

def get_categories(cursor):
    cursor.execute("Select Distinct category from products order by category asc")
    rows = cursor.fetchall()
    category_list = [row['category'] for row in rows]
    return category_list

def get_suppliers(cursor):
    cursor.execute("select supplier_id, supplier_name from suppliers order by supplier_name asc")
    return cursor.fetchall()

def product_inventory_history(cursor, product_id):
    q = "select* from product_inventory_history where product_id = %s order by record_date desc"
    cursor.execute(q, (product_id,))
    return cursor.fetchall()

def get_all_product(cursor):
    cursor.execute("select product_id, product_name from products order by product_name ")
    return cursor.fetchall()

def place_reorder(cursor, db, product_id, reorder_quantity):
    q = """
    Insert into reorders
    (product_id, reorder_quantity, reorder_date, status)
    values(%s, %s, curdate(),%s)
    """
    cursor.execute(q, (product_id, reorder_quantity, "ordered"))
    db.commit()


def get_pending_reorders(cursor):
    cursor.execute("""
    select r.reorder_id , p.product_name
    from reorders as r join products as p 
    on r.product_id= p.product_id
    """)
    return cursor.fetchall()

def mark_reorder_as_received(cursor, db, reorder_id):
    cursor.callproc("MakeReorderAsReceived",[reorder_id])
    db.commit()




    
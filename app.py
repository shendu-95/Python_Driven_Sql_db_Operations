import streamlit as st
import pandas as pd
import numpy as np
from db_functions import(
    connect_to_db,
    get_basics_info,
    get_additional_tables,
    get_categories,
    get_suppliers,
    add_new_manual_id,
    product_inventory_history,
    get_all_product,
    place_reorder,
    get_pending_reorders,
    mark_reorder_as_received
)

# sidebar
st.sidebar.title("Inventory Management Dashboard")
option = st.sidebar.radio("Select Option:",["Basic Information", "Operational Tasks"])

# main space

st.title("Inventory and Supply chain Dashboard")

db = connect_to_db()
cursor = db.cursor(dictionary = True)

# ---------- BASIC INFO PAGE-------------
if option == "Basic Information":
    st.header("Basic Metrics")

    # get basic info from Database
    basic_info = get_basics_info(cursor)

    cols = st.columns(3)
    keys = list(basic_info.keys())

    for i in range(3):
        cols[i].metric(label = keys[i], value=basic_info[keys[i]])

    
    cols = st.columns(3)
    for i in range(3,6):
        cols[i-3].metric(label = keys[i], value=basic_info[keys[i]])

    st.divider()
    
    # fetch and display detailed tables
    tables = get_additional_tables(cursor)
    for labels, data in tables.items():
        st.header(labels)
        df = pd.DataFrame(data)
        st.dataframe(df)
        st.divider()

elif option =="Operational Tasks":
     st.header("Operational Tasks")
     selected_task = st.selectbox("Choose a Task", ["Add New Product","Product History","Place reorder","Receive Reorder"])
     if selected_task == "Add New Product":
         st.header("Add New Product")
         categories = get_categories(cursor)
         suppliers = get_suppliers(cursor)
    
    #--------Add Product-------------- 
         
         with st.form("Add Product Form"):
             product_name=st.text_input("Product Name")
             product_category = st.selectbox("Category", categories)
             product_price = st.number_input("Price", min_value= 0.00)
             product_stock = st.number_input("Stock Quantity", min_value=0, step= 1)
             product_level = st.number_input("Reorder Level", min_value= 0, step = 1)
             
             supplier_ids =[s["supplier_id"] for s in suppliers] 
             supplier_names = [s["supplier_name"] for s in suppliers]
             supplier_id = st.selectbox(
                 "Suppliers",
                 options= supplier_ids,
                 format_func=lambda x: supplier_names[supplier_ids.index(x)]
             )
             submitted = st.form_submit_button("Add Product")

             if submitted:
                 if not product_name:
                     st.error("Please enter the product name")
                 else:
                     try: 
                         add_new_manual_id(cursor, 
                                           db, 
                                           product_name,
                                           product_category,
                                           product_price, 
                                           product_stock,
                                           product_level,
                                           supplier_id)
                         st.success(f"Product {product_name} added successfully!")
                     except Exception as e:
                         st.error(f"Error adding the product {e}")
     #--------Product History------------
     
     if selected_task == "Product History":
         st.header("Product Inventory History")

         products = get_all_product(cursor)
         product_names = [p['product_name'] for p in products]
         product_ids = [p['product_id'] for p in products]

         selected_product_name = st.selectbox("Select a Product", options= product_names)
         
         if selected_product_name:
             selected_product_id = product_ids[product_names.index(selected_product_name)]
             history_data = product_inventory_history(cursor, selected_product_id)

             if history_data:
                 df = pd.DataFrame(history_data)
                 st.dataframe(df)
             else:
                 st.info("No history found for the Product selected")
     
     # -------Placing Order ----------------

     if selected_task == "Place reorder":
         st.header("Placing Order")

         products = get_all_product(cursor)
         product_names = [p['product_name'] for p in products]
         product_ids = [p['product_id'] for p in products]

         selected_product_name = st.selectbox("Select a Product", options= product_names)
         reorder_qty = st.number_input("Reorder Quantity:", min_value= 1, step=1)

         
         if st.button("Place Reorder"):
             if not selected_product_name:
                 st.error("please Select an Product")
             elif reorder_qty<=0:
                 st.error("Reorder Quantity must be greater than 0")
             else:
                 selected_product_id = product_ids[product_names.index(selected_product_name)]
                 try:
                     place_reorder(cursor, db, selected_product_id, reorder_qty)
                     st.success(f"Order placed for {selected_product_name} with quantity{reorder_qty}")
                 except Exception as e:
                     st.error(f"Error placing reorder {e} ")
             
         #----------------RECEIVING AN ORDER ------------------

     elif selected_task=="Receive Reorder":
             st.header("Mark Reorder as Received")
             # Fetch orders in Ordered Stage
             pending_reorders= get_pending_reorders(cursor)
             if not pending_reorders:
                st.info("No Pending Orders to Receive.")
             else:
                 reorder_ids = [r['reorder_id'] for r in pending_reorders]
                 reorder_labels=[f"ID {r['reorder_id']} - {r['product_name']}" for r in  pending_reorders]

                 selected_label =st.selectbox("Select Reorder to mark As Received", options=reorder_labels)

                 if selected_label:
                     selected_reorder_id= reorder_ids[reorder_labels.index(selected_label)]

                     if st.button("Mark as Received"):
                         try:
                             mark_reorder_as_received(cursor, db  , selected_reorder_id)
                             st.success(f"Reorder ID {selected_reorder_id} marked as received")
                         except Exception as e:
                             st.error(f"Erroe {e}")        

         
         




                         


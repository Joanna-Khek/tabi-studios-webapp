import os
import time
import streamlit as st
import pandas as pd
from src import ui
from src import database
from src import utils
from src import validations
from src import send_email

st.title("Invoice")


if 'invoice_num' not in st.session_state:
    st.session_state.invoice_num = utils.get_reference_num(mode='invoice')

current_num = utils.get_reference_num(mode='invoice')

# 1. Invoice Number
st.subheader("Edit Invoice Number")
col1, col2, col3, col4 = st.columns([0.4, 0.2, 0.2, 0.2])
col1.markdown(f"Current number: <span style='color: red;'>{current_num}</span>",
            unsafe_allow_html=True)

col2.button("Add", on_click=utils.update_reference_num, 
            kwargs=dict(mode='invoice',
                        current_num=current_num,
                        operation='add'))
    
col3.button("Subtract", on_click=utils.update_reference_num, 
            kwargs=dict(mode='invoice',
                        current_num=current_num,
                        operation='subtract'))

col4.empty()

invoice_num = utils.format_ref_num(mode='invoice')

# 2. Grab quotation info from database and populate the form
engine = database.create_connection()
df_project = pd.read_sql_query("SELECT * FROM project_details", engine)
df_project_items = pd.read_sql_query("SELECT * FROM quotation_items", engine)

st.subheader("Select Quotation")
quotation_num = st.selectbox(label="Quotation Number", 
                             options=list(df_project.quotation_num.sort_values().unique()))

project_info = df_project.query(f"quotation_num == '{quotation_num}'")
project_items = df_project_items.query(f"quotation_num == '{quotation_num}'")

# 3. Check if invoice has been issued
validations.validate_invoice_issue(project_info)

# 4. Project Information Details
st.subheader("Project Information")
dict_project_info = ui.display_project_info_inputs(reference=True,
                                                   disabled_status=False,
                                                   project_info=project_info)

project_name = dict_project_info['project_name']
project_type = dict_project_info['project_type']
client_contact_person = dict_project_info['client_contact_person']
client_company_name = dict_project_info['client_company_name']
client_uen = dict_project_info['client_uen']
client_email = dict_project_info['client_email']
client_address = dict_project_info['client_address']
project_start_date = dict_project_info['project_start_date']
project_end_date = dict_project_info['project_end_date']
expiration_date = dict_project_info['expiration_date']
date_invoice = dict_project_info['date']

file_name=f"{invoice_num}_({project_name}).pdf"
file_path = f"data/{file_name}"

st.subheader("Details")
list_item, list_quantity, list_rate, list_amount, total_quotation_price = ui.display_project_details(mode='invoice',
                                                                                                     project_items=project_items)

# Save to dataframe
df_items = utils.item_save_to_dataframe(list_item, list_quantity, list_rate, list_amount)
total_invoice_price = total_quotation_price

# 4. Payment Information
st.subheader("Payment Due Date")
if st.toggle("Half Payment"):
    # Add to database
    database.add_task(engine, "half_payment_projects", quotation_num)

    # Add items to list of items
    df_half_payment_items = pd.DataFrame.from_dict({'Item': '(Invoice for 50%)',
                                                    'Quantity': '',
                                                    'Rate': '',
                                                    'Amount': ''}, orient='index').T
    payment_factor = 0.5
    half_payment = 1

else:
    df_half_payment_items = pd.DataFrame.from_dict({'Item': '(Invoice for 100%)',
                                                    'Quantity': '',
                                                    'Rate': '',
                                                    'Amount': ''}, orient='index').T
    payment_factor = 1
    half_payment = 0

payment_due_date = st.date_input("Payment Due Date")
payment_term = st.text_input(label="Payment Term")
adjusted_invoice_price = utils.calculate_total_price(total_invoice_price, payment_factor)
total_invoice_price = utils.format_total_price(total_invoice_price)

st.markdown(f"Total Price: <span style='color:#ff6854;'>${total_invoice_price}</span>", 
                unsafe_allow_html=True)
st.markdown(f"Half Payment Price: <span style='color:#ff6854;'>${adjusted_invoice_price}</span>", 
                unsafe_allow_html=True)

if st.button("Validate Reference Number"):
    validations.validate_ref_num(mode='invoice', ref_num=invoice_num)

if st.button("Generate Invoice"):
    with st.status("Generating Invoice...", expanded=True):
        pdf_local, pdf_remote = utils.generate_quotation_invoice(mode='invoice',
                                                                file_name=file_name,
                                                                project_name=project_name,
                                                                client_contact_person=client_contact_person,
                                                                client_company_name=client_company_name,
                                                                client_address=client_address,
                                                                client_email=client_email,
                                                                reference_num=invoice_num,
                                                                half_payment=half_payment,
                                                                quote_type=None,
                                                                df_half_payment_items=df_half_payment_items,
                                                                df_items=df_items,
                                                                total_price=total_invoice_price,
                                                                adjusted_price=adjusted_invoice_price,
                                                                payment_due_date=payment_due_date,
                                                                expiration_date=None,
                                                                credit_term=None,
                                                                payment_term=payment_term,
                                                                date = date_invoice)
        
        # Preview Invoice
        st.download_button(
            label="Preview Invoice",
            data=pdf_remote,
            file_name=file_name,
            mime="application/octet-stream")
            
        st.success(f"Invoice Generated for {file_name}")

if st.button("Save to database"):
    with st.status("Saving invoice information to cloud database...", expanded=True):
        database.save_invoice_details(engine, project_info, df_items, quotation_num,
                                    invoice_num, project_name, half_payment, total_invoice_price,
                                    adjusted_invoice_price)
        
        st.write("Uploading to google drive...")
        utils.upload_file(file_name, file_path)

        st.write("Removing file from local folder...")
        os.remove(f"data/{file_name}")

        st.success("Saved!")

if st.button("Send Email"):
            
    with st.status("Sending email...", expanded=True):

        
        # Download file
        st.write("Downloading PDF from google drive...")
        utils.download_file(file_name)
        time.sleep(2)
        st.write("Attaching PDF to email...")
        send_email.send_email(mode='invoice',
                            client_email=client_email, 
                            client_contact_person=client_contact_person, 
                            project_name=project_name, 
                            file_name=file_name)
        st.write("Removing file from local folder...")
        os.remove(f"data/{file_name}")
        
        st.success("Email Successfully Sent!")
        st.cache_data.clear()


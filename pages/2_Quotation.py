import os
import numpy as np
import pandas as pd
import time
import streamlit as st
from src import ui
from src import validations
from src import send_email
from src import utils
from src import database

st.title("Quotation")

if 'quotation_num' not in st.session_state:
    st.session_state.quotation_num = utils.get_reference_num(mode='quotation')

current_num = utils.get_reference_num(mode='quotation')

# 1. Quotation Number
st.subheader("Edit Quotation Number")
col1, col2, col3, col4 = st.columns([0.4, 0.2, 0.2, 0.2])

col1.markdown(f"Current number: <span style='color: red;'>{current_num}</span>",
            unsafe_allow_html=True)

col2.button("Add", on_click=utils.update_reference_num, 
            kwargs=dict(mode='quotation',
                        current_num=current_num,
                        operation='add'))
    
col3.button("Subtract", on_click=utils.update_reference_num, 
            kwargs=dict(mode='quotation',
                        current_num=current_num,
                        operation='subtract'))

col4.empty()

if st.toggle("Variation Order"):
    quote_type = 'Variation'
else:
    quote_type = 'Normal'
    
if st.toggle("Refer to quotation"):
    engine = database.create_connection()
    df_project = pd.read_sql_query("SELECT * FROM project_details", engine)
    df_project_items = pd.read_sql_query("SELECT * FROM quotation_items", engine)

    selected_quotation_number = st.selectbox("Quotation Number",
                                             options=list(df_project.quotation_num.sort_values().unique()))
    
    project_info = df_project.query(f"quotation_num == '{selected_quotation_number}'")
    project_items = df_project_items.query(f"quotation_num == '{selected_quotation_number}'")

    st.subheader("Project Information")
    dict_project_info = ui.display_project_info_inputs(reference=True, 
                                                       disabled_status=False,
                                                       project_info=project_info,
                                                       ) 
else:

    st.subheader("Project Information")
    dict_project_info = ui.display_project_info_inputs(reference=False,
                                                       disabled_status=False
                                                       )


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
credit_term = dict_project_info['credit_term']
date_quotation = dict_project_info['date']

st.subheader("Payment Type")
if st.toggle("Half Payment"):
    half_payment = 1
else:
    half_payment = 0

st.subheader('Details')
list_item, list_quantity, list_rate, list_amount, total_quotation_price = ui.display_project_details(mode='quotation')

# Save to dataframe
df_items = utils.item_save_to_dataframe(list_item, list_quantity, list_rate, list_amount)
total_quotation_price = np.where(len(str(total_quotation_price).split(".")[1]) == 1,
                                            str(total_quotation_price) + '0', 
                                            total_quotation_price)

st.markdown(f"Total Price: <span style='color:#ff6854;'>${total_quotation_price}</span>", 
            unsafe_allow_html=True)

quotation_num = utils.format_ref_num(mode='quotation')
file_name=f"{quotation_num}_({project_name}).pdf".replace(" ", "_")
file_path = f"data/{file_name}"

if st.button("Validate Reference Number"):
    validations.validate_ref_num(mode='quotation', ref_num=quotation_num)

if st.button("Generate Quotation"):
    with st.status("Generating Quotation...", expanded=True):
        pdf_local, pdf_remote = utils.generate_quotation_invoice(mode='quotation',
                                                                 file_name=file_name,
                                                                 project_name=project_name,
                                                                 client_contact_person=client_contact_person,
                                                                 client_company_name=client_company_name,
                                                                 client_address=client_address,
                                                                 client_email=client_email,
                                                                 reference_num=quotation_num,
                                                                 half_payment=half_payment,
                                                                 quote_type=quote_type,
                                                                 df_half_payment_items=None,
                                                                 df_items=df_items,
                                                                 total_price=total_quotation_price,
                                                                 adjusted_price=None,
                                                                 payment_due_date=None,
                                                                 expiration_date=expiration_date,
                                                                 credit_term=credit_term,
                                                                 payment_term=None,
                                                                 date = date_quotation
                                                                 )
        
    
        # Preview Invoice
        st.download_button(
            label="Preview Quotation",
            data=pdf_remote,
            file_name=file_name,
            mime="application/octet-stream")
        
        
        st.success(f"Quotation Generated for {file_name}")

if st.button("Save to database"):
    with st.status("Saving quotation to database...", expanded=True):

        database.save_project_details(quotation_num=quotation_num,
                                    project_name=project_name, 
                                    project_type=project_type,
                                    client_contact_person=client_contact_person,
                                    client_company_name=client_company_name, 
                                    client_uen=client_uen, 
                                    client_email=client_email, 
                                    client_address=client_address,
                                    project_start_date=project_start_date, 
                                    project_end_date=project_end_date, 
                                    total_quotation_price=total_quotation_price,
                                    quotation_expiry_date=expiration_date,
                                    credit_term=credit_term,
                                    df_items=df_items)
        
        st.write("Uploading to google drive...")
        utils.upload_file(file_name, file_path)

        st.write("Removing file from local folder...")
        os.remove(f"data/{file_name}")

        st.success("Saved!")

if st.button("Send Email"):
    
    with st.status("Sending email...", expanded=True):
        
        # st.write("Uploading to google drive...")
        # utils.upload_file(file_name, file_path)

        # st.write("Removing file from local folder...")
        # os.remove(f"data/{file_name}")
        
        # Download file
        st.write("Downloading PDF from google drive...")
        utils.download_file(file_name)
        time.sleep(2)
        st.write("Attaching PDF to email...")
        send_email.send_email(mode='quotation',
                            client_email=client_email, 
                            client_contact_person=client_contact_person, 
                            project_name=project_name, 
                            file_name=file_name)

        st.success("Email Successfully Sent!")
        st.cache_data.clear()







            


from datetime import datetime
import streamlit as st
import pandas as pd
import numpy as np
import time
from src import database

st.title("Status Update")
st.info("Update job confirmation and payment received date")

st.subheader("Search for Project")

engine = database.create_connection()
df = pd.read_sql_query("SELECT * FROM project_details", engine)
search_by = st.radio("Search by", ["Quotation Number", "Project Name"])

if search_by == 'Quotation Number':
    quotation_num_selection = st.selectbox(label='Quotation Number',
                                       options=list(df.quotation_num.sort_values().unique()))
    output = (df
          .query(f"quotation_num == '{quotation_num_selection}'")
          .loc[:,['quotation_num', 'project_name', 'client_contact_person',
                  'client_company_name', 'quotation_price', 'quotation_sent_date', 
                  'job_confirm_date', 'invoice_price', 'invoice_num', 
                  'invoice_sent_date', 'payment_received_date']]
          .assign(job_confirm_date=lambda df_: pd.to_datetime(df_.job_confirm_date),
                  payment_received_date=lambda df_: pd.to_datetime(df_.payment_received_date))
    )
    st.dataframe(output, hide_index=True)

elif search_by == 'Project Name':
    project_name_selection = st.selectbox(label="Project Name",
                                          options=list(df.project_name.sort_values().unique()))
    output = (df
          .query(f"project_name == '{project_name_selection}'")
          .loc[:,['quotation_num', 'project_name', 'client_contact_person',
                  'client_company_name', 'quotation_price', 'quotation_sent_date', 
                  'job_confirm_date', 'invoice_price', 'invoice_num', 
                  'invoice_sent_date', 'payment_received_date']]
          .assign(job_confirm_date=lambda df_: pd.to_datetime(df_.job_confirm_date),
                  payment_received_date=lambda df_: pd.to_datetime(df_.payment_received_date))
    )
    st.dataframe(output, hide_index=True)


# 1. Void Quotation
if st.button("Void Quotation"):
    database.delete_task(engine=engine,
                         table="project_details",
                         value=quotation_num_selection)

    database.delete_task(engine=engine,
                         table="quotation_items",
                         value=quotation_num_selection)
    
    st.success("Removed Quotation")


col1, col2 = st.columns(2)

# 2. Accept Job
with col1:
    st.subheader("Confirm Job")
    accepted_job_button = False if pd.isnull(output.job_confirm_date.values[0]) else True
    if accepted_job_button:
        st.warning("Job already accepted for this project. You can still change the date if you wish to.")

    job_date = st.date_input("Confirm Job Date")
    if st.button("Confirm Job"):
        database.update_task(engine=engine,
                            table='project_details',
                            column='job_confirm_date',
                            ref_column='quotation_num',
                            task=[job_date, quotation_num_selection])
        st.success("Saved! Refresh to see changes.")
        time.sleep(1)

# 3. Payment made
with col2:
    st.subheader("Payment Received")
    received_button = False if output.payment_received_date.isnull().any() else True
    if received_button:
        st.warning("Payment already received for this project. You can still change the date if you wish to.")

    payment_date = st.date_input("Payment Date")
    invoice_num_selection = st.selectbox(label='Invoice Number',
                                            options=list(output.invoice_num.sort_values().unique()))
    
    if st.button(label="Received Payment"):
        database.update_task(engine=engine,
                            table='project_details',
                            column='payment_received_date',
                            ref_column='invoice_num',
                            task=[payment_date, invoice_num_selection])
        st.success("Saved! Refresh to see changes.")
        time.sleep(1)

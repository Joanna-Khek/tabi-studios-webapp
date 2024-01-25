import pandas as pd
import sqlite3
import streamlit as st
from typing import Literal
from src import database

options = {'project_type': ('Socials', 'Corporate', 'Event Coverage', 'Wedding', 'Property', 'Others'),
           'package_hours': ('2 Hours', '5 Hours', '10 Hours')}

price = {'2 Hours': 280,
         '5 Hours': 600,
         '10 Hours': 1000}

def validate_ref_num(mode: Literal['quotation', 'invoice'],
                     ref_num: str):
    conn = database.create_connection()
    db = pd.read_sql_query("SELECT * FROM project_details", conn)

    if mode == 'quotation':
        if db.quotation_num.str.contains(ref_num).sum() >= 1:
            st.error("Reference number already in database. Please update the reference number")
        else:
            st.success("Valid Reference Number!")
    elif mode == 'invoice':
        if db.invoice_num.str.contains(ref_num).sum() >= 1:
            st.error("Reference number already in database. Please update the reference number")
        else:
            st.success("Valid Reference Number!")
    

def validate_invoice_issue(project_info: pd.DataFrame) -> None:
    """Check if invoice has already been issues for this quotation number.
       If invoice num is not blank, means it has been issued before.
       Check if it is half payment invoice. If it is, then allow user to issue another.

    Args:
        project_info (pd.DataFrame): dataframe for selected quotation number project
    """
    if project_info.invoice_num.values[0] != '':
        sum_half_payment = (project_info
                            .invoice_half_payment
                            .astype(int)
                            .sum())

        if sum_half_payment == 2 or sum_half_payment == 0:
            st.error("Invoice already issued for this quotation number")
        
        if sum_half_payment == 1:
            st.info(f"This is a half-payment quotation. Number issued: {sum_half_payment}/2")



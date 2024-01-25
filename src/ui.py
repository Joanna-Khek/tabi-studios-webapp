import os
import re
from datetime import datetime
from typing import List, Literal
import pandas as pd
import numpy as np
import streamlit as st

from src import validations

def set_page_config():
    st.set_page_config(
        page_title="TabiStudios Form",
        layout="wide",
        initial_sidebar_state="expanded",
    )

def local_css(css_file):
    with open(css_file) as f:
        st.markdown('<style>{}</style>'.format(f.read()), unsafe_allow_html=True)

def set_local_css():
    curdir = os.path.dirname(os.path.realpath('Home.py')) + r'\\'
    css_file = os.path.join(curdir, 'assets\\style.css')
    local_css(css_file)

def set_page_container_style() -> None:
    """Set report container style."""

    margins_css = """
    <style>
        /* Configuration of paddings of containers inside main area */
        .main > div {
            max-width: 100%;
            padding-left: 5%;
        }
        /*Font size in tabs */
        button[data-baseweb="tab"] div p {
            font-size: 18px;
            font-weight: bold;
        }
    </style>
    """
    st.markdown(margins_css, unsafe_allow_html=True)

def show_logo() -> None:
    logo_url = "assets/Logo.png"
    st.image(logo_url, use_column_width=True)
    st.header("")  # add space between logo and selectors


def display_project_add_details(total_invoice_price: float) -> List:
    """Show additional details fields

    Args:
        total_invoice_price (float): _description_
        int (_type_): _description_
        float (_type_): _description_
        float (_type_): _description_

    Returns:
        add_item (str): description of additional item added
        add_quantity (int): quantity amount of item
        add_rate (float): rate of item
        add_amount (float): add_quantiy * add_rate
    """
    num_add_items = st.number_input(label="Number of additional items",
                                    min_value=1,
                                    key='num_additional_items')

    list_add_item = []
    list_add_quantity = []
    list_add_rate = []
    list_add_amount = []

    for i in range(num_add_items):
        row = st.columns([0.6, 0.1, 0.15, 0.15])
        item = row[0].text_input("Item Description",
                                key=f'add_item_{i+1}_desc')
        
        quantity = row[1].number_input(label="Qty", 
                                        min_value=1, 
                                        step=1,
                                        key=f'add_item_{i+1}_quantity')
        
        rate = row[2].number_input(label="Rate ($)", 
                                min_value=1.00,
                                step=1.00,
                                format="%.2f",
                                key=f'add_item_{i+1}_rate')
        
        amount = row[3].number_input(label="Amount ($)",
                                    value=round(quantity*rate, 2),
                                    disabled=True,
                                    min_value=1.00,
                                    step=1.00,
                                    format="%.2f",
                                    key=f'add_item_{i+1}_amount'
                                    )
        
        total_invoice_price += amount

        list_add_item.append(item)
        list_add_quantity.append(quantity)
        list_add_rate.append(rate)
        list_add_amount.append(amount)

    return list_add_item, list_add_quantity, list_add_rate, list_add_amount, total_invoice_price

def display_project_details(mode=Literal['quotation', 'invoice'],
                            project_items=None) -> List:
    """Show quotation details fields
    Args:
        project_items (pd.DataFrame): quotation info for selected quotation num

    Returns:
        item (str): description of item
        quantity (int): quantity amount of item
        rate (float): rate of item
        amount (float): quantiy * rate
        total_quotation_price (float): total accumulated amount across all items
    """
    
    total_quotation_price = 0

    list_item = []
    list_quantity = []
    list_rate = []
    list_amount = []

    if mode == 'quotation':
        # Blank inputs
        num_items = st.number_input(label="Number of items",
                                    min_value=1,
                                    key='num_items')


        for i in range(num_items):
            row = st.columns([0.6, 0.1, 0.15, 0.15])
            item = row[0].text_input("Item Description",
                                    key=f'item_{i+1}_desc')
            
            quantity = row[1].number_input(label="Qty", 
                                            min_value=1, 
                                            step=1,
                                            key=f'item_{i+1}_quantity')
            
            rate = row[2].number_input(label="Rate ($)",
                                        min_value=1.00,
                                        step=1.00,
                                        format="%.2f",
                                        key=f'item_{i+1}_rate')
            
            amount = row[3].number_input(label="Amount ($)",
                                            value=round(quantity*rate, 2),
                                            disabled=True,
                                            min_value=1.00,
                                            step=1.00,
                                            format="%.2f",
                                            key=f'item_{i+1}_amount',)
            
            total_quotation_price += amount

            list_item.append(item)
            list_quantity.append(quantity)
            list_rate.append(rate)
            list_amount.append(amount)
    
    elif mode == 'invoice':
        # Pre-filled inputs
        num_items = project_items.shape[0]

        for i in range(num_items):
            row = st.columns([0.6, 0.1, 0.15, 0.15])
            item = row[0].text_input("Item Description",
                                     value=project_items.Item.values[i],
                                     disabled=False,
                                     key=f'item_{i+1}_desc')
            
            quantity = row[1].number_input(label="Qty", 
                                           value=int(project_items.Quantity.values[i]),
                                           disabled=False,
                                           key=f'item_{i+1}_quantity')
            
            rate = row[2].number_input(label="Rate ($)",
                                       value=float(project_items.Rate.values[i]),
                                       disabled=False,
                                       format="%.2f",
                                       key=f'item_{i+1}_rate')
            
            amount = row[3].number_input(label="Amount ($)",
                                         value=round(quantity*rate, 2),
                                         disabled=False,
                                         min_value=1.00,
                                         step=1.00,
                                         format="%.2f",
                                         key=f'item_{i+1}_amount',)
            
            total_quotation_price += amount

            list_item.append(item)
            list_quantity.append(quantity)
            list_rate.append(rate)
            list_amount.append(amount)

    return list_item, list_quantity, list_rate, list_amount, total_quotation_price

def display_project_info_inputs(reference: bool, 
                                disabled_status: bool,
                                project_info: pd.DataFrame = None,
                                ):
    """Show project information inputs for quotation and invoice tab

    Args:
        project_info (pd.DataFrame): project information of selected quotation number
        reference (bool, optional): Option to refer to past quotation number details. Defaults to False.
    """
       
    if not reference:
        # Blank quotation
        project_name = st.text_input(label="Project Name")
        project_type = st.selectbox(label='Project Type', 
                                    options=validations.options['project_type'])
        client_contact_person = st.text_input(label="Client Contact Person")
        client_company_name = st.text_input(label="Client Company Name")
        client_uen = st.text_input(label="Client UEN")
        client_email = st.text_input(label="Client Email")
        client_address = st.text_input(label="Client Address")
        project_start_date = st.date_input(label="Project Start Date")
        project_end_date = st.date_input(label="Project End Date")
        expiration_date = st.date_input(label="Quotation Expiration Date")
        credit_term = st.text_input(label="Credit Term")
        date_invoice_quotation = st.date_input(label="Invoice/Quotation Date")

    else:
        # Fill inputs with selected quotation inputs
        project_name = st.text_input(label="Project Name",
                                     disabled=disabled_status,
                                     value=project_info.project_name.values[0])

        project_type = st.selectbox(label='Project Type',
                                    disabled=disabled_status,
                                    options=project_info.project_type)

        client_contact_person = st.text_input(label="Contact Person",
                                              disabled=disabled_status,
                                              value=project_info.client_contact_person.values[0])

        client_company_name = st.text_input(label="Client Company Name",
                                            disabled=disabled_status,
                                            value=project_info.client_company_name.values[0])

        client_uen = st.text_input(label="Client UEN",
                                   disabled=disabled_status,
                                   value=project_info.client_uen.values[0])

        client_email = st.text_input(label="Client Email",
                                     disabled=disabled_status,
                                     value=project_info.client_email.values[0])

        client_address = st.text_input(label="Client Address",
                                       disabled=disabled_status,
                                       value=project_info.client_address.values[0])

        project_start_date = st.date_input(label="Project Start Date",
                                           disabled=disabled_status,
                                           value=pd.to_datetime(project_info.project_start_date.values[0]))

        project_end_date = st.date_input(label="Project End Date",
                                         disabled=disabled_status,
                                         value=pd.to_datetime(project_info.project_end_date.values[0]))

        expiration_date = st.date_input(label="Quotation Expiration Date",
                                        disabled=disabled_status,
                                        value=pd.to_datetime(project_info.quotation_expiry_date.values[0]))
        
        credit_term = st.text_input(label="Credit Term",
                                    disabled=disabled_status,
                                    value=project_info.credit_term.values[0])
        
        date_invoice_quotation = st.date_input(label="Invoice/Quotation Date",
                                               disabled=disabled_status,
                                               value="today")
    
    # Save all the information
    dict_project_info = {'project_name': project_name,
                         'project_type': project_type,
                         'client_contact_person': client_contact_person,
                         'client_company_name': client_company_name,
                         'client_uen': client_uen,
                         'client_email': client_email,
                         'client_address': client_address,
                         'project_start_date': project_start_date,
                         'project_end_date': project_end_date,
                         'expiration_date': expiration_date,
                         'credit_term': credit_term,
                         'date': date_invoice_quotation
                         }
    
    return dict_project_info

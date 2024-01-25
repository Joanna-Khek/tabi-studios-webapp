import os
import re
from datetime import datetime
from typing import Optional
import streamlit as st
import pandas as pd
import numpy as np
from dotenv import load_dotenv
import sqlalchemy
from sqlalchemy import create_engine, text
from psycopg2.extensions import register_adapter, AsIs
from pathlib import Path

def save_project_details(
                         quotation_num: str,
                         project_name: str,
                         project_type: str,
                         client_contact_person: str,
                         client_company_name: str,
                         client_uen: str,
                         client_email: str,
                         client_address: str,
                         project_start_date: datetime,
                         project_end_date: datetime,
                         total_quotation_price: float,
                         quotation_expiry_date: datetime,
                         credit_term: str,
                         df_items: pd.DataFrame) -> pd.DataFrame:
    """Save project details into database"""

    # Project Details Table
    project_details = {'quotation_num': quotation_num,
                        'project_name': project_name,
                        'project_type': project_type,
                        'client_contact_person': client_contact_person,
                        'client_company_name': client_company_name,
                        'client_uen': client_uen,
                        'client_email': client_email,
                        'client_address': client_address,
                        'project_start_date': project_start_date,
                        'project_end_date': project_end_date,
                        'quotation_price': str(total_quotation_price).replace("$", ""),
                        'quotation_sent_date': datetime.now().date(),
                        'quotation_expiry_date': quotation_expiry_date,
                        'credit_term': credit_term,
                        'job_confirm_date': '',
                        'invoice_num': '',
                        'total_invoice_price': '',
                        'invoice_price': '',
                        'invoice_sent_date': '',
                        'invoice_half_payment': '',
                        'payment_received_date': ''}


    # Project Item Details Table
    df_items = df_items.assign(quotation_num=quotation_num)

    
    # Convert to dataframe
    df_project = pd.DataFrame.from_dict(project_details, orient='index').T

    # Save to database
    conn = create_connection()
    df_project.to_sql("project_details", conn, if_exists='append', index=False)
    df_items.to_sql("quotation_items", conn, if_exists='append', index=False)


def save_invoice_details(engine: sqlalchemy,
                         project_info: pd.DataFrame,
                         df_items: pd.DataFrame,
                         quotation_num: str,
                         invoice_num: str,
                         project_name: str,
                         half_payment: bool,
                         total_invoice_price: str,
                         adjusted_invoice_price: str):
       
        df_half_payment = pd.read_sql_query("SELECT DISTINCT(quotation_num) FROM half_payment_projects", engine)

         # Check if invoice is half payment
        if df_half_payment.quotation_num.str.contains(quotation_num).sum() == 1:
            # Check whether any invoice has been sent before
            if project_info.invoice_sent_date.values[0] != '':
                # Not the first invoice entry of half payment projects
                # Update the entries of the first invoice entry
                project_info_updated = (project_info
                                        .copy()
                                        .assign(invoice_num=invoice_num,
                                                invoice_half_payment=half_payment,
                                                invoice_price=adjusted_invoice_price,
                                                invoice_sent_date=datetime.now().date())
                                                ) 
                project_info_updated.to_sql("project_details", con=engine, if_exists='append', index=False)

            else: 
                # First invoice entry
                update_task(engine, 
                            table='project_details',
                            column='invoice_num',
                            ref_column='quotation_num',
                            task=(invoice_num, quotation_num))
                update_task(engine, 
                            table='project_details',
                            column='invoice_half_payment', 
                            ref_column='quotation_num',
                            task=(half_payment, quotation_num))
                update_task(engine, 
                            table='project_details',
                            column='invoice_price',
                            ref_column='quotation_num',
                            task=(str(adjusted_invoice_price).replace("$", ""), quotation_num))
                update_task(engine, 
                            table='project_details',
                            column='total_invoice_price', 
                            ref_column='quotation_num',
                            task=(str(total_invoice_price).replace("$", ""), quotation_num))
                update_task(engine, 
                            table='project_details',
                            column='invoice_sent_date', 
                            ref_column='quotation_num',
                            task=(datetime.now().date(), quotation_num))
        else:
            # Not half payment invoice entry
            update_task(engine, 
                        table='project_details',
                        column='invoice_num', 
                        ref_column='quotation_num',
                        task=[invoice_num, quotation_num])
            update_task(engine, 
                        table='project_details',
                        column='invoice_half_payment', 
                        ref_column='quotation_num',
                        task=[half_payment, quotation_num])
            update_task(engine, 
                        table='project_details',
                        column='invoice_price', 
                        ref_column='quotation_num',
                        task=[str(adjusted_invoice_price).replace("$", ""), quotation_num])
            update_task(engine, 
                        table='project_details',
                        column='total_invoice_price', 
                        ref_column='quotation_num',
                        task=[str(total_invoice_price).replace("$", ""), quotation_num])
            update_task(engine, 
                        table='project_details',
                        column='invoice_sent_date', 
                        ref_column='quotation_num',
                        task=[datetime.now().date(), quotation_num])

        # Update invoice additional items
        df_items = df_items.assign(invoice_num=invoice_num,
                                   quotation_num=quotation_num,
                                   project_name=project_name)
        df_items.to_sql("invoice_items", engine, if_exists='append', index=False)

def configure_db_types():
    def addapt_numpy_float64(numpy_float64):
        return AsIs(numpy_float64)

    def addapt_numpy_int64(numpy_int64):
        return AsIs(numpy_int64)

    def addapt_numpy_float32(numpy_float32):
        return AsIs(numpy_float32)

    def addapt_numpy_int32(numpy_int32):
        return AsIs(numpy_int32)

    def addapt_numpy_array(numpy_array):
        return AsIs(tuple(numpy_array))

    register_adapter(np.float64, addapt_numpy_float64)
    register_adapter(np.int64, addapt_numpy_int64)
    register_adapter(np.float32, addapt_numpy_float32)
    register_adapter(np.int32, addapt_numpy_int32)
    register_adapter(np.ndarray, addapt_numpy_array)

def create_connection():
    #conn = sqlite3.connect(df_file)
    load_dotenv()
    DATABASE_URL = os.environ['DATABASE_URL']
    final_db_url = "postgresql+psycopg2://" + DATABASE_URL.lstrip("postgres://")
    engine = create_engine(final_db_url)
    configure_db_types()

    return engine

def update_task(engine, table, column, ref_column, task):
    sql = text(f"UPDATE {table} SET {column} = (:column_value) WHERE {ref_column} = (:ref_column)")
    params = {'column_value': task[0],
              'ref_column': task[1]}

    with engine.connect() as connection:
        connection.execute(sql, params)
        connection.commit()
    engine.dispose()

def delete_task(engine, table, value):
    sql = text(f"DELETE FROM {table} WHERE quotation_num = (:value)")
    params = {'value': value}

    with engine.connect() as connection:
        connection.execute(sql, params)
        connection.commit()
    engine.dispose()

def add_task(engine, table, value):
    sql = text(f"INSERT INTO {table} VALUES (:value)")
    params = {'value': value}
    with engine.connect() as connection:
        connection.execute(sql, params)
        connection.commit()
    engine.dispose()
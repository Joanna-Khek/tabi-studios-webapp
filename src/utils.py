import os
import io
from typing import Literal, BinaryIO, Optional
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime
import numpy as np
import pandas as pd
import streamlit as st
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseDownload

from jinja2 import Environment, select_autoescape, FileSystemLoader
import pdfkit

from src import database

load_dotenv()

def generate_quotation_invoice(mode: Literal['quotation', 'invoice'],
                               file_name: str,
                               project_name: str,
                               client_contact_person: str,
                               client_company_name: str,
                               client_address: str,
                               client_email: str,
                               reference_num: str,
                               half_payment: bool,
                               quote_type: str,
                               df_half_payment_items: pd.DataFrame,
                               df_items: pd.DataFrame,
                               total_price: float,
                               adjusted_price: float,
                               payment_due_date: Optional[datetime],
                               expiration_date: Optional[datetime],
                               credit_term: Optional[str],
                               payment_term: Optional[str],
                               date: datetime
                                ) -> BinaryIO:
    """Input user inputs to the html template and generate a pdf

    Args:
        file_name (str): file name of quotation pdf
        project_name (str): name of project
        client_contact_person (str): name of contact person
        client_company_name (str): company name of client
        client_address (str): company address of client
        client_email (str): email address of client
        reference_num (str): quotation/invoice reference number
        half_payment (bool): whether this is a half payment project
        quote_type (str): Whether this is variational quotation
        df_items (pd.DataFrame): quotation items details
        total_quotation_price (float): total price

    Returns:
        BinaryIO: pdf binary from wkhtmltopdf
    """
    
    env = Environment(loader=FileSystemLoader("."), autoescape=select_autoescape())
    if mode == 'quotation':
        template = env.get_template("assets/quotation_template.html")
        html_body = template.render(PROJECT_NAME = project_name,
                                    CONTACT_PERSON = client_contact_person,
                                    CLIENT_NAME = client_company_name,
                                    CLIENT_ADDRESS = client_address,
                                    CLIENT_EMAIL = client_email,
                                    REFERENCE_NUM = reference_num,
                                    HALF_PAYMENT = half_payment,
                                    QUOTE_TYPE = quote_type,
                                    ITEMS = df_items,
                                    TOTAL_PRICE = total_price,
                                    EXPIRATION_DATE = expiration_date.strftime(format="%d %B %Y"),
                                    CREDIT_TERM = credit_term,
                                    DATE_TODAY = date.strftime(format="%d %B %Y"))


    elif mode == 'invoice':
        template = env.get_template("assets/invoice_template.html")
        html_body = template.render(PROJECT_NAME = project_name,
                                    CONTACT_PERSON = client_contact_person,
                                    CLIENT_NAME = client_company_name,
                                    CLIENT_ADDRESS = client_address,
                                    CLIENT_EMAIL = client_email,
                                    REFERENCE_NUM = reference_num,
                                    HALF_PAYMENT = half_payment,
                                    HALF_PAYMENT_ITEMS = df_half_payment_items,
                                    ITEMS = df_items,
                                    PAYMENT_TERM = payment_term,
                                    CREDIT_TERM = credit_term,
                                    TOTAL_PRICE = total_price,
                                    ADJUSTED_TOTAL_PRICE = adjusted_price,
                                    DATE_TODAY = date.strftime(format="%d %B %Y"),
                                    DUE_DATE = pd.to_datetime(payment_due_date).strftime(format="%d %B %Y"))


    # path_wkhtmltopdf = r'C:\Users\Joanna\Desktop\Projects\tabistudios-webapp\wkhtmltopdf.exe'
    # config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
    options = {
        'page-size': 'A4',
        'dpi': 800,
        'enable-local-file-access': ''}
    

    file_path = f"data/{file_name}"
    pdf_local = pdfkit.from_string(html_body, 
                                   output_path=file_path,
                                   options=options)
    
    pdf_remote = pdfkit.from_string(html_body, 
                                    options=options)

    # pdf_local = pdfkit.from_string(html_body,
    #                                 output_path=file_path,
    #                                 configuration=config,
    #                                 options=options)
                    
    # pdf_remote = pdfkit.from_string(html_body,
    #                                 configuration=config,
    #                                 options=options)
    return pdf_local, pdf_remote

def authenticate():
    """Connects to google drive"""

    SCOPES = ['https://www.googleapis.com/auth/drive']
    GOOGLE_APPLICATION_CREDENTIALS = {
                    "type": "service_account",
                    "project_id": os.getenv("PROJECT_ID"),
                    "private_key_id": os.getenv("PRIVATE_KEY_ID"),
                    "private_key": os.getenv("PRIVATE_KEY"),
                    "client_email": os.getenv("CLIENT_EMAIL"),
                    "client_id": os.getenv("CLIENT_ID"),
                    "auth_uri": os.getenv("AUTH_URI"),
                    "token_uri": os.getenv("TOKEN_URI"),
                    "auth_provider_x509_cert_url": os.getenv("AUTH_PROVIDER"),
                    "client_x509_cert_url": os.getenv("CLIENT"),
                    "universe_domain": os.getenv("UNIVERSE_DOMAIN")
                }

    creds = service_account.Credentials.from_service_account_info(GOOGLE_APPLICATION_CREDENTIALS, scopes=SCOPES)
    return creds

def upload_file(file_name: str,
                file_path: Path) -> None:
    """Create project metadata and upload pdf to google drive

    Args:
        file_name (str): quotation pdf filename
        file_path (Path): path of file to be uploaded to drive
    """

    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)

    file_metadata = {
        'name': file_name,
        'useDomainAdminAccess':True,
        'parents': [os.getenv("GOOGLE_DRIVE_PARENT_FOLDER_ID")]
    }

    file = service.files().create(
        body=file_metadata,
        media_body=file_path
    ).execute()



def download_file(file_name: str) -> None:
    """Downloads file from google drive

    Args:
        metadata (dict): project metadata to be queried
    """
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)


    file_id = service.files().list(q=f"name='{file_name}'",
                                   spaces='drive').execute()['files'][0]['id']
    
    request = service.files().get_media(fileId=file_id)
    file = io.BytesIO()
    downloader = MediaIoBaseDownload(file, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print(F'Download {int(status.progress() * 100)}.')

    with open(f'data/{file_name}', 'wb') as output:
        output.write(file.getvalue())

def item_save_to_dataframe(list_item: list,
                           list_quantity: list,
                           list_rate: list,
                           list_amount: list) -> pd.DataFrame:
    df = pd.DataFrame()
    df['Item'] = list_item
    df['Quantity'] = list_quantity
    df['Rate'] = list_rate
    df['Amount'] = list_amount

    df.Rate = df.Rate.apply(lambda x: np.where(len(str(x).split(".")[1]) == 1,
                                                str(x) + '0', 
                                                x)) 
    df.Amount = df.Amount.apply(lambda x: np.where(len(str(x).split(".")[1]) == 1,
                                                str(x) + '0', 
                                                x)) 
    return df

def get_reference_num(mode):
    engine = database.create_connection()
    df_ref_num = pd.read_sql_query("SELECT * FROM reference_number", engine)
    if mode == 'quotation':
        current_num = df_ref_num.quotation_num.values[0]
    elif mode == 'invoice':
        current_num = df_ref_num.invoice_num.values[0]

    return current_num

def update_reference_num(mode: Literal['quotation', 'invoice'],
                         current_num: int,
                         operation: Literal['add', 'subtract'],):
    
    engine = database.create_connection()

    # Update reference number
    if operation == 'add':
        new_num = int(current_num) + 1
        
    elif operation == 'subtract':
        new_num = int(current_num) - 1

    if mode == 'quotation':
        st.session_state.quotation_num = new_num
        # Save to database
        database.update_task(engine=engine,
                            table='reference_number',
                            column='quotation_num',
                            ref_column='quotation_num',
                            task=[new_num, current_num])
    elif mode =='invoice':
        st.session_state.invoice_num = new_num
        # Save to database
        database.update_task(engine=engine,
                            table='reference_number',
                            column='invoice_num',
                            ref_column='invoice_num',
                            task=[new_num, current_num])

    

def format_ref_num(mode: Literal['quotation', 'invoice']):
    
    # Get current number
    new_num = get_reference_num(mode=mode)

    # Add zeros in front
    num_zeros_to_add = len('000') - len(str(new_num))

    # New number
    new_num = '0'*num_zeros_to_add + str(new_num)

    # Add Year
    year_str = str(datetime.now().year)

    if mode == 'quotation':
        final_num = 'TSQ' + year_str + new_num
    elif mode == 'invoice':
        final_num = 'TSI' + year_str + new_num
    return final_num

def format_total_price(price: float):
    final_price = np.where(len(str(price).split(".")[1]) == 1,
                               str(price) + '0', 
                               price)
    return final_price

def calculate_total_price(total_invoice_price: float,
                          payment_factor: float) -> str:
    """Calculates total invoice price taking into account half payment

    Args:
        total_invoice_price (float): sum of all items
        payment_factor (float): either 0.5 or 1 to take into account half payment

    Returns:
        str: total invoice price formatted
    """
    price = total_invoice_price*payment_factor
    final_price = format_total_price(price)
    return final_price
import os
from dotenv import load_dotenv
from typing import Literal
import smtplib

from email import encoders
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

load_dotenv()


def send_email(mode: Literal['quotation', 'invoice'],
               client_email: str, 
               client_contact_person: str, 
               project_name: str, 
               file_name: str):


    email_sender = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")

    
    msg = MIMEMultipart("alternative")
    

    if mode == 'quotation':
        subject = f'Quotation for {project_name}'

        html_text = f"""
        <br>
        <img src="cid:logo" width=400px height=150px/>
        <br>
        Dear <b>{client_contact_person},</b>
        <br>
        <p>I hope you're having an awesome day! We're thrilled that you're exploring Tabi Studios for your project needs.
        We've put together a tailored quotation just for you. You can find the detailed quotation attached as a PDF for your convenience.
        <br>
        <br>
        If you've got questions or need more info about the quotation, feel free to contact us as daren@tabistudios.co
        <br>
        <br>
        Regards, <br>
        Daren
        </p>
        """.format(client_name=client_contact_person,
                   project_name=project_name)
        
    elif mode == 'invoice':
        subject = f'Invoice for {project_name}'

        html_text = f"""
        <br>
        <img src="cid:logo" width=400px height=150px/>
        <br>
        Dear <b>{client_contact_person},</b>
        <br>
        <p>I trust you're doing well. We're reaching out to share your invoice for the project, {project_name}, you've received from Tabi Studios. We greatly value your business and are honored to assist you.
        <br>
        <br>
        Please find the attached invoice for a detailed breakdown of the charges.
        <br>
        <br>
        Thank you for choosing us, and if you have any questions or need further assistance, please don't hesitate to reach us at daren@tabistudios.co
        <br>
        <br>
        Regards, <br>
        Daren
        </p>
        """.format(client_name=client_contact_person,
                   project_name=project_name)


    msg['From'] = email_sender
    msg['To'] = client_email
    msg['Subject'] = subject
    
    body = MIMEText(html_text, 'html')
    msg.attach(body)

    fo = open(f"data/{file_name}",'rb')
    attach = MIMEApplication(fo.read(),_subtype="pdf")
    fo.close()
    attach.add_header('Content-Disposition','attachment',filename=file_name)
    msg.attach(attach)
    

    with open("assets/Logo.png", "rb") as f:
        img_data = MIMEImage(f.read())

    img_data.add_header('Content-ID', '<logo>')
    msg.attach(img_data)


    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(email_sender, password)
    server.sendmail(email_sender, client_email, msg.as_string())
    server.quit()

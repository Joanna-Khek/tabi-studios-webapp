# Tabi Studios Web Application

## Project Description
My younger brother has recently embarked on his entrepreneurial journey. As his elder sister, I decided to put my data skills to good use. I developed a Streamlit web application to assist him in streamlining business processing workflow. The web application is hosted on streamlit private server and can be accessed through a web link. 

The image below illustrates the features and workflow of the web application.
![architecture](https://github.com/Joanna-Khek/tabi-studios-webapp/assets/53141849/8febc3ae-7830-4461-895f-74363968c278)

The web application allows users to perform the following actions:
- Generate quotation/invoice
- Send email with attached quotation/invoice
- Save quotation/invoice to google drive
- Save quotation/invoice details to cloud database
- Update project information and save to database
- View statistics via dashboard

## Features and Usage
### 1. Generate Quotation and Invoice
- Users fill up client information via a form in the web application. The inputs of the form will be populated onto the HTML template for both quotation and invoice.
- Users can click on the *"Generate Quotation/Invoice"* button to download a PDF version of the generated quotation/invoice.

![preview_quotation](https://github.com/Joanna-Khek/tabi-studios-webapp/assets/53141849/4b2590b0-829b-4e1b-b901-dba3353e525f)

### 2. Email
- If user is satisfied with the generated content, proceed to email client by clicking on *"Send Email"* button. An email template in HTML is created for this purpose and the quotation/invoice will be attached in the email.
  
### 3. Save to google drive and cloud database
- A copy of the quotation/invoice can be saved to the user's google drive.
- Users can also save the details to a cloud database.

![preview_buttons](https://github.com/Joanna-Khek/tabi-studios-webapp/assets/53141849/bfa99fb5-53be-41f4-b1a7-1b8760660780)

### 4. Update project status
- Users can also update the status of the project such as job confirmation date and whether payment has been received.
  
![preview_update](https://github.com/Joanna-Khek/tabi-studios-webapp/assets/53141849/eff3cfd8-5afb-468a-9405-204a10020544)

### 5. Dashboard
- Finally, all the information saved in the database is used to build a business statistics dashboard.

![preview_dashboard](https://github.com/Joanna-Khek/tabi-studios-webapp/assets/53141849/7d5c23e2-a09b-48e1-b2e7-add50639b935)

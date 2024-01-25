import re
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime, timedelta

import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards

def total_unearned_revnue(df_projects: pd.DataFrame) -> float:
    """Compute total quotation revenue"""

    value = (df_projects
             .query("job_confirm_date != ''")
             .quotation_price
             .astype(float)
             .sum())
    if value == '':
        value = 0
    return '$' + str(value)

def total_revenue(df_projects: pd.DataFrame) -> float:
    """Compute the total revenue. Only those job"""

    temp = df_projects.copy()
    temp = (temp
            .assign(invoice_price=lambda df_: np.where(df_.invoice_price == '', 0, df_.invoice_price))
            .query("payment_received_date != ''"))
    value = temp.invoice_price.astype(float).sum()
        
    return '$' + str(value)


def total_quotation(df_projects: pd.DataFrame) -> int:
    """Compute the number of unique quotations"""
    value = df_projects.quotation_num.nunique()

    return value

def total_invoices(df_projects: pd.DataFrame) -> int:
    """Compute the number of unique invoices issued"""

    value = df_projects.invoice_num.replace('', np.nan).nunique()
    
    return value

def total_job_taken(df_projects: pd.DataFrame) -> int:
    """Compute total job accepted"""
    value = len(df_projects.query("job_confirm_date != ''"))
    return value

def total_monthly_salary(df_projects: pd.DataFrame) -> int:
    """Compute total monthly salary based on project date"""
    temp = df_projects.copy()
    temp = temp.assign(project_end_month=lambda df_: pd.to_datetime(df_.project_end_date).dt.month,
                       project_end_year=lambda df_: pd.to_datetime(df_.project_end_date).dt.year)
    month_now = datetime.now().month
    year_now = datetime.now().year

    projects_month_year = temp.query(f"project_end_month == {month_now} and project_end_year == {year_now}")
    value = projects_month_year.quotation_price.astype(float).sum()

    return value
    
def upcoming_projects(df_projects: pd.DataFrame) -> int:
    """Upcoming projects by month"""
    temp = df_projects.copy()

    temp['date'] = list(map(lambda x, y: pd.date_range(start=x, end=y, freq='M'),
                      temp['project_start_date'], 
                      temp['project_end_date']))
    temp = (temp
            .explode('date')
            .assign(date=lambda df_: df_.date.fillna(df_.project_start_date))
            .assign(date=lambda df_: df_.date.dt.to_period('M'))
    )
    test = temp.date.value_counts().reset_index()
    test = test.assign(date=lambda df_: df_.date.astype(str))
    c = alt.Chart(test).mark_bar().encode(
        x="date", 
        y=alt.Y('count', scale=alt.Scale())
    )
    st.altair_chart(c, use_container_width=True)


def show_revenue_metrics(df_projects):

    col1, col2 = st.columns(2)
    col1.metric(label="Total Projected Revenue", 
                value=total_unearned_revnue(df_projects))
    col2.metric(label="Total Earned Revenue", value=total_revenue(df_projects))
    style_metric_cards(border_left_color='#4051b5')

def show_metrics(df_projects):

    col1, col2, col3 = st.columns(3)

    col1.metric(label="Total Job Taken", value=total_job_taken(df_projects))
    col2.metric(label="# Quotations Issued", value=total_quotation(df_projects))
    col3.metric(label="# Invoices Issued", value=total_invoices(df_projects))
    style_metric_cards(border_left_color='#4051b5')

def payment_expiration(df_projects):
    temp = df_projects.copy()
    temp = (temp
            .assign(Payment_Countdown = lambda df_: pd.to_datetime(df_.invoice_sent_date) + timedelta(days=30),
                    Deadline = lambda df_: np.where(df_.Payment_Countdown.dt.date >= datetime.now().date(),
                                                   "Due", 
                                                   "Not Due"),
                    payment_received_date=lambda df_: pd.to_datetime(df_.payment_received_date)
                    )
            .query("payment_received_date.isnull() and Deadline == 'Due'")
            .drop(["Payment_Countdown", "Deadline"], axis=1)
            )
    
    if temp.shape[0] != 0:
        st.dataframe(temp, hide_index=True)
    else:
        st.success("No payments overdue soon!")


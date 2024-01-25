import streamlit as st
import pandas as pd
from datetime import datetime
from src import ui
from src import dashboard
from src import database

if __name__ == "__main__":

    ui.set_page_config()
    ui.set_page_container_style()
    #ui.show_logo()

    st.title("Dashboard")
    col1, col2, col3 = st.columns(3)

    engine = database.create_connection()
    df_projects = pd.read_sql_query("SELECT * FROM project_details", engine)

    month = datetime.now().strftime(format='%B')
    st.subheader(f"{month} Statistics")
    dashboard.show_revenue_metrics(df_projects)
    dashboard.show_metrics(df_projects)

    st.subheader("Payments Due Soon")
    dashboard.payment_expiration(df_projects)

    st.subheader("Upcoming Projects")
    col1, col2 = st.columns(2)
    with col1:
        dashboard.upcoming_projects(df_projects)
    with col2:
        st.dataframe(df_projects.loc[:, ["project_name", "client_company_name", "project_start_date", "project_end_date"]], hide_index=True)
    
    

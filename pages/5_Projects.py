import streamlit as st
import pandas as pd
from src import database

st.title("Project Search")

engine = database.create_connection()
df_project = (pd.read_sql_query("SELECT * FROM project_details", engine)
              .sort_values(by='quotation_num', ascending=True))

st.dataframe(df_project, hide_index=True)
# search_by = st.radio("Search by", ["Quotation Number", "Project Name"])
# if search_by == 'Quotation Number':
#     input = st.selectbox("Quotation Number",
#                          options=list(df_project.quotation_num.sort_values().unique()))
#     filter = df_project.query(f"quotation_num == '{input}'")
#     st.dataframe(filter, hide_index=True)

# elif search_by == 'Project Name':
#     input = st.selectbox("Project Name",
#                          options=list(df_project.project_name.sort_values().unique()))
#     filter = df_project.query(f"project_name == '{input}'")
#     st.dataframe(filter, hide_index=True)




import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import StringIO
import os

st.set_page_config(page_title="Student Attendance Analysis", layout="wide", page_icon="📊")
st.title("📊 Student Attendance Analysis")

# Set up directories
os.makedirs('exports', exist_ok=True)
os.makedirs('data', exist_ok=True)

st.sidebar.header("Upload Attendance Data")
uploaded_file = st.sidebar.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file:
    # Save uploaded file to data folder
    file_path = os.path.join('data', uploaded_file.name)
    with open(file_path, 'wb') as f:
        f.write(uploaded_file.getbuffer())
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)
    st.success("Data loaded successfully!")
    st.write("### Raw Data", df)

    # Data Cleaning
    st.subheader("🧹 Data Cleaning & Preprocessing")
    st.write(f"Rows before cleaning: {df.shape[0]}")
    df_clean = df.dropna()
    st.write(f"Rows after dropping missing: {df_clean.shape[0]}")
    st.write(df_clean.head())

    # Convert 'Attendance' to numeric (1 for Present, 0 for Absent)
    if 'Attendance' in df_clean.columns:
        df_clean['Attendance_Numeric'] = df_clean['Attendance'].map({'Present': 1, 'Absent': 0})
    # Use 'Name' instead of 'Student' for grouping
    if 'Attendance_Numeric' in df_clean.columns and 'Name' in df_clean.columns:
        attendance_summary = df_clean.groupby('Name')["Attendance_Numeric"].mean().reset_index()
        attendance_summary["Attendance %"] = attendance_summary["Attendance_Numeric"] * 100
        st.write("#### Attendance Percentage per Student", attendance_summary)

        # Flag low attendance
        threshold = st.slider("Flag students below attendance %", 0, 100, 75)
        flagged = attendance_summary[attendance_summary["Attendance %"] < threshold]
        st.warning(f"Students below {threshold}% attendance:")
        st.dataframe(flagged)

        # Visualizations
        st.subheader("📊 Visualizations")
        fig, ax = plt.subplots(figsize=(10,4))
        sns.barplot(x="Name", y="Attendance %", data=attendance_summary, ax=ax)
        plt.xticks(rotation=45)
        st.pyplot(fig)

        st.line_chart(attendance_summary.set_index("Name")["Attendance %"])
    else:
        st.error("Required columns ('Name', 'Attendance') not found or not properly formatted.")

    # Export cleaned data
    st.subheader("📤 Export Cleaned Data")
    csv = df_clean.to_csv(index=False).encode('utf-8')
    export_path = os.path.join('exports', 'cleaned_attendance.csv')
    with open(export_path, 'wb') as f:
        f.write(csv)
    st.download_button("Download Cleaned CSV", csv, "cleaned_attendance.csv", "text/csv")
else:
    st.info("Please upload an attendance CSV or Excel file to begin analysis.")

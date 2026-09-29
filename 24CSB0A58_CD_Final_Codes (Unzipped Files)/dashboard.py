import pandas as pd
import os
import streamlit as st

def render_dashboard():
    st.title("📊 Error Analytics Dashboard")
    
    log_file = "compiler_errors.csv"
    if os.path.exists(log_file):
        df = pd.read_csv(log_file)
        
        if df.empty:
            st.info("No errors recorded yet.")
            return

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Errors Recorded", len(df))
        with col2:
            st.metric("Unique Error Types", df['Error_Type'].nunique())

        st.subheader("Top Error Types")
        error_counts = df['Error_Type'].value_counts()
        st.bar_chart(error_counts)
        
        st.subheader("Recent Error Log")
        st.dataframe(df.tail(10).iloc[::-1]) # Show last 10 in reverse chronological
        
    else:
        st.info("No errors recorded yet.")

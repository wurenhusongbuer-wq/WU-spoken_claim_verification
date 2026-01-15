"""
Streamlit Main Application

Main entry point for the Streamlit web interface of the claim verification system.

Author: Capstone Team
Date: 2024
"""

import streamlit as st
from streamlit_option_menu import option_menu
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(
    page_title="Claim Verification System",
    page_icon="✓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding-top: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-badge {
        background-color: #d4edda;
        color: #155724;
        padding: 0.5rem 1rem;
        border-radius: 0.25rem;
        display: inline-block;
    }
    .error-badge {
        background-color: #f8d7da;
        color: #721c24;
        padding: 0.5rem 1rem;
        border-radius: 0.25rem;
        display: inline-block;
    }
    .warning-badge {
        background-color: #fff3cd;
        color: #856404;
        padding: 0.5rem 1rem;
        border-radius: 0.25rem;
        display: inline-block;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'Home'

# Sidebar navigation
with st.sidebar:
    st.image("https://via.placeholder.com/200x100?text=Logo", use_column_width=True)
    st.title("Navigation")
    
    selected = option_menu(
        menu_title=None,
        options=["Home", "Upload Video", "Analysis", "Results", "Monitoring", "Evaluation", "Settings"],
        icons=["house", "upload", "search", "bar-chart", "speedometer", "graph-up", "gear"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "#fafafa"},
            "icon": {"color": "orange", "font-size": "25px"},
            "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "#ff6b6b"},
        }
    )
    
    st.markdown("---")
    st.markdown("### System Status")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("API Status", "✓ Online")
    with col2:
        st.metric("DB Status", "✓ Connected")

# Main content area
if selected == "Home":
    from pages import home_page
    home_page.render()

elif selected == "Upload Video":
    from pages import upload_page
    upload_page.render()

elif selected == "Analysis":
    from pages import analysis_page
    analysis_page.render()

elif selected == "Results":
    from pages import results_page
    results_page.render()

elif selected == "Monitoring":
    from pages import monitoring_page
    monitoring_page.render()

elif selected == "Evaluation":
    from pages import evaluation_page
    evaluation_page.render()

elif selected == "Settings":
    from pages import settings_page
    settings_page.render()

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: gray; font-size: 12px;'>
        <p>Spoken Claim Verification System v1.0.0</p>
        <p>© 2024 Capstone Project. All rights reserved.</p>
    </div>
""", unsafe_allow_html=True)

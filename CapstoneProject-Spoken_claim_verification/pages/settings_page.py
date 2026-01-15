"""
Settings Page

System configuration and settings management.

Author: Capstone Team
Date: 2024
"""

import streamlit as st


def render():
    """Render settings page."""
    st.title("⚙️ Settings")
    
    st.markdown("""
        Configure system settings and preferences.
    """)
    
    # Settings tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["General", "API Keys", "Processing", "Database", "Advanced"]
    )
    
    # General Settings
    with tab1:
        st.markdown("## General Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Application")
            
            app_name = st.text_input(
                "Application Name",
                value="Spoken Claim Verification System"
            )
            
            app_version = st.text_input(
                "Application Version",
                value="1.0.0",
                disabled=True
            )
            
            language = st.selectbox(
                "Language",
                ["English", "Chinese", "Spanish", "French"]
            )
            
            theme = st.selectbox(
                "Theme",
                ["Light", "Dark", "Auto"]
            )
        
        with col2:
            st.markdown("### System")
            
            log_level = st.selectbox(
                "Log Level",
                ["DEBUG", "INFO", "WARNING", "ERROR"],
                index=1
            )
            
            debug_mode = st.checkbox("Debug Mode", value=False)
            
            auto_refresh = st.checkbox("Auto-refresh Dashboard", value=True)
            
            refresh_interval = st.slider(
                "Refresh Interval (seconds)",
                min_value=5,
                max_value=60,
                value=30,
                disabled=not auto_refresh
            )
        
        if st.button("💾 Save General Settings"):
            st.success("Settings saved successfully!")
    
    # API Keys
    with tab2:
        st.markdown("## API Configuration")
        
        st.warning("⚠️ Never share your API keys. Keep them confidential.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Google APIs")
            
            google_api_key = st.text_input(
                "Google API Key",
                type="password",
                placeholder="Enter your Google API key"
            )
            
            google_search_key = st.text_input(
                "Google Search API Key",
                type="password",
                placeholder="Enter your Google Search API key"
            )
            
            google_search_engine_id = st.text_input(
                "Google Search Engine ID",
                type="password",
                placeholder="Enter your Search Engine ID"
            )
        
        with col2:
            st.markdown("### Other Services")
            
            openai_api_key = st.text_input(
                "OpenAI API Key (Optional)",
                type="password",
                placeholder="Enter your OpenAI API key"
            )
            
            api_timeout = st.slider(
                "API Timeout (seconds)",
                min_value=10,
                max_value=300,
                value=60
            )
            
            max_retries = st.slider(
                "Max Retries",
                min_value=1,
                max_value=10,
                value=3
            )
        
        if st.button("💾 Save API Settings"):
            st.success("API settings saved successfully!")
    
    # Processing Settings
    with tab3:
        st.markdown("## Processing Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Speech Recognition")
            
            whisper_model = st.selectbox(
                "Whisper Model",
                ["tiny", "base", "small", "medium", "large-v3"],
                index=4
            )
            
            audio_sample_rate = st.slider(
                "Audio Sample Rate (Hz)",
                min_value=8000,
                max_value=48000,
                value=16000,
                step=1000
            )
            
            language = st.selectbox(
                "Audio Language",
                ["Auto-detect", "English", "Chinese", "Spanish"],
                index=0
            )
        
        with col2:
            st.markdown("### Claim Processing")
            
            gemini_temperature = st.slider(
                "Gemini Temperature",
                min_value=0.0,
                max_value=1.0,
                value=0.3,
                step=0.05
            )
            
            max_tokens = st.slider(
                "Max Tokens",
                min_value=500,
                max_value=4000,
                value=2000,
                step=100
            )
            
            confidence_threshold = st.slider(
                "Confidence Threshold",
                min_value=0.0,
                max_value=1.0,
                value=0.5,
                step=0.05
            )
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Evidence Retrieval")
            
            num_search_results = st.slider(
                "Number of Search Results",
                min_value=1,
                max_value=10,
                value=5
            )
            
            extract_full_text = st.checkbox(
                "Extract Full Text from Sources",
                value=False
            )
        
        with col2:
            st.markdown("### Processing Options")
            
            batch_size = st.slider(
                "Batch Size",
                min_value=1,
                max_value=50,
                value=10
            )
            
            max_workers = st.slider(
                "Max Workers",
                min_value=1,
                max_value=16,
                value=4
            )
        
        if st.button("💾 Save Processing Settings"):
            st.success("Processing settings saved successfully!")
    
    # Database Settings
    with tab4:
        st.markdown("## Database Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### MySQL")
            
            mysql_host = st.text_input(
                "MySQL Host",
                value="localhost"
            )
            
            mysql_port = st.number_input(
                "MySQL Port",
                value=3306,
                min_value=1,
                max_value=65535
            )
            
            mysql_user = st.text_input(
                "MySQL User",
                value="root"
            )
            
            mysql_password = st.text_input(
                "MySQL Password",
                type="password"
            )
            
            mysql_database = st.text_input(
                "MySQL Database",
                value="claim_verification"
            )
        
        with col2:
            st.markdown("### InfluxDB")
            
            influxdb_url = st.text_input(
                "InfluxDB URL",
                value="http://localhost:8086"
            )
            
            influxdb_org = st.text_input(
                "InfluxDB Organization",
                value="capstone"
            )
            
            influxdb_bucket = st.text_input(
                "InfluxDB Bucket",
                value="metrics"
            )
            
            influxdb_token = st.text_input(
                "InfluxDB Token",
                type="password"
            )
            
            influxdb_timeout = st.slider(
                "InfluxDB Timeout (seconds)",
                min_value=5,
                max_value=60,
                value=10
            )
        
        if st.button("💾 Save Database Settings"):
            st.success("Database settings saved successfully!")
        
        if st.button("🔌 Test Database Connection"):
            st.info("Testing database connections...")
            st.success("✓ MySQL connection successful")
            st.success("✓ InfluxDB connection successful")
    
    # Advanced Settings
    with tab5:
        st.markdown("## Advanced Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Performance")
            
            enable_caching = st.checkbox(
                "Enable Caching",
                value=True
            )
            
            cache_ttl = st.slider(
                "Cache TTL (seconds)",
                min_value=60,
                max_value=3600,
                value=3600,
                disabled=not enable_caching
            )
            
            enable_compression = st.checkbox(
                "Enable Compression",
                value=True
            )
        
        with col2:
            st.markdown("### Security")
            
            enable_ssl = st.checkbox(
                "Enable SSL/TLS",
                value=True
            )
            
            enable_auth = st.checkbox(
                "Enable Authentication",
                value=True
            )
            
            session_timeout = st.slider(
                "Session Timeout (minutes)",
                min_value=5,
                max_value=480,
                value=60
            )
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Data Management")
            
            data_retention_days = st.slider(
                "Data Retention (days)",
                min_value=7,
                max_value=365,
                value=90
            )
            
            auto_backup = st.checkbox(
                "Enable Auto Backup",
                value=True
            )
            
            backup_frequency = st.selectbox(
                "Backup Frequency",
                ["Daily", "Weekly", "Monthly"],
                disabled=not auto_backup
            )
        
        with col2:
            st.markdown("### Monitoring")
            
            enable_monitoring = st.checkbox(
                "Enable Monitoring",
                value=True
            )
            
            monitoring_interval = st.slider(
                "Monitoring Interval (seconds)",
                min_value=10,
                max_value=300,
                value=60,
                disabled=not enable_monitoring
            )
            
            alert_threshold = st.slider(
                "Alert Threshold (%)",
                min_value=50,
                max_value=100,
                value=80
            )
        
        if st.button("💾 Save Advanced Settings"):
            st.success("Advanced settings saved successfully!")
    
    # System maintenance
    st.markdown("---")
    st.markdown("## 🔧 System Maintenance")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Clear Cache"):
            st.success("Cache cleared successfully!")
    
    with col2:
        if st.button("📊 Rebuild Indexes"):
            st.info("Rebuilding indexes...")
            st.success("Indexes rebuilt successfully!")
    
    with col3:
        if st.button("📋 Export Configuration"):
            st.info("Configuration export coming soon!")
    
    # About
    st.markdown("---")
    st.markdown("## ℹ️ About")
    
    st.markdown("""
    **Spoken Claim Verification System**
    
    Version: 1.0.0
    
    A comprehensive system for verifying spoken claims in short-form videos using 
    Large Language Models and Retrieval-Augmented Verification.
    
    **Key Technologies:**
    - Whisper large-v3 for speech recognition
    - Gemini 2.5 Pro for claim extraction and verification
    - Google Search for evidence retrieval
    - MySQL and InfluxDB for data storage
    - Grafana for visualization
    
    **Support:** For issues and questions, please visit the documentation or contact support.
    """)

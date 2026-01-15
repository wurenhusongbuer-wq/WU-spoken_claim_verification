"""
Monitoring Page

System monitoring and real-time metrics dashboard.

Author: Capstone Team
Date: 2024
"""

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd


def render():
    """Render monitoring page."""
    st.title("📊 System Monitoring")
    
    st.markdown("""
        Real-time system metrics and performance monitoring.
    """)
    
    # Auto-refresh
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.markdown("## System Metrics")
    
    with col2:
        if st.button("🔄 Refresh"):
            st.rerun()
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "API Status",
            "✓ Online",
            delta="Uptime: 99.9%"
        )
    
    with col2:
        st.metric(
            "Database Status",
            "✓ Connected",
            delta="Queries/min: 245"
        )
    
    with col3:
        st.metric(
            "Average Latency",
            "2.4s",
            delta="↓ 0.1s"
        )
    
    with col4:
        st.metric(
            "Claims/Hour",
            "487",
            delta="↑ 23"
        )
    
    # Performance metrics
    st.markdown("## 📈 Performance Metrics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Latency over time
        hours = [(datetime.now() - timedelta(hours=i)).strftime("%H:%M") for i in range(24, 0, -1)]
        latencies = [2.1, 2.2, 2.3, 2.2, 2.4, 2.3, 2.5, 2.2, 2.1, 2.3, 2.4, 2.2, 2.3, 2.4, 2.5, 2.3, 2.2, 2.4, 2.3, 2.2, 2.1, 2.3, 2.4, 2.4]
        
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=hours,
            y=latencies,
            mode='lines+markers',
            name='Latency',
            line=dict(color='#4c6ef5', width=2),
            marker=dict(size=6),
            fill='tozeroy'
        ))
        fig1.update_layout(
            title="Latency Trend (Last 24 Hours)",
            xaxis_title="Time",
            yaxis_title="Latency (seconds)",
            hovermode='x unified',
            height=300
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Throughput
        throughputs = [420, 445, 410, 465, 480, 490, 475, 460, 445, 430, 455, 470, 485, 495, 480, 465, 450, 440, 455, 470, 485, 490, 495, 487]
        
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=hours,
            y=throughputs,
            mode='lines+markers',
            name='Throughput',
            line=dict(color='#51cf66', width=2),
            marker=dict(size=6),
            fill='tozeroy'
        ))
        fig2.update_layout(
            title="Throughput Trend (Claims/Hour)",
            xaxis_title="Time",
            yaxis_title="Claims per Hour",
            hovermode='x unified',
            height=300
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # Component performance
    st.markdown("## 🔧 Component Performance")
    
    component_data = [
        {"Component": "Whisper ASR", "Avg Latency": 0.8, "Error Rate": 0.02, "Status": "✓"},
        {"Component": "Claim Extraction", "Avg Latency": 0.6, "Error Rate": 0.01, "Status": "✓"},
        {"Component": "Evidence Retrieval", "Avg Latency": 0.5, "Error Rate": 0.03, "Status": "✓"},
        {"Component": "Verification", "Avg Latency": 0.4, "Error Rate": 0.01, "Status": "✓"},
        {"Component": "Database", "Avg Latency": 0.05, "Error Rate": 0.0, "Status": "✓"},
    ]
    
    df_components = pd.DataFrame(component_data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Component latency
        fig3 = go.Figure(data=[go.Bar(
            x=df_components["Component"],
            y=df_components["Avg Latency"],
            marker=dict(color='#4c6ef5')
        )])
        fig3.update_layout(
            title="Component Latency",
            xaxis_title="Component",
            yaxis_title="Latency (seconds)",
            height=300
        )
        st.plotly_chart(fig3, use_container_width=True)
    
    with col2:
        # Error rates
        fig4 = go.Figure(data=[go.Bar(
            x=df_components["Component"],
            y=df_components["Error Rate"],
            marker=dict(color='#ff6b6b')
        )])
        fig4.update_layout(
            title="Component Error Rates",
            xaxis_title="Component",
            yaxis_title="Error Rate",
            height=300
        )
        st.plotly_chart(fig4, use_container_width=True)
    
    # Resource usage
    st.markdown("## 💾 Resource Usage")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("CPU Usage", "45%", delta="↑ 5%")
    
    with col2:
        st.metric("Memory Usage", "62%", delta="↑ 8%")
    
    with col3:
        st.metric("Disk Usage", "38%", delta="↑ 2%")
    
    with col4:
        st.metric("Network I/O", "125 MB/s", delta="↑ 15 MB/s")
    
    # API usage
    st.markdown("## 🔑 API Usage")
    
    api_data = [
        {"Service": "Google Gemini", "Requests": 1547, "Tokens": 245000, "Cost": "$8.50"},
        {"Service": "Google Search", "Requests": 1547, "Queries": 1547, "Cost": "$1.55"},
        {"Service": "Whisper ASR", "Requests": 150, "Minutes": 450, "Cost": "$0.45"},
    ]
    
    df_api = pd.DataFrame(api_data)
    
    st.dataframe(
        df_api,
        use_container_width=True,
        hide_index=True
    )
    
    # Error log
    st.markdown("## ⚠️ Recent Errors")
    
    error_data = [
        {"Time": "2024-01-15 14:23", "Component": "Evidence Retrieval", "Error": "API rate limit exceeded", "Status": "Resolved"},
        {"Time": "2024-01-15 12:45", "Component": "Database", "Error": "Connection timeout", "Status": "Resolved"},
        {"Time": "2024-01-15 10:12", "Component": "Whisper ASR", "Error": "Invalid audio format", "Status": "Resolved"},
    ]
    
    df_errors = pd.DataFrame(error_data)
    
    st.dataframe(
        df_errors,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Time": st.column_config.TextColumn("Time", width="small"),
            "Component": st.column_config.TextColumn("Component", width="medium"),
            "Error": st.column_config.TextColumn("Error", width="large"),
            "Status": st.column_config.TextColumn("Status", width="small"),
        }
    )
    
    # System health
    st.markdown("## 🏥 System Health")
    
    health_score = 98
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # Gauge chart
        fig5 = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=health_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Health Score"},
            delta={'reference': 95},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "#ff6b6b"},
                    {'range': [50, 80], 'color': "#ffd43b"},
                    {'range': [80, 100], 'color': "#51cf66"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        fig5.update_layout(height=300)
        st.plotly_chart(fig5, use_container_width=True)
    
    with col2:
        st.markdown("""
        ### Health Status
        
        **Overall Status**: ✓ Healthy
        
        **Key Indicators**:
        - API Availability: 99.9%
        - Database Connectivity: 100%
        - Average Response Time: 2.4s
        - Error Rate: < 1%
        
        **Recent Events**:
        - ✓ All systems operational
        - ✓ No critical alerts
        - ✓ Performance within SLA
        """)
    
    # Alerts
    st.markdown("## 🚨 Alerts")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("ℹ️ **Info**: Scheduled maintenance on 2024-01-20 at 02:00 UTC")
    
    with col2:
        st.warning("⚠️ **Warning**: High memory usage detected on database server")

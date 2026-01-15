"""
Results Page

Displays verification results and summary statistics.

Author: Capstone Team
Date: 2024
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime


def render():
    """Render results page."""
    st.title("📊 Verification Results")
    
    st.markdown("""
        View comprehensive verification results for processed videos.
    """)
    
    # Results filter
    st.markdown("## Filter Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.multiselect(
            "Verification Status",
            ["True", "False", "Uncertain"],
            default=["True", "False", "Uncertain"]
        )
    
    with col2:
        confidence_min = st.slider(
            "Minimum Confidence",
            min_value=0.0,
            max_value=1.0,
            value=0.0,
            step=0.05
        )
    
    with col3:
        date_range = st.date_input(
            "Date Range",
            value=(pd.Timestamp("2024-01-01"), pd.Timestamp("2024-12-31")),
            max_value=datetime.now()
        )
    
    # Results data
    results_data = [
        {
            "Video ID": "video_001",
            "Claim": "Global temperatures have risen by 1.1°C",
            "Label": "True",
            "Confidence": 0.95,
            "Processing Time": "2.3s",
            "Sources": 3,
            "Date": "2024-01-15"
        },
        {
            "Video ID": "video_001",
            "Claim": "Arctic sea ice declined by 13% per decade",
            "Label": "True",
            "Confidence": 0.92,
            "Processing Time": "2.1s",
            "Sources": 2,
            "Date": "2024-01-15"
        },
        {
            "Video ID": "video_002",
            "Claim": "COVID-19 was created in a lab",
            "Label": "False",
            "Confidence": 0.88,
            "Processing Time": "2.5s",
            "Sources": 4,
            "Date": "2024-01-14"
        },
        {
            "Video ID": "video_002",
            "Claim": "Vaccines contain microchips",
            "Label": "False",
            "Confidence": 0.91,
            "Processing Time": "2.2s",
            "Sources": 3,
            "Date": "2024-01-14"
        },
        {
            "Video ID": "video_003",
            "Claim": "The moon landing was faked",
            "Label": "False",
            "Confidence": 0.94,
            "Processing Time": "2.4s",
            "Sources": 5,
            "Date": "2024-01-13"
        },
        {
            "Video ID": "video_003",
            "Claim": "Climate change is real",
            "Label": "True",
            "Confidence": 0.96,
            "Processing Time": "2.0s",
            "Sources": 4,
            "Date": "2024-01-13"
        },
    ]
    
    df_results = pd.DataFrame(results_data)
    
    # Apply filters
    df_filtered = df_results[
        (df_results["Label"].isin(status_filter)) &
        (df_results["Confidence"] >= confidence_min)
    ]
    
    # Display results table
    st.markdown("## Results Table")
    
    st.dataframe(
        df_filtered,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Video ID": st.column_config.TextColumn("Video ID", width="small"),
            "Claim": st.column_config.TextColumn("Claim", width="large"),
            "Label": st.column_config.TextColumn("Label", width="small"),
            "Confidence": st.column_config.ProgressColumn("Confidence", min_value=0, max_value=1),
            "Processing Time": st.column_config.TextColumn("Time", width="small"),
            "Sources": st.column_config.NumberColumn("Sources", width="small"),
            "Date": st.column_config.TextColumn("Date", width="small"),
        }
    )
    
    # Summary statistics
    st.markdown("## 📈 Summary Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Results", len(df_filtered))
    
    with col2:
        true_count = len(df_filtered[df_filtered["Label"] == "True"])
        st.metric("True Claims", true_count)
    
    with col3:
        false_count = len(df_filtered[df_filtered["Label"] == "False"])
        st.metric("False Claims", false_count)
    
    with col4:
        avg_confidence = df_filtered["Confidence"].mean()
        st.metric("Avg Confidence", f"{avg_confidence:.1%}")
    
    # Visualization
    st.markdown("## 📊 Visualizations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Label distribution
        label_counts = df_filtered["Label"].value_counts()
        colors = {"True": "#51cf66", "False": "#ff6b6b", "Uncertain": "#ffd43b"}
        
        fig1 = go.Figure(data=[go.Pie(
            labels=label_counts.index,
            values=label_counts.values,
            marker=dict(colors=[colors.get(label, "#999") for label in label_counts.index]),
            textposition='inside',
            textinfo='label+percent'
        )])
        fig1.update_layout(title="Verification Results Distribution", height=400)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Confidence distribution by label
        fig2 = go.Figure()
        
        for label in df_filtered["Label"].unique():
            data = df_filtered[df_filtered["Label"] == label]["Confidence"]
            fig2.add_trace(go.Box(
                y=data,
                name=label,
                marker=dict(color=colors.get(label, "#999"))
            ))
        
        fig2.update_layout(
            title="Confidence Distribution by Label",
            yaxis_title="Confidence Score",
            height=400
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # Processing time analysis
    st.markdown("## ⏱️ Processing Time Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Processing time trend
        df_filtered["Processing Time (s)"] = df_filtered["Processing Time"].str.replace("s", "").astype(float)
        
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            y=df_filtered["Processing Time (s)"],
            mode='lines+markers',
            name='Processing Time',
            line=dict(color='#4c6ef5', width=2),
            marker=dict(size=8)
        ))
        fig3.update_layout(
            title="Processing Time Trend",
            xaxis_title="Claim Index",
            yaxis_title="Time (seconds)",
            height=300
        )
        st.plotly_chart(fig3, use_container_width=True)
    
    with col2:
        # Average metrics
        avg_time = df_filtered["Processing Time (s)"].mean()
        avg_sources = df_filtered["Sources"].mean()
        
        st.metric("Average Processing Time", f"{avg_time:.2f}s")
        st.metric("Average Sources Used", f"{avg_sources:.1f}")
    
    # Detailed view
    st.markdown("## 🔍 Detailed View")
    
    selected_result = st.selectbox(
        "Select a result to view details",
        range(len(df_filtered)),
        format_func=lambda i: f"{df_filtered.iloc[i]['Video ID']} - {df_filtered.iloc[i]['Claim'][:50]}..."
    )
    
    result = df_filtered.iloc[selected_result]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Video ID", result["Video ID"])
    
    with col2:
        st.metric("Label", result["Label"])
    
    with col3:
        st.metric("Confidence", f"{result['Confidence']:.1%}")
    
    with col4:
        st.metric("Processing Time", result["Processing Time"])
    
    st.markdown("### Claim")
    st.info(result["Claim"])
    
    # Export options
    st.markdown("## 💾 Export Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 Export as CSV"):
            csv = df_filtered.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="verification_results.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("📥 Export as JSON"):
            import json
            json_data = df_filtered.to_json(orient="records", indent=2)
            st.download_button(
                label="Download JSON",
                data=json_data,
                file_name="verification_results.json",
                mime="application/json"
            )
    
    with col3:
        if st.button("📥 Export as Excel"):
            st.info("Excel export coming soon!")

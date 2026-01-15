"""
Analysis Page

Displays detailed analysis of claims and verification process.

Author: Capstone Team
Date: 2024
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go


def render():
    """Render analysis page."""
    st.title("🔍 Claim Analysis")
    
    st.markdown("""
        Detailed analysis of extracted claims and verification process.
    """)
    
    # Video selection
    st.markdown("## Select Video")
    
    video_id = st.selectbox(
        "Choose a video to analyze",
        ["video_001", "video_002", "video_003", "video_004", "video_005"],
        key="video_select"
    )
    
    # Transcript section
    st.markdown("## 📝 Transcript")
    
    with st.expander("View Full Transcript", expanded=False):
        transcript = """
        Welcome to our discussion about climate change. Recent studies show that global temperatures 
        have risen by approximately 1.1 degrees Celsius since pre-industrial times. This is primarily 
        due to human activities, particularly the emission of greenhouse gases. The IPCC reports that 
        we have only a limited time window to prevent catastrophic climate impacts.
        
        According to NASA data, Arctic sea ice has declined by about 13% per decade over the last 40 years. 
        This is one of the most visible indicators of climate change. Additionally, sea levels are rising 
        at an accelerating rate, threatening coastal communities worldwide.
        
        However, some argue that climate change is a natural cycle. But the scientific consensus is clear: 
        the current warming trend is unprecedented in at least the last 2,000 years.
        """
        st.text_area("Full Transcript", value=transcript, height=200, disabled=True)
    
    # Claims extraction
    st.markdown("## 🎯 Extracted Claims")
    
    claims_data = [
        {
            "ID": "claim_001",
            "Claim": "Global temperatures have risen by approximately 1.1 degrees Celsius since pre-industrial times",
            "Type": "Statistical",
            "Confidence": 0.95,
            "Status": "Verified"
        },
        {
            "ID": "claim_002",
            "Claim": "Human activities are primarily responsible for global warming",
            "Type": "Factual",
            "Confidence": 0.92,
            "Status": "Verified"
        },
        {
            "ID": "claim_003",
            "Claim": "Arctic sea ice has declined by about 13% per decade over the last 40 years",
            "Type": "Statistical",
            "Confidence": 0.88,
            "Status": "Verified"
        },
        {
            "ID": "claim_004",
            "Claim": "Sea levels are rising at an accelerating rate",
            "Type": "Factual",
            "Confidence": 0.85,
            "Status": "Verified"
        },
        {
            "ID": "claim_005",
            "Claim": "Current warming trend is unprecedented in at least the last 2,000 years",
            "Type": "Factual",
            "Confidence": 0.87,
            "Status": "Verified"
        },
    ]
    
    df_claims = pd.DataFrame(claims_data)
    
    # Display claims table
    st.dataframe(
        df_claims,
        use_container_width=True,
        hide_index=True,
        column_config={
            "ID": st.column_config.TextColumn("ID", width="small"),
            "Claim": st.column_config.TextColumn("Claim", width="large"),
            "Type": st.column_config.TextColumn("Type", width="small"),
            "Confidence": st.column_config.ProgressColumn("Confidence", min_value=0, max_value=1),
            "Status": st.column_config.TextColumn("Status", width="small"),
        }
    )
    
    # Claim details
    st.markdown("## 📋 Claim Details")
    
    selected_claim = st.selectbox(
        "Select a claim to view details",
        df_claims["ID"].tolist(),
        format_func=lambda x: f"{x} - {df_claims[df_claims['ID']==x]['Claim'].values[0][:50]}..."
    )
    
    claim_row = df_claims[df_claims["ID"] == selected_claim].iloc[0]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Claim ID", claim_row["ID"])
    
    with col2:
        st.metric("Type", claim_row["Type"])
    
    with col3:
        st.metric("Confidence", f"{claim_row['Confidence']:.1%}")
    
    with col4:
        st.metric("Status", claim_row["Status"])
    
    st.markdown("### Full Claim Text")
    st.info(claim_row["Claim"])
    
    # Evidence section
    st.markdown("### Evidence Retrieved")
    
    evidence_data = [
        {
            "Rank": 1,
            "Source": "NASA - Global Climate Change",
            "Snippet": "Global temperatures have risen approximately 1.1 degrees Celsius since pre-industrial times...",
            "Relevance": 0.95,
            "Domain Authority": 0.95
        },
        {
            "Rank": 2,
            "Source": "IPCC - Climate Change 2023 Report",
            "Snippet": "It is unequivocal that human influence has warmed the climate system...",
            "Relevance": 0.92,
            "Domain Authority": 0.95
        },
        {
            "Rank": 3,
            "Source": "National Geographic - Climate Facts",
            "Snippet": "Scientific evidence shows that the climate is changing...",
            "Relevance": 0.88,
            "Domain Authority": 0.90
        },
    ]
    
    df_evidence = pd.DataFrame(evidence_data)
    
    st.dataframe(
        df_evidence,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Rank": st.column_config.NumberColumn("Rank", width="small"),
            "Source": st.column_config.TextColumn("Source", width="large"),
            "Snippet": st.column_config.TextColumn("Snippet", width="large"),
            "Relevance": st.column_config.ProgressColumn("Relevance", min_value=0, max_value=1),
            "Domain Authority": st.column_config.ProgressColumn("Authority", min_value=0, max_value=1),
        }
    )
    
    # Verification result
    st.markdown("### Verification Result")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Label", "✓ TRUE")
    
    with col2:
        st.metric("Confidence", "92%")
    
    with col3:
        st.metric("Processing Time", "2.4s")
    
    st.markdown("### Explanation")
    st.success("""
    This claim is supported by multiple authoritative sources including NASA and the IPCC. 
    The 1.1°C warming figure is consistent with data from the most recent climate reports. 
    The evidence strongly supports this claim.
    """)
    
    st.markdown("### Citations")
    st.markdown("""
    1. NASA Global Climate Change: https://climate.nasa.gov/
    2. IPCC Sixth Assessment Report: https://www.ipcc.ch/
    3. National Geographic Climate Facts: https://www.nationalgeographic.com/climate/
    """)
    
    # Claim statistics
    st.markdown("## 📊 Claim Statistics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Claim type distribution
        claim_types = df_claims["Type"].value_counts()
        
        fig1 = go.Figure(data=[go.Bar(
            x=claim_types.index,
            y=claim_types.values,
            marker=dict(color=['#ff6b6b', '#51cf66', '#ffd43b'])
        )])
        fig1.update_layout(
            title="Claims by Type",
            xaxis_title="Type",
            yaxis_title="Count",
            height=300
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Confidence distribution
        fig2 = go.Figure(data=[go.Histogram(
            x=df_claims["Confidence"],
            nbinsx=10,
            marker=dict(color='#4c6ef5')
        )])
        fig2.update_layout(
            title="Confidence Distribution",
            xaxis_title="Confidence Score",
            yaxis_title="Number of Claims",
            height=300
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # Export options
    st.markdown("## 💾 Export Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 Export as CSV"):
            csv = df_claims.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"{video_id}_claims.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("📥 Export as JSON"):
            import json
            json_data = df_claims.to_json(orient="records", indent=2)
            st.download_button(
                label="Download JSON",
                data=json_data,
                file_name=f"{video_id}_claims.json",
                mime="application/json"
            )
    
    with col3:
        if st.button("📥 Export as PDF"):
            st.info("PDF export coming soon!")

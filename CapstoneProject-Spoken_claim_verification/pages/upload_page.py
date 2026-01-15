"""
Upload Video Page

Allows users to upload and process videos.

Author: Capstone Team
Date: 2024
"""

import streamlit as st
import os
from pathlib import Path
from datetime import datetime


def render():
    """Render upload page."""
    st.title("📤 Upload Video")
    
    st.markdown("""
        Upload a video file to begin the claim verification process.
        The system will automatically extract audio, transcribe, extract claims, and verify them.
    """)
    
    # Upload section
    st.markdown("## Video Upload")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Choose a video file",
            type=["mp4", "avi", "mov", "mkv", "webm"],
            help="Supported formats: MP4, AVI, MOV, MKV, WebM (Max 500MB)"
        )
    
    with col2:
        st.info(f"Max file size: 500MB")
    
    if uploaded_file is not None:
        # Display file info
        st.markdown("### File Information")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("File Name", uploaded_file.name)
        
        with col2:
            file_size_mb = uploaded_file.size / (1024 * 1024)
            st.metric("File Size", f"{file_size_mb:.2f} MB")
        
        with col3:
            st.metric("File Type", uploaded_file.type)
        
        # Video preview
        st.markdown("### Video Preview")
        st.video(uploaded_file)
        
        # Processing options
        st.markdown("### Processing Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            video_id = st.text_input(
                "Video ID",
                value=f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                help="Unique identifier for this video"
            )
        
        with col2:
            language = st.selectbox(
                "Language",
                ["English", "Chinese", "Spanish", "French", "German"],
                help="Language of the video content"
            )
        
        # Advanced options
        with st.expander("Advanced Options"):
            col1, col2 = st.columns(2)
            
            with col1:
                sample_rate = st.slider(
                    "Audio Sample Rate (Hz)",
                    min_value=8000,
                    max_value=48000,
                    value=16000,
                    step=1000
                )
            
            with col2:
                confidence_threshold = st.slider(
                    "Confidence Threshold",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.5,
                    step=0.05
                )
            
            save_to_db = st.checkbox(
                "Save results to database",
                value=True
            )
            
            extract_full_text = st.checkbox(
                "Extract full text from evidence sources",
                value=False,
                help="This may increase processing time"
            )
        
        # Processing button
        st.markdown("### Start Processing")
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("🚀 Process Video", key="process_btn", use_container_width=True):
                st.session_state.processing = True
                st.session_state.video_id = video_id
        
        with col2:
            if st.button("📋 Preview", key="preview_btn", use_container_width=True):
                st.info("Preview feature coming soon!")
        
        # Processing progress
        if st.session_state.get('processing', False):
            st.markdown("### Processing Progress")
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Simulate processing steps
            steps = [
                ("Saving video file", 0.1),
                ("Extracting audio", 0.2),
                ("Transcribing audio", 0.5),
                ("Extracting claims", 0.7),
                ("Retrieving evidence", 0.85),
                ("Verifying claims", 0.95),
                ("Saving results", 1.0),
            ]
            
            for step_name, progress in steps:
                status_text.text(f"Status: {step_name}...")
                progress_bar.progress(progress)
                import time
                time.sleep(0.3)
            
            status_text.text("✓ Processing completed!")
            st.success(f"Video {video_id} processed successfully!")
            
            # Show results summary
            st.markdown("### Results Summary")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Claims Extracted", "12")
            
            with col2:
                st.metric("Verified Claims", "11")
            
            with col3:
                st.metric("Processing Time", "28.4s")
            
            with col4:
                st.metric("Avg Latency/Claim", "2.37s")
            
            # Next steps
            st.markdown("### Next Steps")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📊 View Detailed Results"):
                    st.info("Redirecting to Results page...")
            
            with col2:
                if st.button("📈 View Analytics"):
                    st.info("Redirecting to Monitoring page...")
    
    else:
        # Empty state
        st.markdown("### 📁 No file selected")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **Supported Formats:**
            - MP4
            - AVI
            - MOV
            - MKV
            - WebM
            """)
        
        with col2:
            st.markdown("""
            **Requirements:**
            - Max size: 500MB
            - Audio required
            - Spoken content
            """)
        
        with col3:
            st.markdown("""
            **Tips:**
            - Use clear audio
            - Avoid background noise
            - Ensure good lighting
            """)
    
    # Processing guidelines
    st.markdown("---")
    st.markdown("## 📋 Processing Guidelines")
    
    st.markdown("""
    ### Before Uploading
    - Ensure the video contains clear spoken content
    - Check that audio quality is good
    - Verify file format is supported
    
    ### Processing Steps
    1. **Audio Extraction**: Extract audio track from video
    2. **Transcription**: Convert speech to text using Whisper
    3. **Claim Extraction**: Identify atomic claims from transcript
    4. **Evidence Retrieval**: Search for web evidence for each claim
    5. **Verification**: Verify claims using LLM and evidence
    6. **Storage**: Save results to database
    
    ### Expected Timeline
    - Small videos (< 5 min): ~1-2 minutes
    - Medium videos (5-15 min): ~3-5 minutes
    - Large videos (> 15 min): ~5-10 minutes
    """)

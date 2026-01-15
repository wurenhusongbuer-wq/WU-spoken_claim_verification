"""
Whisper Speech Recognition Service

This module provides a FastAPI-based service for speech-to-text transcription
using OpenAI's Whisper model. It handles audio file processing and returns
structured transcription results with timing information.

Author: Capstone Team
Date: 2024
"""

import os
import logging
from typing import Optional
from pathlib import Path
import time

import whisper
from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Whisper Speech Recognition Service")

# Global model instance
whisper_model = None


class TranscriptionResponse(BaseModel):
    """Response model for transcription results."""
    text: str
    language: str
    duration: float
    processing_time: float
    segments: list = []


def load_model(model_name: str = "large-v3"):
    """
    Load Whisper model into memory.
    
    Args:
        model_name: Name of the Whisper model to load
        
    Returns:
        Loaded Whisper model
    """
    global whisper_model
    if whisper_model is None:
        logger.info(f"Loading Whisper model: {model_name}")
        whisper_model = whisper.load_model(model_name)
        logger.info("Model loaded successfully")
    return whisper_model


@app.on_event("startup")
async def startup_event():
    """Load model on application startup."""
    load_model()
    logger.info("Whisper service started")


@app.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe(file: UploadFile = File(...)):
    """
    Transcribe audio file using Whisper model.
    
    Args:
        file: Audio file to transcribe (WAV, MP3, M4A, FLAC, etc.)
        
    Returns:
        TranscriptionResponse with transcribed text and metadata
        
    Raises:
        HTTPException: If file processing fails
    """
    temp_file_path = None
    try:
        # Save uploaded file temporarily
        temp_file_path = f"/tmp/{file.filename}"
        with open(temp_file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        logger.info(f"Processing audio file: {file.filename}")
        start_time = time.time()
        
        # Transcribe audio
        result = whisper_model.transcribe(temp_file_path)
        
        processing_time = time.time() - start_time
        
        logger.info(f"Transcription completed in {processing_time:.2f}s")
        
        return TranscriptionResponse(
            text=result["text"],
            language=result.get("language", "unknown"),
            duration=result.get("duration", 0),
            processing_time=processing_time,
            segments=result.get("segments", [])
        )
        
    except Exception as e:
        logger.error(f"Transcription error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Whisper Speech Recognition",
        "model_loaded": whisper_model is not None
    }


if __name__ == "__main__":
    port = int(os.getenv("WHISPER_PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)

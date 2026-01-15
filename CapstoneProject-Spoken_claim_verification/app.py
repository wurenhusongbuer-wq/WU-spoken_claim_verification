"""
Main Application Entry Point

This is the central orchestration module for the spoken claim verification system.
It coordinates all components: speech recognition, claim extraction, evidence retrieval,
and verification.

Author: Capstone Team
Date: 2024
"""

import os
import logging
import json
import time
from typing import Dict, List, Optional
from pathlib import Path
from dataclasses import asdict

import requests
from dotenv import load_dotenv

from components import (
    GeminiService,
    EvidenceRetriever,
    EvidenceReranker,
    BaselineModel
)
from utils import (
    WERCalculator,
    DataFetcher,
    MySQLManager,
    InfluxDBManager
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ClaimVerificationPipeline:
    """Main pipeline for claim verification."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize the pipeline.
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.load_config()
        
        # Initialize components
        self.gemini_service = GeminiService()
        self.evidence_retriever = EvidenceRetriever()
        self.evidence_reranker = EvidenceReranker()
        self.baseline_model = BaselineModel()
        self.data_fetcher = DataFetcher()
        
        # Initialize database managers
        self.mysql_manager = MySQLManager(
            host=os.getenv("MYSQL_HOST", "localhost"),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD", ""),
            database=os.getenv("MYSQL_DB", "claim_verification")
        )
        
        self.influxdb_manager = InfluxDBManager(
            url=os.getenv("INFLUXDB_URL", "http://localhost:8086"),
            token=os.getenv("INFLUXDB_TOKEN", ""),
            org=os.getenv("INFLUXDB_ORG", "capstone"),
            bucket=os.getenv("INFLUXDB_BUCKET", "metrics")
        )
        
        logger.info("Pipeline initialized successfully")
    
    def load_config(self) -> None:
        """Load configuration from YAML file."""
        try:
            import yaml
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    self.config = yaml.safe_load(f)
                logger.info(f"Configuration loaded from {self.config_path}")
            else:
                self.config = self.get_default_config()
                logger.info("Using default configuration")
        except ImportError:
            logger.warning("PyYAML not installed, using default config")
            self.config = self.get_default_config()
    
    @staticmethod
    def get_default_config() -> Dict:
        """Get default configuration."""
        return {
            "whisper": {
                "model": "large-v3",
                "language": "en"
            },
            "gemini": {
                "temperature": 0.3,
                "max_tokens": 2000
            },
            "evidence_retrieval": {
                "num_results": 5,
                "extract_full_text": False
            },
            "verification": {
                "confidence_threshold": 0.5
            }
        }
    
    def transcribe_audio(self, audio_path: str) -> Optional[str]:
        """
        Transcribe audio file using Whisper service.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Transcribed text or None if failed
        """
        try:
            logger.info(f"Transcribing audio: {audio_path}")
            start_time = time.time()
            
            # Call Whisper service
            whisper_url = os.getenv("WHISPER_SERVICE_URL", "http://localhost:8001")
            
            with open(audio_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(
                    f"{whisper_url}/transcribe",
                    files=files,
                    timeout=300
                )
            
            response.raise_for_status()
            result = response.json()
            
            latency = time.time() - start_time
            
            # Log latency metric
            self.influxdb_manager.write_latency_metric(
                component="whisper",
                latency_ms=latency * 1000
            )
            
            logger.info(f"Transcription completed in {latency:.2f}s")
            return result.get("text")
            
        except Exception as e:
            logger.error(f"Transcription error: {str(e)}")
            return None
    
    def extract_claims(self, transcript: str) -> List[Dict]:
        """
        Extract claims from transcript.
        
        Args:
            transcript: Transcript text
            
        Returns:
            List of extracted claims
        """
        try:
            logger.info("Extracting claims from transcript")
            start_time = time.time()
            
            claims = self.gemini_service.extract_claims(
                transcript,
                temperature=self.config["gemini"]["temperature"]
            )
            
            latency = time.time() - start_time
            
            # Log latency metric
            self.influxdb_manager.write_latency_metric(
                component="claim_extraction",
                latency_ms=latency * 1000
            )
            
            logger.info(f"Extracted {len(claims)} claims in {latency:.2f}s")
            
            return [asdict(c) for c in claims]
            
        except Exception as e:
            logger.error(f"Claim extraction error: {str(e)}")
            return []
    
    def retrieve_evidence(self, claims: List[str]) -> Dict[str, Dict]:
        """
        Retrieve evidence for claims.
        
        Args:
            claims: List of claim texts
            
        Returns:
            Dictionary mapping claims to evidence
        """
        try:
            logger.info(f"Retrieving evidence for {len(claims)} claims")
            start_time = time.time()
            
            evidence_results = self.evidence_retriever.batch_retrieve_evidence(
                claims,
                num_results=self.config["evidence_retrieval"]["num_results"],
                extract_full_text=self.config["evidence_retrieval"]["extract_full_text"]
            )
            
            latency = time.time() - start_time
            
            # Log latency metric
            self.influxdb_manager.write_latency_metric(
                component="evidence_retrieval",
                latency_ms=latency * 1000
            )
            
            logger.info(f"Evidence retrieved in {latency:.2f}s")
            
            return {r["claim"]: r for r in evidence_results}
            
        except Exception as e:
            logger.error(f"Evidence retrieval error: {str(e)}")
            return {}
    
    def verify_claims(
        self,
        claims: List[str],
        evidence_dict: Dict[str, Dict]
    ) -> List[Dict]:
        """
        Verify claims using evidence.
        
        Args:
            claims: List of claim texts
            evidence_dict: Dictionary mapping claims to evidence
            
        Returns:
            List of verification results
        """
        try:
            logger.info(f"Verifying {len(claims)} claims")
            start_time = time.time()
            
            results = []
            
            for claim in claims:
                evidence = evidence_dict.get(claim, {})
                evidence_text = evidence.get("evidence_text", "")
                
                # Verify using Gemini
                verification = self.gemini_service.verify_claim(claim, evidence_text)
                
                result = {
                    "claim": claim,
                    "label": verification.label,
                    "confidence": verification.confidence,
                    "explanation": verification.explanation,
                    "citations": verification.citations,
                    "sources": evidence.get("sources", [])
                }
                
                results.append(result)
            
            latency = time.time() - start_time
            
            # Log latency metric
            self.influxdb_manager.write_latency_metric(
                component="verification",
                latency_ms=latency * 1000
            )
            
            logger.info(f"Verification completed in {latency:.2f}s")
            
            return results
            
        except Exception as e:
            logger.error(f"Verification error: {str(e)}")
            return []
    
    def process_video(
        self,
        video_path: str,
        video_id: str,
        save_to_db: bool = True
    ) -> Dict:
        """
        Process a complete video through the pipeline.
        
        Args:
            video_path: Path to video file
            video_id: Video identifier
            save_to_db: Whether to save results to database
            
        Returns:
            Dictionary with processing results
        """
        logger.info(f"Processing video: {video_id}")
        pipeline_start = time.time()
        
        results = {
            "video_id": video_id,
            "status": "processing",
            "transcript": None,
            "claims": [],
            "evidence": {},
            "verifications": [],
            "total_time": 0
        }
        
        try:
            # Extract audio
            audio_path = self.data_fetcher.extract_audio(video_path)
            if not audio_path:
                results["status"] = "failed"
                results["error"] = "Audio extraction failed"
                return results
            
            # Transcribe
            transcript = self.transcribe_audio(audio_path)
            if not transcript:
                results["status"] = "failed"
                results["error"] = "Transcription failed"
                return results
            
            results["transcript"] = transcript
            
            # Extract claims
            claims_data = self.extract_claims(transcript)
            claims = [c["text"] for c in claims_data]
            results["claims"] = claims_data
            
            if not claims:
                results["status"] = "completed"
                results["total_time"] = time.time() - pipeline_start
                return results
            
            # Retrieve evidence
            evidence_dict = self.retrieve_evidence(claims)
            results["evidence"] = evidence_dict
            
            # Verify claims
            verifications = self.verify_claims(claims, evidence_dict)
            results["verifications"] = verifications
            
            # Save to database if requested
            if save_to_db:
                self.save_results_to_db(video_id, results)
            
            results["status"] = "completed"
            results["total_time"] = time.time() - pipeline_start
            
            logger.info(f"Video processing completed in {results['total_time']:.2f}s")
            
        except Exception as e:
            logger.error(f"Pipeline error: {str(e)}")
            results["status"] = "failed"
            results["error"] = str(e)
        
        return results
    
    def save_results_to_db(self, video_id: str, results: Dict) -> None:
        """
        Save processing results to database.
        
        Args:
            video_id: Video identifier
            results: Processing results
        """
        try:
            for claim_data in results.get("claims", []):
                claim_id = self.mysql_manager.insert_claim(
                    video_id=video_id,
                    claim_text=claim_data["text"],
                    claim_type=claim_data.get("claim_type", "factual"),
                    confidence=claim_data.get("confidence", 0.0)
                )
                
                if claim_id:
                    # Find corresponding verification
                    for verification in results.get("verifications", []):
                        if verification["claim"] == claim_data["text"]:
                            self.mysql_manager.insert_verification(
                                claim_id=claim_id,
                                label=verification["label"],
                                confidence=verification["confidence"],
                                explanation=verification["explanation"],
                                citations=verification.get("citations", [])
                            )
                            break
            
            logger.info(f"Results saved to database for video: {video_id}")
        except Exception as e:
            logger.error(f"Error saving results to database: {str(e)}")
    
    def cleanup(self) -> None:
        """Clean up resources."""
        self.mysql_manager.disconnect()
        self.influxdb_manager.disconnect()
        logger.info("Pipeline cleanup completed")


def main():
    """Main entry point."""
    # Initialize pipeline
    pipeline = ClaimVerificationPipeline()
    
    # Example: Process a video
    # video_path = "path/to/video.mp4"
    # results = pipeline.process_video(video_path, "video_001")
    # print(json.dumps(results, indent=2))
    
    # Cleanup
    pipeline.cleanup()


if __name__ == "__main__":
    main()

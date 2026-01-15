"""
Gemini Service for Claim Extraction and Verification

This module provides interfaces to Google's Gemini API for:
1. Extracting atomic claims from transcripts
2. Verifying claims with evidence

Author: Capstone Team
Date: 2024
"""

import os
import json
import logging
import time
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

import google.generativeai as genai
from pydantic import BaseModel

logger = logging.getLogger(__name__)


@dataclass
class Claim:
    """Represents a single atomic claim extracted from transcript."""
    claim_id: str
    text: str
    confidence: float
    claim_type: str


@dataclass
class VerificationResult:
    """Represents verification result for a claim."""
    claim_id: str
    claim_text: str
    label: str  # "true", "false", "uncertain"
    confidence: float
    explanation: str
    citations: List[str]
    evidence_used: str


class ClaimExtractionPrompt(BaseModel):
    """Prompt template for claim extraction."""
    system_message: str = """You are an expert fact-checker and claim analyzer. Your task is to extract 
atomic, verifiable claims from transcripts. Each claim should be:
1. A single, standalone statement that can be verified independently
2. Specific and measurable
3. Free of hedging language (unless the speaker explicitly hedged)
4. Extractable as a complete thought

Return results as a JSON array with the following structure:
{
    "claims": [
        {
            "claim_id": "claim_001",
            "text": "The claim text",
            "confidence": 0.95,
            "claim_type": "factual/statistical/opinion"
        }
    ]
}"""
    
    user_template: str = """Extract atomic claims from the following transcript:

TRANSCRIPT:
{transcript}

Return only valid JSON."""


class VerificationPrompt(BaseModel):
    """Prompt template for claim verification."""
    system_message: str = """You are an expert fact-checker. Your task is to verify claims using provided evidence.
For each claim, provide:
1. A verdict (true/false/uncertain)
2. Confidence score (0-1)
3. Clear explanation
4. Citations from the evidence

Return results as JSON with this structure:
{
    "verification": {
        "claim_id": "claim_001",
        "label": "true|false|uncertain",
        "confidence": 0.85,
        "explanation": "Detailed explanation",
        "citations": ["source 1", "source 2"]
    }
}"""
    
    user_template: str = """Verify the following claim using the provided evidence:

CLAIM:
{claim}

EVIDENCE:
{evidence}

Provide your verification result in JSON format."""


class GeminiService:
    """Service for interacting with Google Gemini API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini service.
        
        Args:
            api_key: Google API key. If None, uses GOOGLE_API_KEY environment variable
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-2.5-pro")
        logger.info("Gemini service initialized")
    
    def extract_claims(
        self,
        transcript: str,
        temperature: float = 0.3,
        max_tokens: int = 2000
    ) -> List[Claim]:
        """
        Extract atomic claims from transcript.
        
        Args:
            transcript: Text transcript to extract claims from
            temperature: Model temperature (0-1)
            max_tokens: Maximum tokens in response
            
        Returns:
            List of extracted claims
            
        Raises:
            ValueError: If API response cannot be parsed
        """
        prompt = ClaimExtractionPrompt()
        
        try:
            start_time = time.time()
            
            response = self.model.generate_content(
                f"{prompt.system_message}\n\n{prompt.user_template.format(transcript=transcript)}",
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                    "top_p": 0.95,
                }
            )
            
            processing_time = time.time() - start_time
            logger.info(f"Claim extraction completed in {processing_time:.2f}s")
            
            # Parse response
            response_text = response.text
            
            # Extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")
            
            json_str = response_text[json_start:json_end]
            result = json.loads(json_str)
            
            claims = [
                Claim(
                    claim_id=c.get("claim_id", f"claim_{i:03d}"),
                    text=c.get("text", ""),
                    confidence=c.get("confidence", 0.0),
                    claim_type=c.get("claim_type", "factual")
                )
                for i, c in enumerate(result.get("claims", []))
            ]
            
            logger.info(f"Extracted {len(claims)} claims")
            return claims
            
        except Exception as e:
            logger.error(f"Error extracting claims: {str(e)}")
            raise
    
    def verify_claim(
        self,
        claim: str,
        evidence: str,
        temperature: float = 0.3,
        max_tokens: int = 1500
    ) -> VerificationResult:
        """
        Verify a claim using provided evidence.
        
        Args:
            claim: Claim text to verify
            evidence: Evidence text to use for verification
            temperature: Model temperature (0-1)
            max_tokens: Maximum tokens in response
            
        Returns:
            VerificationResult with verdict and explanation
            
        Raises:
            ValueError: If API response cannot be parsed
        """
        prompt = VerificationPrompt()
        
        try:
            start_time = time.time()
            
            response = self.model.generate_content(
                f"{prompt.system_message}\n\n{prompt.user_template.format(claim=claim, evidence=evidence)}",
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                    "top_p": 0.95,
                }
            )
            
            processing_time = time.time() - start_time
            logger.info(f"Claim verification completed in {processing_time:.2f}s")
            
            # Parse response
            response_text = response.text
            
            # Extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")
            
            json_str = response_text[json_start:json_end]
            result = json.loads(json_str)
            
            verification = result.get("verification", {})
            
            return VerificationResult(
                claim_id=verification.get("claim_id", "unknown"),
                claim_text=claim,
                label=verification.get("label", "uncertain"),
                confidence=verification.get("confidence", 0.0),
                explanation=verification.get("explanation", ""),
                citations=verification.get("citations", []),
                evidence_used=evidence[:500]  # Store first 500 chars of evidence
            )
            
        except Exception as e:
            logger.error(f"Error verifying claim: {str(e)}")
            raise
    
    def batch_extract_claims(
        self,
        transcripts: List[str],
        temperature: float = 0.3
    ) -> Dict[str, List[Claim]]:
        """
        Extract claims from multiple transcripts.
        
        Args:
            transcripts: List of transcripts
            temperature: Model temperature
            
        Returns:
            Dictionary mapping transcript index to list of claims
        """
        results = {}
        for i, transcript in enumerate(transcripts):
            try:
                claims = self.extract_claims(transcript, temperature=temperature)
                results[f"transcript_{i}"] = claims
            except Exception as e:
                logger.error(f"Error processing transcript {i}: {str(e)}")
                results[f"transcript_{i}"] = []
        
        return results
    
    def batch_verify_claims(
        self,
        claims_with_evidence: List[tuple],
        temperature: float = 0.3
    ) -> List[VerificationResult]:
        """
        Verify multiple claims with their evidence.
        
        Args:
            claims_with_evidence: List of (claim, evidence) tuples
            temperature: Model temperature
            
        Returns:
            List of verification results
        """
        results = []
        for claim, evidence in claims_with_evidence:
            try:
                result = self.verify_claim(claim, evidence, temperature=temperature)
                results.append(result)
            except Exception as e:
                logger.error(f"Error verifying claim '{claim[:50]}...': {str(e)}")
        
        return results

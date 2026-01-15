"""
Baseline Model for Claim Verification

This module provides a simple baseline model for claim verification
based on keyword matching and heuristics. Used for comparison with LLM-based approach.

Author: Capstone Team
Date: 2024
"""

import logging
import re
from typing import Dict, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class BaselineVerification:
    """Result from baseline verification."""
    claim: str
    label: str  # "true", "false", "uncertain"
    confidence: float
    reasoning: str


class BaselineModel:
    """Simple baseline model for claim verification."""
    
    # Keywords indicating true claims
    TRUE_KEYWORDS = {
        "confirmed", "verified", "proven", "established", "documented",
        "official", "according to", "research shows", "studies indicate",
        "evidence suggests", "data shows", "statistics show"
    }
    
    # Keywords indicating false claims
    FALSE_KEYWORDS = {
        "debunked", "false", "hoax", "fake", "misleading", "incorrect",
        "disproven", "contradicts", "denies", "refutes", "disputed"
    }
    
    # Uncertainty keywords
    UNCERTAIN_KEYWORDS = {
        "may", "might", "could", "possibly", "allegedly", "reportedly",
        "unclear", "uncertain", "unknown", "unverified", "unconfirmed"
    }
    
    def __init__(self):
        """Initialize baseline model."""
        logger.info("Baseline model initialized")
    
    def count_keyword_matches(self, text: str, keywords: set) -> int:
        """
        Count keyword matches in text.
        
        Args:
            text: Text to search
            keywords: Set of keywords to match
            
        Returns:
            Number of matches
        """
        text_lower = text.lower()
        count = 0
        for keyword in keywords:
            count += len(re.findall(rf'\b{re.escape(keyword)}\b', text_lower))
        return count
    
    def verify_claim(self, claim: str, evidence: str = "") -> BaselineVerification:
        """
        Verify a claim using baseline heuristics.
        
        Args:
            claim: Claim to verify
            evidence: Evidence text (optional)
            
        Returns:
            BaselineVerification result
        """
        # Combine claim and evidence
        combined_text = f"{claim} {evidence}".lower()
        
        # Count keyword matches
        true_count = self.count_keyword_matches(combined_text, self.TRUE_KEYWORDS)
        false_count = self.count_keyword_matches(combined_text, self.FALSE_KEYWORDS)
        uncertain_count = self.count_keyword_matches(combined_text, self.UNCERTAIN_KEYWORDS)
        
        # Determine label based on keyword counts
        if false_count > true_count and false_count > uncertain_count:
            label = "false"
            confidence = min(false_count / max(true_count + uncertain_count + 1, 1), 1.0)
            reasoning = f"Found {false_count} false-indicating keywords vs {true_count} true-indicating keywords"
        
        elif true_count > false_count and true_count > uncertain_count:
            label = "true"
            confidence = min(true_count / max(false_count + uncertain_count + 1, 1), 1.0)
            reasoning = f"Found {true_count} true-indicating keywords vs {false_count} false-indicating keywords"
        
        else:
            label = "uncertain"
            confidence = 0.5
            reasoning = f"Keyword counts inconclusive: true={true_count}, false={false_count}, uncertain={uncertain_count}"
        
        return BaselineVerification(
            claim=claim,
            label=label,
            confidence=confidence,
            reasoning=reasoning
        )
    
    def batch_verify_claims(
        self,
        claims: List[str],
        evidence_list: List[str] = None
    ) -> List[BaselineVerification]:
        """
        Verify multiple claims.
        
        Args:
            claims: List of claims
            evidence_list: Optional list of evidence (must match claims length)
            
        Returns:
            List of verification results
        """
        if evidence_list is None:
            evidence_list = [""] * len(claims)
        
        results = []
        for claim, evidence in zip(claims, evidence_list):
            try:
                result = self.verify_claim(claim, evidence)
                results.append(result)
            except Exception as e:
                logger.error(f"Error verifying claim '{claim[:50]}...': {str(e)}")
                results.append(BaselineVerification(
                    claim=claim,
                    label="uncertain",
                    confidence=0.0,
                    reasoning=f"Error: {str(e)}"
                ))
        
        return results
    
    def get_statistics(self, results: List[BaselineVerification]) -> Dict:
        """
        Calculate statistics from verification results.
        
        Args:
            results: List of verification results
            
        Returns:
            Dictionary with statistics
        """
        if not results:
            return {}
        
        total = len(results)
        true_count = sum(1 for r in results if r.label == "true")
        false_count = sum(1 for r in results if r.label == "false")
        uncertain_count = sum(1 for r in results if r.label == "uncertain")
        
        avg_confidence = sum(r.confidence for r in results) / total if total > 0 else 0
        
        return {
            "total_claims": total,
            "true_count": true_count,
            "false_count": false_count,
            "uncertain_count": uncertain_count,
            "true_percentage": (true_count / total * 100) if total > 0 else 0,
            "false_percentage": (false_count / total * 100) if total > 0 else 0,
            "uncertain_percentage": (uncertain_count / total * 100) if total > 0 else 0,
            "average_confidence": avg_confidence
        }

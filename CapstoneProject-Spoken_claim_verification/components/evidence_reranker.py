"""
Evidence Reranker Module

This module reranks evidence based on relevance to claims.
It uses various heuristics and scoring methods to prioritize most relevant evidence.

Author: Capstone Team
Date: 2024
"""

import logging
from typing import List, Dict, Tuple
from dataclasses import dataclass
import re

logger = logging.getLogger(__name__)


@dataclass
class RankedEvidence:
    """Represents ranked evidence with score."""
    title: str
    url: str
    snippet: str
    rank: int
    relevance_score: float
    reasoning: str


class EvidenceReranker:
    """Reranks evidence based on relevance to claims."""
    
    # Domain authority scores (higher = more trustworthy)
    DOMAIN_AUTHORITY = {
        "wikipedia.org": 0.95,
        "gov.uk": 0.95,
        "census.gov": 0.95,
        "bbc.com": 0.90,
        "reuters.com": 0.90,
        "apnews.com": 0.90,
        "nytimes.com": 0.90,
        "theguardian.com": 0.85,
        "cnn.com": 0.80,
        "bbc.co.uk": 0.90,
    }
    
    def __init__(self):
        """Initialize evidence reranker."""
        logger.info("Evidence reranker initialized")
    
    def extract_domain(self, url: str) -> str:
        """
        Extract domain from URL.
        
        Args:
            url: URL string
            
        Returns:
            Domain name
        """
        try:
            # Remove protocol
            url = url.replace("https://", "").replace("http://", "")
            # Remove path
            domain = url.split('/')[0]
            # Remove www
            domain = domain.replace("www.", "")
            return domain
        except:
            return ""
    
    def get_domain_authority_score(self, url: str) -> float:
        """
        Get authority score for domain.
        
        Args:
            url: URL string
            
        Returns:
            Authority score (0-1)
        """
        domain = self.extract_domain(url)
        
        # Check exact match
        if domain in self.DOMAIN_AUTHORITY:
            return self.DOMAIN_AUTHORITY[domain]
        
        # Check partial match
        for known_domain, score in self.DOMAIN_AUTHORITY.items():
            if known_domain in domain:
                return score * 0.9  # Slightly lower for partial matches
        
        # Default score for unknown domains
        return 0.5
    
    def calculate_keyword_overlap(self, claim: str, text: str) -> float:
        """
        Calculate keyword overlap between claim and evidence text.
        
        Args:
            claim: Claim text
            text: Evidence text
            
        Returns:
            Overlap score (0-1)
        """
        # Extract keywords (words > 3 chars, excluding common words)
        stop_words = {"the", "and", "or", "is", "are", "was", "were", "be", "been", "being"}
        
        claim_words = set(
            w.lower() for w in re.findall(r'\b\w+\b', claim)
            if len(w) > 3 and w.lower() not in stop_words
        )
        
        text_words = set(
            w.lower() for w in re.findall(r'\b\w+\b', text)
            if len(w) > 3 and w.lower() not in stop_words
        )
        
        if not claim_words:
            return 0.0
        
        overlap = len(claim_words & text_words)
        return min(overlap / len(claim_words), 1.0)
    
    def calculate_recency_score(self, snippet: str) -> float:
        """
        Calculate recency score based on date mentions in snippet.
        
        Args:
            snippet: Evidence snippet
            
        Returns:
            Recency score (0-1)
        """
        # Look for recent years (2020-2024)
        recent_years = re.findall(r'\b(202[0-4])\b', snippet)
        if recent_years:
            return 0.9
        
        # Look for any year mentions
        years = re.findall(r'\b(19\d{2}|20\d{2})\b', snippet)
        if years:
            return 0.6
        
        return 0.5
    
    def rerank_evidence(
        self,
        claim: str,
        evidence_list: List[Dict],
        weights: Dict[str, float] = None
    ) -> List[RankedEvidence]:
        """
        Rerank evidence based on relevance to claim.
        
        Args:
            claim: Claim text
            evidence_list: List of evidence dictionaries with title, url, snippet
            weights: Weights for different scoring components
            
        Returns:
            List of reranked evidence
        """
        if weights is None:
            weights = {
                "domain_authority": 0.4,
                "keyword_overlap": 0.4,
                "recency": 0.2
            }
        
        ranked = []
        
        for i, evidence in enumerate(evidence_list):
            title = evidence.get("title", "")
            url = evidence.get("url", "")
            snippet = evidence.get("snippet", "")
            
            # Calculate component scores
            domain_score = self.get_domain_authority_score(url)
            keyword_score = self.calculate_keyword_overlap(claim, snippet)
            recency_score = self.calculate_recency_score(snippet)
            
            # Calculate weighted score
            total_score = (
                domain_score * weights["domain_authority"] +
                keyword_score * weights["keyword_overlap"] +
                recency_score * weights["recency"]
            )
            
            # Build reasoning
            reasoning = f"Domain authority: {domain_score:.2f}, Keyword overlap: {keyword_score:.2f}, Recency: {recency_score:.2f}"
            
            ranked.append(RankedEvidence(
                title=title,
                url=url,
                snippet=snippet,
                rank=i + 1,
                relevance_score=total_score,
                reasoning=reasoning
            ))
        
        # Sort by relevance score (descending)
        ranked.sort(key=lambda x: x.relevance_score, reverse=True)
        
        # Update ranks
        for i, item in enumerate(ranked):
            item.rank = i + 1
        
        logger.info(f"Reranked {len(ranked)} evidence items for claim: {claim[:50]}...")
        
        return ranked
    
    def batch_rerank_evidence(
        self,
        claims_evidence: List[Tuple[str, List[Dict]]],
        weights: Dict[str, float] = None
    ) -> Dict[str, List[RankedEvidence]]:
        """
        Rerank evidence for multiple claims.
        
        Args:
            claims_evidence: List of (claim, evidence_list) tuples
            weights: Weights for scoring components
            
        Returns:
            Dictionary mapping claim to reranked evidence
        """
        results = {}
        
        for claim, evidence_list in claims_evidence:
            try:
                reranked = self.rerank_evidence(claim, evidence_list, weights=weights)
                results[claim] = reranked
            except Exception as e:
                logger.error(f"Error reranking evidence for claim '{claim[:50]}...': {str(e)}")
                results[claim] = []
        
        return results
    
    def get_top_evidence(
        self,
        claim: str,
        evidence_list: List[Dict],
        top_k: int = 3,
        min_score: float = 0.3
    ) -> List[RankedEvidence]:
        """
        Get top-k most relevant evidence items.
        
        Args:
            claim: Claim text
            evidence_list: List of evidence
            top_k: Number of top items to return
            min_score: Minimum relevance score threshold
            
        Returns:
            List of top-k evidence items
        """
        reranked = self.rerank_evidence(claim, evidence_list)
        
        # Filter by minimum score and limit to top-k
        filtered = [e for e in reranked if e.relevance_score >= min_score]
        
        return filtered[:top_k]

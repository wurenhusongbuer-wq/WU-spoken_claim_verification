"""
Components Package

Provides core components for the spoken claim verification system:
- Gemini service for claim extraction and verification
- Evidence retriever for web search
- Evidence reranker for relevance scoring
- Baseline model for comparison
"""

from .gemini_service import GeminiService, Claim, VerificationResult
from .evidence_retriever import EvidenceRetriever, SearchResult
from .evidence_reranker import EvidenceReranker, RankedEvidence
from .baseline_model import BaselineModel, BaselineVerification

__all__ = [
    "GeminiService",
    "Claim",
    "VerificationResult",
    "EvidenceRetriever",
    "SearchResult",
    "EvidenceReranker",
    "RankedEvidence",
    "BaselineModel",
    "BaselineVerification",
]

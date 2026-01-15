"""
Evidence Retriever Module

This module retrieves web evidence for claims using Google Search API.
It handles search queries, result processing, and evidence ranking.

Author: Capstone Team
Date: 2024
"""

import os
import logging
import time
from typing import List, Dict, Optional
from dataclasses import dataclass
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Represents a single search result."""
    title: str
    url: str
    snippet: str
    rank: int
    relevance_score: float = 0.0


class EvidenceRetriever:
    """Retrieves web evidence for claims using Google Search API."""
    
    def __init__(self, api_key: Optional[str] = None, search_engine_id: Optional[str] = None):
        """
        Initialize evidence retriever.
        
        Args:
            api_key: Google Custom Search API key
            search_engine_id: Google Custom Search Engine ID
        """
        self.api_key = api_key or os.getenv("GOOGLE_SEARCH_API_KEY")
        self.search_engine_id = search_engine_id or os.getenv("GOOGLE_SEARCH_ENGINE_ID")
        
        if not self.api_key or not self.search_engine_id:
            logger.warning("Google Search credentials not fully configured")
        
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        self.session = requests.Session()
    
    def search(
        self,
        query: str,
        num_results: int = 5,
        timeout: int = 10
    ) -> List[SearchResult]:
        """
        Search for evidence related to a claim.
        
        Args:
            query: Search query
            num_results: Number of results to retrieve
            timeout: Request timeout in seconds
            
        Returns:
            List of SearchResult objects
        """
        try:
            logger.info(f"Searching for: {query}")
            start_time = time.time()
            
            params = {
                "q": query,
                "key": self.api_key,
                "cx": self.search_engine_id,
                "num": min(num_results, 10),  # Google API max is 10
            }
            
            response = self.session.get(
                self.base_url,
                params=params,
                timeout=timeout
            )
            response.raise_for_status()
            
            search_time = time.time() - start_time
            logger.info(f"Search completed in {search_time:.2f}s")
            
            data = response.json()
            results = []
            
            for i, item in enumerate(data.get("items", [])[:num_results]):
                result = SearchResult(
                    title=item.get("title", ""),
                    url=item.get("link", ""),
                    snippet=item.get("snippet", ""),
                    rank=i + 1,
                    relevance_score=1.0 / (i + 1)  # Simple ranking by position
                )
                results.append(result)
            
            logger.info(f"Retrieved {len(results)} search results")
            return results
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Search error: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error during search: {str(e)}")
            return []
    
    def extract_text_from_url(
        self,
        url: str,
        timeout: int = 10,
        max_length: int = 5000
    ) -> str:
        """
        Extract text content from a URL.
        
        Args:
            url: URL to extract from
            timeout: Request timeout in seconds
            max_length: Maximum length of extracted text
            
        Returns:
            Extracted text content
        """
        try:
            logger.info(f"Extracting content from: {url}")
            
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text
            text = soup.get_text(separator=' ', strip=True)
            
            # Clean up whitespace
            text = ' '.join(text.split())
            
            # Truncate if necessary
            if len(text) > max_length:
                text = text[:max_length] + "..."
            
            logger.info(f"Extracted {len(text)} characters")
            return text
            
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {str(e)}")
            return ""
    
    def retrieve_evidence(
        self,
        claim: str,
        num_results: int = 5,
        extract_full_text: bool = False
    ) -> Dict[str, any]:
        """
        Retrieve evidence for a claim.
        
        Args:
            claim: Claim to retrieve evidence for
            num_results: Number of search results to retrieve
            extract_full_text: Whether to extract full text from URLs
            
        Returns:
            Dictionary containing search results and extracted evidence
        """
        try:
            # Search for the claim
            search_results = self.search(claim, num_results=num_results)
            
            if not search_results:
                logger.warning(f"No search results found for claim: {claim}")
                return {
                    "claim": claim,
                    "search_results": [],
                    "evidence_text": "",
                    "sources": []
                }
            
            # Extract evidence text from top results
            evidence_texts = []
            sources = []
            
            for result in search_results[:3]:  # Use top 3 results
                sources.append({
                    "title": result.title,
                    "url": result.url,
                    "snippet": result.snippet,
                    "rank": result.rank
                })
                
                if extract_full_text:
                    full_text = self.extract_text_from_url(result.url)
                    if full_text:
                        evidence_texts.append(f"Source: {result.title}\n{full_text}")
                else:
                    evidence_texts.append(f"Source: {result.title}\n{result.snippet}")
            
            combined_evidence = "\n\n".join(evidence_texts)
            
            return {
                "claim": claim,
                "search_results": [
                    {
                        "title": r.title,
                        "url": r.url,
                        "snippet": r.snippet,
                        "rank": r.rank,
                        "relevance_score": r.relevance_score
                    }
                    for r in search_results
                ],
                "evidence_text": combined_evidence,
                "sources": sources,
                "num_sources": len(sources)
            }
            
        except Exception as e:
            logger.error(f"Error retrieving evidence: {str(e)}")
            return {
                "claim": claim,
                "search_results": [],
                "evidence_text": "",
                "sources": [],
                "error": str(e)
            }
    
    def batch_retrieve_evidence(
        self,
        claims: List[str],
        num_results: int = 5,
        extract_full_text: bool = False
    ) -> List[Dict]:
        """
        Retrieve evidence for multiple claims.
        
        Args:
            claims: List of claims
            num_results: Number of search results per claim
            extract_full_text: Whether to extract full text from URLs
            
        Returns:
            List of evidence retrieval results
        """
        results = []
        for claim in claims:
            try:
                evidence = self.retrieve_evidence(
                    claim,
                    num_results=num_results,
                    extract_full_text=extract_full_text
                )
                results.append(evidence)
            except Exception as e:
                logger.error(f"Error retrieving evidence for claim '{claim[:50]}...': {str(e)}")
                results.append({
                    "claim": claim,
                    "search_results": [],
                    "evidence_text": "",
                    "sources": [],
                    "error": str(e)
                })
        
        return results

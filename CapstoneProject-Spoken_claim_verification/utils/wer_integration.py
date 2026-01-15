"""
Word Error Rate (WER) Integration

This module calculates WER for ASR quality assessment.
WER measures the percentage of words that are incorrectly transcribed.

Author: Capstone Team
Date: 2024
"""

import logging
from typing import List, Tuple
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class WERCalculator:
    """Calculates Word Error Rate for transcription quality."""
    
    @staticmethod
    def calculate_wer(reference: str, hypothesis: str) -> float:
        """
        Calculate Word Error Rate between reference and hypothesis.
        
        Args:
            reference: Reference (ground truth) text
            hypothesis: Hypothesis (ASR output) text
            
        Returns:
            WER as a percentage (0-100)
        """
        ref_words = reference.split()
        hyp_words = hypothesis.split()
        
        # Use dynamic programming to calculate edit distance
        d = WERCalculator._edit_distance(ref_words, hyp_words)
        
        if len(ref_words) == 0:
            return 0.0 if len(hyp_words) == 0 else 100.0
        
        wer = (d / len(ref_words)) * 100
        return min(wer, 100.0)  # Cap at 100%
    
    @staticmethod
    def _edit_distance(ref_words: List[str], hyp_words: List[str]) -> int:
        """
        Calculate edit distance (Levenshtein distance) between word sequences.
        
        Args:
            ref_words: Reference words
            hyp_words: Hypothesis words
            
        Returns:
            Edit distance
        """
        m, n = len(ref_words), len(hyp_words)
        
        # Initialize DP table
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        # Initialize first row and column
        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j
        
        # Fill DP table
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if ref_words[i-1] == hyp_words[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = 1 + min(
                        dp[i-1][j],      # Deletion
                        dp[i][j-1],      # Insertion
                        dp[i-1][j-1]     # Substitution
                    )
        
        return dp[m][n]
    
    @staticmethod
    def calculate_cer(reference: str, hypothesis: str) -> float:
        """
        Calculate Character Error Rate.
        
        Args:
            reference: Reference text
            hypothesis: Hypothesis text
            
        Returns:
            CER as a percentage (0-100)
        """
        ref_chars = list(reference)
        hyp_chars = list(hypothesis)
        
        d = WERCalculator._edit_distance(ref_chars, hyp_chars)
        
        if len(ref_chars) == 0:
            return 0.0 if len(hyp_chars) == 0 else 100.0
        
        cer = (d / len(ref_chars)) * 100
        return min(cer, 100.0)
    
    @staticmethod
    def batch_calculate_wer(
        references: List[str],
        hypotheses: List[str]
    ) -> Tuple[float, List[float]]:
        """
        Calculate WER for multiple pairs.
        
        Args:
            references: List of reference texts
            hypotheses: List of hypothesis texts
            
        Returns:
            Tuple of (average WER, list of individual WERs)
        """
        if len(references) != len(hypotheses):
            raise ValueError("References and hypotheses must have same length")
        
        wers = [
            WERCalculator.calculate_wer(ref, hyp)
            for ref, hyp in zip(references, hypotheses)
        ]
        
        avg_wer = sum(wers) / len(wers) if wers else 0.0
        
        logger.info(f"Batch WER calculation: average={avg_wer:.2f}%, count={len(wers)}")
        
        return avg_wer, wers
    
    @staticmethod
    def get_detailed_comparison(reference: str, hypothesis: str) -> dict:
        """
        Get detailed comparison between reference and hypothesis.
        
        Args:
            reference: Reference text
            hypothesis: Hypothesis text
            
        Returns:
            Dictionary with detailed metrics
        """
        wer = WERCalculator.calculate_wer(reference, hypothesis)
        cer = WERCalculator.calculate_cer(reference, hypothesis)
        
        ref_words = reference.split()
        hyp_words = hypothesis.split()
        
        # Calculate similarity ratio
        matcher = SequenceMatcher(None, reference, hypothesis)
        similarity = matcher.ratio()
        
        return {
            "wer": wer,
            "cer": cer,
            "similarity_ratio": similarity,
            "reference_length": len(ref_words),
            "hypothesis_length": len(hyp_words),
            "reference_text": reference,
            "hypothesis_text": hypothesis
        }

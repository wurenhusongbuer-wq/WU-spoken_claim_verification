"""
Batch Evaluator Module

Evaluates system performance on benchmark datasets.

Author: Capstone Team
Date: 2024
"""

import logging
import json
from typing import List, Dict, Tuple
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class EvaluationMetrics:
    """Evaluation metrics for verification results."""
    precision: float
    recall: float
    f1_score: float
    accuracy: float
    confusion_matrix: Dict[str, Dict[str, int]]
    per_label_metrics: Dict[str, Dict[str, float]]


class BatchEvaluator:
    """Evaluates system performance on batches of claims."""
    
    def __init__(self):
        """Initialize batch evaluator."""
        logger.info("Batch evaluator initialized")
    
    def calculate_confusion_matrix(
        self,
        ground_truth: List[str],
        predictions: List[str]
    ) -> Dict[str, Dict[str, int]]:
        """
        Calculate confusion matrix.
        
        Args:
            ground_truth: Ground truth labels
            predictions: Predicted labels
            
        Returns:
            Confusion matrix as nested dictionary
        """
        labels = set(ground_truth + predictions)
        matrix = {label: {l: 0 for l in labels} for label in labels}
        
        for true_label, pred_label in zip(ground_truth, predictions):
            matrix[true_label][pred_label] += 1
        
        return matrix
    
    def calculate_metrics(
        self,
        ground_truth: List[str],
        predictions: List[str]
    ) -> EvaluationMetrics:
        """
        Calculate evaluation metrics.
        
        Args:
            ground_truth: Ground truth labels
            predictions: Predicted labels
            
        Returns:
            EvaluationMetrics object
        """
        if len(ground_truth) != len(predictions):
            raise ValueError("Ground truth and predictions must have same length")
        
        # Calculate confusion matrix
        confusion_matrix = self.calculate_confusion_matrix(ground_truth, predictions)
        
        # Get unique labels
        labels = list(confusion_matrix.keys())
        
        # Calculate per-label metrics
        per_label_metrics = {}
        total_tp = 0
        total_fp = 0
        total_fn = 0
        
        for label in labels:
            tp = confusion_matrix[label][label]
            fp = sum(confusion_matrix[other_label][label] 
                    for other_label in labels if other_label != label)
            fn = sum(confusion_matrix[label][other_label] 
                    for other_label in labels if other_label != label)
            
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
            
            per_label_metrics[label] = {
                "precision": precision,
                "recall": recall,
                "f1_score": f1,
                "support": tp + fn
            }
            
            total_tp += tp
            total_fp += fp
            total_fn += fn
        
        # Calculate macro-averaged metrics
        macro_precision = sum(m["precision"] for m in per_label_metrics.values()) / len(labels)
        macro_recall = sum(m["recall"] for m in per_label_metrics.values()) / len(labels)
        macro_f1 = 2 * (macro_precision * macro_recall) / (macro_precision + macro_recall) if (macro_precision + macro_recall) > 0 else 0.0
        
        # Calculate accuracy
        correct = sum(confusion_matrix[label][label] for label in labels)
        accuracy = correct / len(ground_truth) if len(ground_truth) > 0 else 0.0
        
        return EvaluationMetrics(
            precision=macro_precision,
            recall=macro_recall,
            f1_score=macro_f1,
            accuracy=accuracy,
            confusion_matrix=confusion_matrix,
            per_label_metrics=per_label_metrics
        )
    
    def evaluate_batch(
        self,
        results: List[Dict],
        ground_truth_field: str = "ground_truth",
        prediction_field: str = "label"
    ) -> EvaluationMetrics:
        """
        Evaluate a batch of results.
        
        Args:
            results: List of result dictionaries
            ground_truth_field: Field name for ground truth
            prediction_field: Field name for predictions
            
        Returns:
            EvaluationMetrics object
        """
        ground_truth = [r[ground_truth_field] for r in results]
        predictions = [r[prediction_field] for r in results]
        
        return self.calculate_metrics(ground_truth, predictions)
    
    def evaluate_with_confidence(
        self,
        results: List[Dict],
        confidence_threshold: float = 0.5,
        ground_truth_field: str = "ground_truth",
        prediction_field: str = "label",
        confidence_field: str = "confidence"
    ) -> Dict:
        """
        Evaluate results with confidence threshold filtering.
        
        Args:
            results: List of result dictionaries
            confidence_threshold: Minimum confidence to include
            ground_truth_field: Field name for ground truth
            prediction_field: Field name for predictions
            confidence_field: Field name for confidence scores
            
        Returns:
            Dictionary with metrics at different confidence levels
        """
        # Filter by confidence
        filtered_results = [
            r for r in results 
            if r.get(confidence_field, 0) >= confidence_threshold
        ]
        
        metrics = self.evaluate_batch(filtered_results, ground_truth_field, prediction_field)
        
        return {
            "threshold": confidence_threshold,
            "total_results": len(results),
            "filtered_results": len(filtered_results),
            "coverage": len(filtered_results) / len(results) if results else 0.0,
            "metrics": {
                "precision": metrics.precision,
                "recall": metrics.recall,
                "f1_score": metrics.f1_score,
                "accuracy": metrics.accuracy
            }
        }
    
    def generate_report(
        self,
        metrics: EvaluationMetrics,
        output_file: str = "evaluation_report.json"
    ) -> None:
        """
        Generate evaluation report.
        
        Args:
            metrics: EvaluationMetrics object
            output_file: Output file path
        """
        report = {
            "overall_metrics": {
                "precision": metrics.precision,
                "recall": metrics.recall,
                "f1_score": metrics.f1_score,
                "accuracy": metrics.accuracy
            },
            "confusion_matrix": metrics.confusion_matrix,
            "per_label_metrics": metrics.per_label_metrics
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Evaluation report saved to {output_file}")
    
    def compare_results(
        self,
        baseline_results: List[Dict],
        system_results: List[Dict],
        ground_truth_field: str = "ground_truth",
        prediction_field: str = "label"
    ) -> Dict:
        """
        Compare baseline and system results.
        
        Args:
            baseline_results: Baseline model results
            system_results: System model results
            ground_truth_field: Field name for ground truth
            prediction_field: Field name for predictions
            
        Returns:
            Comparison dictionary
        """
        baseline_metrics = self.evaluate_batch(baseline_results, ground_truth_field, prediction_field)
        system_metrics = self.evaluate_batch(system_results, ground_truth_field, prediction_field)
        
        comparison = {
            "baseline": {
                "precision": baseline_metrics.precision,
                "recall": baseline_metrics.recall,
                "f1_score": baseline_metrics.f1_score,
                "accuracy": baseline_metrics.accuracy
            },
            "system": {
                "precision": system_metrics.precision,
                "recall": system_metrics.recall,
                "f1_score": system_metrics.f1_score,
                "accuracy": system_metrics.accuracy
            },
            "improvement": {
                "precision": system_metrics.precision - baseline_metrics.precision,
                "recall": system_metrics.recall - baseline_metrics.recall,
                "f1_score": system_metrics.f1_score - baseline_metrics.f1_score,
                "accuracy": system_metrics.accuracy - baseline_metrics.accuracy
            }
        }
        
        return comparison

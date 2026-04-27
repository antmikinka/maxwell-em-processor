# Maxwell EM Processor - Data Science Implementation Plan

## Implementation Overview

This document provides detailed technical implementation plans for the data science enhancements identified in the comprehensive analysis. Each section includes specific code examples, architecture diagrams, and integration strategies.

## 1. Quality Assessment System Implementation

### 1.1 Automated Quality Scoring Architecture

```python
# src/quality_assessment.py
"""
Automated Quality Assessment System for Maxwell EM Processor
Implements comprehensive quality scoring for OCR results and content extraction
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import torch
from transformers import BertTokenizer, BertModel
import logging

@dataclass
class QualityMetrics:
    """Quality assessment metrics structure"""
    ocr_quality: float  # 0.0 - 1.0
    content_quality: float  # 0.0 - 1.0
    processing_quality: float  # 0.0 - 1.0
    overall_quality: float  # Weighted average
    quality_class: str  # "excellent", "good", "fair", "poor"
    issues: List[str]  # List of quality issues detected

class OCRQualityAssessor:
    """Assesses OCR quality using multiple metrics"""

    def __init__(self):
        self.model = self._build_quality_model()
        self.scaler = StandardScaler()

    def _build_quality_model(self):
        """Build machine learning model for OCR quality prediction"""
        # Features: confidence_scores, text_density, equation_count,
        #           processing_time, error_rate, image_quality
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        return model

    def extract_ocr_features(self, page_data: Dict) -> np.ndarray:
        """Extract features for OCR quality assessment"""
        features = []

        # Confidence-based features
        confidence_scores = [line.get('confidence', 0.0)
                           for line in page_data.get('line_data', [])
                           if line.get('confidence') is not None]

        features.extend([
            np.mean(confidence_scores) if confidence_scores else 0.0,
            np.std(confidence_scores) if confidence_scores else 0.0,
            np.min(confidence_scores) if confidence_scores else 0.0,
            len([c for c in confidence_scores if c < 0.7]) / len(confidence_scores) if confidence_scores else 1.0
        ])

        # Content-based features
        line_data = page_data.get('line_data', [])
        text_lines = [line for line in line_data if line.get('type') == 'text']
        equation_lines = [line for line in line_data if line.get('type') == 'equation']

        features.extend([
            len(text_lines),
            len(equation_lines),
            len(line_data),
            len(equation_lines) / len(line_data) if line_data else 0.0,
            len(text_lines) / len(line_data) if line_data else 0.0
        ])

        # Processing-based features
        processing_time = page_data.get('processing_time_seconds', 0.0)
        features.extend([
            processing_time,
            1.0 if processing_time > 30 else 0.0  # Flag for slow processing
        ])

        # Layout-based features
        page_width = page_data.get('page_width', 0)
        page_height = page_data.get('page_height', 0)
        features.extend([
            page_width,
            page_height,
            page_width * page_height if page_width and page_height else 0.0
        ])

        return np.array(features).reshape(1, -1)

    def assess_page_quality(self, page_data: Dict) -> float:
        """Assess quality of a single page"""
        features = self.extract_ocr_features(page_data)

        # Handle case where model hasn't been trained yet
        if hasattr(self.model, 'estimators_'):
            quality_score = self.model.predict(features)[0]
        else:
            # Default quality assessment based on heuristics
            quality_score = self._heuristic_quality_assessment(page_data)

        return max(0.0, min(1.0, quality_score))

    def _heuristic_quality_assessment(self, page_data: Dict) -> float:
        """Fallback heuristic-based quality assessment"""
        score = 1.0

        # Penalize low confidence
        confidence_scores = [line.get('confidence', 0.0)
                           for line in page_data.get('line_data', [])
                           if line.get('confidence') is not None]

        if confidence_scores:
            avg_confidence = np.mean(confidence_scores)
            if avg_confidence < 0.5:
                score -= 0.4
            elif avg_confidence < 0.7:
                score -= 0.2
            elif avg_confidence < 0.8:
                score -= 0.1

        # Penalize very slow processing
        processing_time = page_data.get('processing_time_seconds', 0.0)
        if processing_time > 60:
            score -= 0.2
        elif processing_time > 30:
            score -= 0.1

        # Penalize missing content
        line_count = len(page_data.get('line_data', []))
        if line_count == 0:
            score -= 0.5
        elif line_count < 5:
            score -= 0.2

        return max(0.0, min(1.0, score))

class ContentQualityAssessor:
    """Assesses content quality using semantic analysis"""

    def __init__(self):
        self.tokenizer = BertTokenizer.from_pretrained('allenai/scibert_scivocab_uncased')
        self.model = BertModel.from_pretrained('allenai/scibert_scivocab_uncased')
        self.content_classifier = self._build_content_classifier()

    def _build_content_classifier(self):
        """Build content quality classifier"""
        # This would be trained on labeled content quality data
        # For now, return a placeholder
        return None

    def extract_content_features(self, page_data: Dict) -> Dict:
        """Extract semantic content features"""
        text_content = []
        equation_content = []

        for line in page_data.get('line_data', []):
            if line.get('type') == 'text' and line.get('text'):
                text_content.append(line['text'])
            elif line.get('type') == 'equation' and line.get('text'):
                equation_content.append(line['text'])

        combined_text = ' '.join(text_content)

        features = {
            'text_length': len(combined_text),
            'equation_count': len(equation_content),
            'text_complexity': self._calculate_text_complexity(combined_text),
            'equation_complexity': self._calculate_equation_complexity(equation_content),
            'semantic_coherence': self._calculate_semantic_coherence(text_content)
        }

        return features

    def _calculate_text_complexity(self, text: str) -> float:
        """Calculate text complexity using readability metrics"""
        if not text:
            return 0.0

        # Simple complexity based on average word length and sentence length
        words = text.split()
        if not words:
            return 0.0

        avg_word_length = sum(len(word) for word in words) / len(words)
        sentence_count = text.count('.') + text.count('!') + text.count('?')

        if sentence_count == 0:
            return min(avg_word_length / 10, 1.0)

        avg_sentence_length = len(words) / sentence_count
        complexity = (avg_word_length / 10) * (avg_sentence_length / 20)

        return min(complexity, 1.0)

    def _calculate_equation_complexity(self, equations: List[str]) -> float:
        """Calculate mathematical complexity of equations"""
        if not equations:
            return 0.0

        complexity_scores = []
        for eq in equations:
            # Count mathematical symbols and operators
            symbols = sum(1 for char in eq if char in ['∑', '∫', '∂', '∇', '∏', '∞'])
            operators = sum(1 for char in eq if char in ['+', '-', '=', '×', '÷'])
            complexity = min((symbols * 2 + operators) / 20, 1.0)
            complexity_scores.append(complexity)

        return np.mean(complexity_scores) if complexity_scores else 0.0

    def _calculate_semantic_coherence(self, text_lines: List[str]) -> float:
        """Calculate semantic coherence between text lines"""
        if len(text_lines) < 2:
            return 1.0

        # Simple coherence based on shared vocabulary
        coherence_scores = []
        for i in range(len(text_lines) - 1):
            words1 = set(text_lines[i].lower().split())
            words2 = set(text_lines[i + 1].lower().split())
            if words1 or words2:
                overlap = len(words1 & words2) / len(words1 | words2)
                coherence_scores.append(overlap)

        return np.mean(coherence_scores) if coherence_scores else 0.5

    def assess_content_quality(self, page_data: Dict) -> float:
        """Assess content quality"""
        features = self.extract_content_features(page_data)

        # Heuristic-based content quality scoring
        quality_score = 1.0

        # Penalize very short content
        if features['text_length'] < 50:
            quality_score -= 0.3
        elif features['text_length'] < 100:
            quality_score -= 0.1

        # Reward appropriate equation density
        equation_ratio = features['equation_count'] / max(1, len(page_data.get('line_data', [])))
        if equation_ratio > 0.3:  # Too many equations might indicate poor text
            quality_score -= 0.1
        elif equation_ratio > 0.05:  # Good balance
            quality_score += 0.1

        # Penalize poor coherence
        if features['semantic_coherence'] < 0.1:
            quality_score -= 0.2
        elif features['semantic_coherence'] < 0.2:
            quality_score -= 0.1

        # Penalize low complexity (might be placeholder content)
        total_complexity = features['text_complexity'] + features['equation_complexity']
        if total_complexity < 0.1:
            quality_score -= 0.1

        return max(0.0, min(1.0, quality_score))

class ProcessingQualityAssessor:
    """Assesses processing quality and efficiency"""

    def __init__(self):
        self.target_processing_time = 10.0  # seconds per page
        self.target_confidence_threshold = 0.8

    def assess_processing_quality(self, page_data: Dict) -> float:
        """Assess processing quality"""
        quality_score = 1.0

        # Check processing time
        processing_time = page_data.get('processing_time_seconds', 0.0)
        if processing_time > self.target_processing_time * 2:
            quality_score -= 0.3
        elif processing_time > self.target_processing_time:
            quality_score -= 0.1

        # Check confidence consistency
        confidence_scores = [line.get('confidence', 0.0)
                           for line in page_data.get('line_data', [])
                           if line.get('confidence') is not None]

        if confidence_scores:
            avg_confidence = np.mean(confidence_scores)
            confidence_std = np.std(confidence_scores)

            if avg_confidence < self.target_confidence_threshold:
                quality_score -= 0.2
            if confidence_std > 0.3:  # High variance in confidence
                quality_score -= 0.1

        # Check metadata completeness
        required_fields = ['page_number', 'pdf_id', 'line_data']
        missing_fields = sum(1 for field in required_fields
                           if field not in page_data or not page_data[field])

        if missing_fields > 0:
            quality_score -= 0.2 * missing_fields

        return max(0.0, min(1.0, quality_score))

class QualityAssessmentPipeline:
    """Main pipeline for quality assessment"""

    def __init__(self):
        self.ocr_assessor = OCRQualityAssessor()
        self.content_assessor = ContentQualityAssessor()
        self.processing_assessor = ProcessingQualityAssessor()
        self.logger = logging.getLogger(__name__)

    def assess_page(self, page_data: Dict) -> QualityMetrics:
        """Assess quality of a single page"""
        try:
            ocr_quality = self.ocr_assessor.assess_page_quality(page_data)
            content_quality = self.content_assessor.assess_content_quality(page_data)
            processing_quality = self.processing_assessor.assess_processing_quality(page_data)

            # Calculate weighted overall quality
            overall_quality = (
                ocr_quality * 0.4 +
                content_quality * 0.4 +
                processing_quality * 0.2
            )

            # Determine quality class
            if overall_quality >= 0.8:
                quality_class = "excellent"
            elif overall_quality >= 0.6:
                quality_class = "good"
            elif overall_quality >= 0.4:
                quality_class = "fair"
            else:
                quality_class = "poor"

            # Identify issues
            issues = self._identify_quality_issues(page_data, ocr_quality, content_quality, processing_quality)

            return QualityMetrics(
                ocr_quality=ocr_quality,
                content_quality=content_quality,
                processing_quality=processing_quality,
                overall_quality=overall_quality,
                quality_class=quality_class,
                issues=issues
            )

        except Exception as e:
            self.logger.error(f"Error assessing quality for page {page_data.get('page_number', 'unknown')}: {str(e)}")
            return QualityMetrics(
                ocr_quality=0.0,
                content_quality=0.0,
                processing_quality=0.0,
                overall_quality=0.0,
                quality_class="error",
                issues=[f"Quality assessment failed: {str(e)}"]
            )

    def _identify_quality_issues(self, page_data: Dict, ocr_quality: float,
                               content_quality: float, processing_quality: float) -> List[str]:
        """Identify specific quality issues"""
        issues = []

        if ocr_quality < 0.5:
            issues.append("Low OCR confidence detected")
        if content_quality < 0.5:
            issues.append("Poor content structure or completeness")
        if processing_quality < 0.5:
            issues.append("Processing inefficiency or errors")

        # Check for specific patterns
        line_count = len(page_data.get('line_data', []))
        if line_count == 0:
            issues.append("No content extracted from page")
        elif line_count < 3:
            issues.append("Very little content extracted")

        confidence_scores = [line.get('confidence', 0.0)
                           for line in page_data.get('line_data', [])
                           if line.get('confidence') is not None]
        if confidence_scores and np.mean(confidence_scores) < 0.6:
            issues.append("Low average confidence across page")

        processing_time = page_data.get('processing_time_seconds', 0.0)
        if processing_time > 30:
            issues.append("Excessive processing time")

        return issues

    def assess_volume(self, volume_data: Dict) -> Dict:
        """Assess quality of entire volume"""
        page_qualities = []
        volume_issues = []

        for page_num, page_data in volume_data.get('pages', {}).items():
            page_quality = self.assess_page(page_data)
            page_qualities.append(page_quality)

            if page_quality.issues:
                volume_issues.extend([
                    f"Page {page_num}: {issue}" for issue in page_quality.issues
                ])

        if not page_qualities:
            return {"error": "No pages found for quality assessment"}

        # Calculate volume-level metrics
        ocr_qualities = [pq.ocr_quality for pq in page_qualities]
        content_qualities = [pq.content_quality for pq in page_qualities]
        processing_qualities = [pq.processing_quality for pq in page_qualities]
        overall_qualities = [pq.overall_quality for pq in page_qualities]

        quality_summary = {
            "volume_quality_summary": {
                "avg_ocr_quality": np.mean(ocr_qualities),
                "avg_content_quality": np.mean(content_qualities),
                "avg_processing_quality": np.mean(processing_qualities),
                "avg_overall_quality": np.mean(overall_qualities),
                "quality_std_dev": np.std(overall_qualities),
                "min_quality": min(overall_qualities),
                "max_quality": max(overall_qualities),
                "excellent_pages": sum(1 for pq in page_qualities if pq.quality_class == "excellent"),
                "good_pages": sum(1 for pq in page_qualities if pq.quality_class == "good"),
                "fair_pages": sum(1 for pq in page_qualities if pq.quality_class == "fair"),
                "poor_pages": sum(1 for pq in page_qualities if pq.quality_class == "poor"),
                "total_pages": len(page_qualities)
            },
            "quality_issues": volume_issues,
            "recommendations": self._generate_quality_recommendations(overall_qualities, volume_issues)
        }

        return quality_summary

    def _generate_quality_recommendations(self, quality_scores: List[float],
                                        issues: List[str]) -> List[str]:
        """Generate recommendations based on quality assessment"""
        recommendations = []

        avg_quality = np.mean(quality_scores) if quality_scores else 0.0

        if avg_quality < 0.5:
            recommendations.append("URGENT: Overall quality is poor. Consider reprocessing with higher quality settings.")
        elif avg_quality < 0.7:
            recommendations.append("Quality is below target. Review processing parameters and consider improvements.")

        low_quality_pages = sum(1 for score in quality_scores if score < 0.4)
        if low_quality_pages > len(quality_scores) * 0.1:  # More than 10% poor quality
            recommendations.append(f"Significant number of poor quality pages ({low_quality_pages}). Review OCR settings.")

        if any("Low OCR confidence" in issue for issue in issues):
            recommendations.append("Consider improving image quality or adjusting OCR parameters for better confidence.")

        if any("Processing inefficiency" in issue for issue in issues):
            recommendations.append("Optimize processing pipeline to reduce errors and improve efficiency.")

        if not recommendations:
            recommendations.append("Quality assessment looks good. Continue monitoring.")

        return recommendations
```

### 1.2 Quality Monitoring Dashboard

```python
# src/quality_dashboard.py
"""
Real-time Quality Monitoring Dashboard for Maxwell EM Processor
Provides live updates on processing quality and system performance
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from pathlib import Path
import time

class QualityMonitoringDashboard:
    """Interactive dashboard for quality monitoring"""

    def __init__(self, data_directory: str):
        self.data_directory = Path(data_directory)
        self.refresh_interval = 30  # seconds

    def load_quality_data(self) -> Dict:
        """Load latest quality assessment data"""
        quality_files = list(self.data_directory.glob("**/quality_assessment*.json"))

        if not quality_files:
            return {"error": "No quality data found"}

        # Load most recent quality data
        latest_file = max(quality_files, key=lambda f: f.stat().st_mtime)
        with open(latest_file, 'r') as f:
            return json.load(f)

    def create_quality_overview(self, quality_data: Dict):
        """Create main quality overview dashboard"""
        st.title("🔍 Maxwell EM Processor - Quality Monitoring Dashboard")
        st.markdown(f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

        if "error" in quality_data:
            st.error(quality_data["error"])
            return

        # Main quality metrics
        col1, col2, col3, col4 = st.columns(4)

        summary = quality_data.get("volume_quality_summary", {})

        with col1:
            st.metric(
                label="🎯 Overall Quality Score",
                value=f"{summary.get('avg_overall_quality', 0):.2f}",
                delta=None
            )

        with col2:
            st.metric(
                label="📄 Average OCR Quality",
                value=f"{summary.get('avg_ocr_quality', 0):.2f}",
                delta=None
            )

        with col3:
            st.metric(
                label="📝 Average Content Quality",
                value=f"{summary.get('avg_content_quality', 0):.2f}",
                delta=None
            )

        with col4:
            st.metric(
                label="⚡ Processing Quality",
                value=f"{summary.get('avg_processing_quality', 0):.2f}",
                delta=None
            )

        # Quality distribution
        self.create_quality_distribution_chart(summary)
        self.create_quality_trend_analysis(quality_data)
        self.display_quality_issues(quality_data)
        self.display_page_quality_heatmap(quality_data)

    def create_quality_distribution_chart(self, summary: Dict):
        """Create quality distribution visualization"""
        st.subheader("📊 Quality Distribution")

        quality_classes = ["excellent", "good", "fair", "poor"]
        counts = [summary.get(f"{cls}_pages", 0) for cls in quality_classes]
        total_pages = summary.get("total_pages", 1)

        # Calculate percentages
        percentages = [(count / total_pages) * 100 for count in counts]

        col1, col2 = st.columns(2)

        with col1:
            fig = go.Figure(data=[go.Pie(
                labels=quality_classes,
                values=counts,
                hole=0.3,
                colors=['#2E8B57', '#32CD32', '#FFD700', '#FF6347']
            )])
            fig.update_layout(title="Page Quality Distribution")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = go.Figure(data=[go.Bar(
                x=quality_classes,
                y=percentages,
                marker_color=['#2E8B57', '#32CD32', '#FFD700', '#FF6347']
            )])
            fig.update_layout(
                title="Quality Distribution (%)",
                yaxis_title="Percentage (%)"
            )
            st.plotly_chart(fig, use_container_width=True)

    def create_quality_trend_analysis(self, quality_data: Dict):
        """Analyze quality trends over pages"""
        st.subheader("📈 Quality Trend Analysis")

        # Create sample trend data (in real implementation, this would come from historical data)
        page_qualities = []
        page_numbers = []

        # Extract page quality data
        for page_num, page_data in quality_data.get("page_qualities", {}).items():
            page_qualities.append(page_data.get("overall_quality", 0))
            page_numbers.append(int(page_num))

        if page_qualities:
            df = pd.DataFrame({
                'Page': page_numbers,
                'Quality': page_qualities
            })
            df = df.sort_values('Page')

            fig = go.Figure()

            # Add quality line
            fig.add_trace(go.Scatter(
                x=df['Page'],
                y=df['Quality'],
                mode='lines+markers',
                name='Quality Score',
                line=dict(color='#1f77b4', width=2),
                marker=dict(size=4)
            ))

            # Add quality thresholds
            fig.add_hline(y=0.8, line_dash="dash", line_color="green",
                         annotation_text="Excellent Threshold")
            fig.add_hline(y=0.6, line_dash="dash", line_color="orange",
                         annotation_text="Good Threshold")
            fig.add_hline(y=0.4, line_dash="dash", line_color="red",
                         annotation_text="Poor Threshold")

            fig.update_layout(
                title="Quality Trend Across Pages",
                xaxis_title="Page Number",
                yaxis_title="Quality Score",
                hovermode='x unified'
            )

            st.plotly_chart(fig, use_container_width=True)

    def display_quality_issues(self, quality_data: Dict):
        """Display quality issues and recommendations"""
        st.subheader("⚠️ Quality Issues & Recommendations")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Issues Found:**")
            issues = quality_data.get("quality_issues", [])

            if issues:
                for issue in issues[:10]:  # Show first 10 issues
                    st.warning(issue)
                if len(issues) > 10:
                    st.info(f"... and {len(issues) - 10} more issues")
            else:
                st.success("✅ No quality issues detected!")

        with col2:
            st.markdown("**Recommendations:**")
            recommendations = quality_data.get("recommendations", [])

            for rec in recommendations:
                if "URGENT" in rec:
                    st.error(rec)
                elif "Consider" in rec or "Review" in rec:
                    st.warning(rec)
                else:
                    st.info(rec)

    def display_page_quality_heatmap(self, quality_data: Dict):
        """Display quality heatmap for pages"""
        st.subheader("🌡️ Page Quality Heatmap")

        # Create a grid representation of page qualities
        page_qualities = {}
        for page_num, page_data in quality_data.get("page_qualities", {}).items():
            page_qualities[int(page_num)] = page_data.get("overall_quality", 0)

        if not page_qualities:
            st.info("No page quality data available for heatmap")
            return

        # Create heatmap data
        max_page = max(page_qualities.keys())
        grid_size = 20  # 20x20 grid

        heatmap_data = np.zeros((grid_size, grid_size))
        quality_colors = np.full((grid_size, grid_size), -1.0)

        for page_num, quality in page_qualities.items():
            row = (page_num - 1) // grid_size
            col = (page_num - 1) % grid_size
            if row < grid_size and col < grid_size:
                heatmap_data[row, col] = quality
                quality_colors[row, col] = quality

        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=quality_colors,
            colorscale='RdYlGn',
            zmin=0,
            zmax=1,
            text=[[f"Page {i*grid_size+j+1}<br>Quality: {quality_colors[i,j]:.2f}"
                  if quality_colors[i,j] >= 0 else f"Page {i*grid_size+j+1}<br>No data"
                  for j in range(grid_size)] for i in range(grid_size)],
            hoverinfo='text'
        ))

        fig.update_layout(
            title="Page Quality Heatmap",
            xaxis_title="Column",
            yaxis_title="Row",
            width=600,
            height=600
        )

        st.plotly_chart(fig)

    def run_dashboard(self):
        """Run the quality monitoring dashboard"""
        st.set_page_config(
            page_title="Maxwell EM Quality Dashboard",
            page_icon="🔍",
            layout="wide",
            initial_sidebar_state="expanded"
        )

        # Auto-refresh
        if st.button("🔄 Refresh Data"):
            st.rerun()

        # Load and display quality data
        quality_data = self.load_quality_data()
        self.create_quality_overview(quality_data)

        # Auto-refresh every 30 seconds
        time.sleep(self.refresh_interval)
        st.rerun()

# Integration with main pipeline
def integrate_quality_assessment():
    """Integrate quality assessment into main processing pipeline"""
    from src.quality_assessment import QualityAssessmentPipeline
    from src.data_models import PDFOCRResult
    import json
    from pathlib import Path

    # Initialize quality assessment
    quality_pipeline = QualityAssessmentPipeline()

    # Load OCR results
    ocr_result_file = Path("output/database/volume_2_ocr_result.json")
    with open(ocr_result_file, 'r') as f:
        ocr_data = json.load(f)

    # Assess quality
    volume_quality = quality_pipeline.assess_volume(ocr_data)

    # Save quality results
    quality_output_dir = Path("output/quality_assessment")
    quality_output_dir.mkdir(parents=True, exist_ok=True)

    quality_file = quality_output_dir / f"quality_assessment_volume_2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(quality_file, 'w') as f:
        json.dump(volume_quality, f, indent=2)

    return volume_quality

if __name__ == "__main__":
    # Example usage
    dashboard = QualityMonitoringDashboard("output/quality_assessment")
    dashboard.run_dashboard()
```

## 2. ML-Enhanced Content Classification Implementation

### 2.1 Advanced Content Classification System

```python
# src/ml_content_classifier.py
"""
Machine Learning Enhanced Content Classification for Maxwell EM Processor
Implements advanced classification using BERT embeddings and ensemble methods
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
import torch
from transformers import BertTokenizer, BertModel, pipeline
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import logging
from pathlib import Path
import re

@dataclass
class ClassificationResult:
    """Classification result structure"""
    predicted_class: str
    confidence: float
    alternative_classes: List[Tuple[str, float]]
    reasoning: str
    metadata: Dict

class PhysicsBERTClassifier:
    """BERT-based classifier for physics content classification"""

    def __init__(self, model_name: str = 'allenai/scibert_scivocab_uncased'):
        self.model_name = model_name
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        self.model = BertModel.from_pretrained(model_name)
        self.classifier = None
        self.label_encoder = LabelEncoder()
        self.scaler = StandardScaler()
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)

        # Physics domain labels
        self.physics_labels = [
            'electrostatics', 'magnetostatics', 'electrodynamics',
            'maxwell_equations', 'electromagnetic_waves', 'optics',
            'classical_mechanics', 'quantum_mechanics', 'thermodynamics',
            'statistical_mechanics', 'relativity', 'nuclear_physics',
            'particle_physics', 'condensed_matter', 'plasma_physics',
            'experimental_techniques', 'mathematical_methods', 'computational_physics'
        ]

        self.logger = logging.getLogger(__name__)

    def extract_physics_features(self, text: str) -> np.ndarray:
        """Extract physics-specific features from text"""
        features = []

        # Physics keyword frequency
        physics_keywords = {
            'electromagnetism': ['electric field', 'magnetic field', 'Maxwell', 'electromagnetic'],
            'quantum': ['wave function', 'quantum', 'particle', 'uncertainty'],
            'mechanics': ['force', 'motion', 'energy', 'momentum'],
            'thermodynamics': ['entropy', 'temperature', 'heat', 'equilibrium']
        }

        text_lower = text.lower()
        for category, keywords in physics_keywords.items():
            keyword_count = sum(text_lower.count(keyword) for keyword in keywords)
            features.append(keyword_count / max(len(text.split()), 1))  # Normalize by text length

        # Mathematical symbol frequency
        math_symbols = ['∫', '∑', '∂', '∇', '∏', '∞', '∀', '∃', '∈']
        math_density = sum(text.count(symbol) for symbol in math_symbols) / max(len(text), 1)
        features.append(math_density)

        # Equation patterns
        equation_patterns = [
            r'\\begin\{equation\}',
            r'\$.*\$',
            r'\\[.*\\]',
            r'\\frac\{.*\}\{.*\}'
        ]
        equation_count = sum(len(re.findall(pattern, text, re.DOTALL)) for pattern in equation_patterns)
        features.append(equation_count / max(len(text.split()), 1))

        # Section type indicators
        section_indicators = [
            'chapter', 'section', 'article', 'theorem', 'proof',
            'definition', 'example', 'figure', 'table'
        ]
        for indicator in section_indicators:
            features.append(text_lower.count(indicator) / max(len(text.split()), 1))

        return np.array(features)

    def get_bert_embeddings(self, text: str, max_length: int = 512) -> np.ndarray:
        """Get BERT embeddings for text"""
        if not text.strip():
            return np.zeros(768)  # BERT base model embedding size

        # Tokenize and truncate/pad
        inputs = self.tokenizer(
            text,
            return_tensors='pt',
            max_length=max_length,
            truncation=True,
            padding='max_length'
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # Get embeddings
        with torch.no_grad():
            outputs = self.model(**inputs)
            # Use [CLS] token embedding
            embeddings = outputs.last_hidden_state[:, 0, :].cpu().numpy()

        return embeddings[0]

    def extract_comprehensive_features(self, page_data: Dict) -> np.ndarray:
        """Extract comprehensive features for classification"""
        # Text content
        text_content = []
        equation_content = []

        for line in page_data.get('line_data', []):
            if line.get('type') == 'text' and line.get('text'):
                text_content.append(line['text'])
            elif line.get('type') == 'equation' and line.get('text'):
                equation_content.append(line['text'])

        combined_text = ' '.join(text_content)
        combined_equations = ' '.join(equation_content)

        # BERT embeddings for text
        text_embeddings = self.get_bert_embeddings(combined_text)
        equation_embeddings = self.get_bert_embeddings(combined_equations)

        # Physics-specific features
        physics_features = self.extract_physics_features(combined_text)

        # Layout features
        layout_features = self.extract_layout_features(page_data)

        # Confidence features
        confidence_features = self.extract_confidence_features(page_data)

        # Combine all features
        combined_features = np.concatenate([
            text_embeddings,
            equation_embeddings,
            physics_features,
            layout_features,
            confidence_features
        ])

        return combined_features

    def extract_layout_features(self, page_data: Dict) -> np.ndarray:
        """Extract layout and structural features"""
        features = []

        line_data = page_data.get('line_data', [])
        if not line_data:
            return np.zeros(5)

        # Line type distribution
        line_types = [line.get('type', 'unknown') for line in line_data]
        type_counts = {}
        for line_type in line_types:
            type_counts[line_type] = type_counts.get(line_type, 0) + 1

        total_lines = len(line_data)
        for line_type in ['text', 'equation', 'figure', 'diagram', 'section_header']:
            features.append(type_counts.get(line_type, 0) / total_lines)

        # Page structure features
        page_width = page_data.get('page_width', 0)
        page_height = page_data.get('page_height', 0)
        features.extend([
            page_width / 1000 if page_width else 0,  # Normalize
            page_height / 1000 if page_height else 0,
            len(line_data) / 100,  # Normalize line count
        ])

        return np.array(features)

    def extract_confidence_features(self, page_data: Dict) -> np.ndarray:
        """Extract confidence-based features"""
        confidence_scores = [line.get('confidence', 0.0)
                           for line in page_data.get('line_data', [])
                           if line.get('confidence') is not None]

        if not confidence_scores:
            return np.zeros(4)

        features = [
            np.mean(confidence_scores),
            np.std(confidence_scores),
            np.min(confidence_scores),
            len([c for c in confidence_scores if c < 0.7]) / len(confidence_scores)
        ]

        return np.array(features)

    def train_classifier(self, training_data: List[Dict], labels: List[str]):
        """Train the classification model"""
        self.logger.info(f"Training classifier with {len(training_data)} samples")

        # Extract features
        X = []
        for page_data in training_data:
            features = self.extract_comprehensive_features(page_data)
            X.append(features)

        X = np.array(X)
        y = self.label_encoder.fit_transform(labels)

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Create ensemble classifier
        rf_classifier = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight='balanced'
        )

        svm_classifier = SVC(
            kernel='rbf',
            class_weight='balanced',
            probability=True,
            random_state=42
        )

        nn_classifier = MLPClassifier(
            hidden_layer_sizes=(128, 64),
            activation='relu',
            solver='adam',
            max_iter=1000,
            random_state=42
        )

        # Ensemble voting
        self.classifier = VotingClassifier(
            estimators=[
                ('rf', rf_classifier),
                ('svm', svm_classifier),
                ('nn', nn_classifier)
            ],
            voting='soft'
        )

        # Train classifier
        self.classifier.fit(X_scaled, y)

        # Cross-validation
        cv_scores = cross_val_score(self.classifier, X_scaled, y, cv=5)
        self.logger.info(f"Cross-validation scores: {cv_scores}")
        self.logger.info(f"Mean CV accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")

        return cv_scores

    def predict(self, page_data: Dict) -> ClassificationResult:
        """Predict classification for a page"""
        if self.classifier is None:
            raise ValueError("Classifier not trained yet")

        # Extract features
        features = self.extract_comprehensive_features(page_data)
        features_scaled = self.scaler.transform(features.reshape(1, -1))

        # Get predictions
        probabilities = self.classifier.predict_proba(features_scaled)[0]
        predicted_class_idx = np.argmax(probabilities)
        confidence = probabilities[predicted_class_idx]

        # Get class names
        predicted_class = self.label_encoder.inverse_transform([predicted_class_idx])[0]

        # Get alternative classes
        sorted_indices = np.argsort(probabilities)[::-1]
        alternative_classes = []
        for idx in sorted_indices[:3]:
            if idx != predicted_class_idx:
                class_name = self.label_encoder.inverse_transform([idx])[0]
                alternative_classes.append((class_name, probabilities[idx]))

        # Generate reasoning
        reasoning = self._generate_reasoning(page_data, predicted_class, confidence)

        return ClassificationResult(
            predicted_class=predicted_class,
            confidence=confidence,
            alternative_classes=alternative_classes,
            reasoning=reasoning,
            metadata={
                'feature_vector_size': len(features),
                'all_probabilities': dict(zip(
                    self.label_encoder.inverse_transform(range(len(probabilities))),
                    probabilities
                ))
            }
        )

    def _generate_reasoning(self, page_data: Dict, predicted_class: str, confidence: float) -> str:
        """Generate human-readable reasoning for classification"""
        text_content = []
        for line in page_data.get('line_data', []):
            if line.get('type') == 'text' and line.get('text'):
                text_content.append(line['text'])

        combined_text = ' '.join(text_content).lower()

        # Physics keyword analysis
        keyword_indicators = {
            'electrostatics': ['electric field', 'charge', 'coulomb', 'potential'],
            'magnetostatics': ['magnetic field', 'current', 'ampere', 'induction'],
            'electrodynamics': ['electromagnetic', 'radiation', 'wave', 'oscillation'],
            'quantum_mechanics': ['wave function', 'quantum', 'particle', 'uncertainty']
        }

        indicators_found = []
        if predicted_class in keyword_indicators:
            keywords = keyword_indicators[predicted_class]
            for keyword in keywords:
                if keyword in combined_text:
                    indicators_found.append(keyword)

        # Confidence interpretation
        if confidence > 0.8:
            confidence_level = "high confidence"
        elif confidence > 0.6:
            confidence_level = "moderate confidence"
        else:
            confidence_level = "low confidence"

        # Generate reasoning text
        if indicators_found:
            reasoning = f"Classified as {predicted_class} with {confidence_level} "
            reasoning += f"({confidence:.2f}). Indicators: {', '.join(indicators_found[:3])}."
        else:
            reasoning = f"Classified as {predicted_class} with {confidence_level} "
            reasoning += f"({confidence:.2f}). No explicit keywords found, classification based on contextual patterns."

        return reasoning

    def save_model(self, model_path: str):
        """Save trained model"""
        model_dir = Path(model_path).parent
        model_dir.mkdir(parents=True, exist_ok=True)

        model_data = {
            'classifier': self.classifier,
            'label_encoder': self.label_encoder,
            'scaler': self.scaler,
            'model_name': self.model_name,
            'physics_labels': self.physics_labels
        }

        joblib.dump(model_data, model_path)
        self.logger.info(f"Model saved to {model_path}")

    def load_model(self, model_path: str):
        """Load trained model"""
        if not Path(model_path).exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")

        model_data = joblib.load(model_path)
        self.classifier = model_data['classifier']
        self.label_encoder = model_data['label_encoder']
        self.scaler = model_data['scaler']
        self.model_name = model_data['model_name']
        self.physics_labels = model_data['physics_labels']

        self.logger.info(f"Model loaded from {model_path}")

class TOCIntegrationClassifier:
    """Integrates ML classification with TOC-based deterministic classification"""

    def __init__(self, ml_classifier: PhysicsBERTClassifier, toc_data: Dict):
        self.ml_classifier = ml_classifier
        self.toc_data = toc_data
        self.confidence_threshold = 0.7  # Minimum confidence for ML classification

    def classify_with_toc_integration(self, page_data: Dict, page_number: int) -> ClassificationResult:
        """Classify page using both ML and TOC data"""
        # Get ML prediction
        ml_result = self.ml_classifier.predict(page_data)

        # Get TOC-based classification
        toc_result = self._get_toc_classification(page_number)

        # Integrate results
        if ml_result.confidence >= self.confidence_threshold:
            # High confidence ML result takes precedence
            final_result = ml_result
            reasoning = f"ML classification selected (confidence: {ml_result.confidence:.2f}). {ml_result.reasoning}"
        else:
            # Use TOC result or fallback to ML with adjusted confidence
            if toc_result and toc_result.confidence > ml_result.confidence:
                final_result = toc_result
                reasoning = f"TOC classification selected (confidence: {toc_result.confidence:.2f}). {toc_result.reasoning}"
            else:
                final_result = ml_result
                final_result.confidence *= 0.8  # Reduce confidence for low-confidence ML
                reasoning = f"Low-confidence ML result used (adjusted confidence: {final_result.confidence:.2f}). {ml_result.reasoning}"

        final_result.reasoning = reasoning
        final_result.metadata['integration_method'] = 'ml_with_toc_fallback'
        final_result.metadata['ml_confidence'] = ml_result.confidence
        final_result.metadata['toc_classification'] = toc_result.predicted_class if toc_result else None

        return final_result

    def _get_toc_classification(self, page_number: int) -> Optional[ClassificationResult]:
        """Get classification from TOC data"""
        if not self.toc_data:
            return None

        # Find which section this page belongs to
        for section_type in ['parts', 'chapters', 'articles']:
            for section_id, section_data in self.toc_data.get(section_type, {}).items():
                if 'page_start' in section_data and 'page_end' in section_data:
                    if section_data['page_start'] <= page_number <= section_data['page_end']:
                        return ClassificationResult(
                            predicted_class=section_id,
                            confidence=1.0,
                            alternative_classes=[],
                            reasoning=f"TOC-based classification: {section_type} {section_id}",
                            metadata={'source': 'toc', 'page_range': f"{section_data['page_start']}-{section_data['page_end']}"}
                        )

        return None

# Integration with main pipeline
class EnhancedContentClassifier:
    """Enhanced content classification system for Maxwell EM Processor"""

    def __init__(self, model_path: Optional[str] = None):
        self.ml_classifier = PhysicsBERTClassifier()
        self.toc_data = None

        if model_path and Path(model_path).exists():
            self.ml_classifier.load_model(model_path)

    def load_toc_data(self, toc_file: str):
        """Load TOC data for integration"""
        import json
        with open(toc_file, 'r') as f:
            self.toc_data = json.load(f)

    def classify_page(self, page_data: Dict, page_number: int) -> ClassificationResult:
        """Classify a single page"""
        if self.toc_data:
            integrator = TOCIntegrationClassifier(self.ml_classifier, self.toc_data)
            return integrator.classify_with_toc_integration(page_data, page_number)
        else:
            return self.ml_classifier.predict(page_data)

    def batch_classify(self, volume_data: Dict) -> Dict:
        """Classify all pages in a volume"""
        results = {}

        for page_num, page_data in volume_data.get('pages', {}).items():
            try:
                classification = self.classify_page(page_data, int(page_num))
                results[page_num] = {
                    'classification': classification.predicted_class,
                    'confidence': classification.confidence,
                    'reasoning': classification.reasoning,
                    'metadata': classification.metadata
                }
            except Exception as e:
                results[page_num] = {
                    'classification': 'error',
                    'confidence': 0.0,
                    'reasoning': f'Classification failed: {str(e)}',
                    'metadata': {}
                }

        return results

if __name__ == "__main__":
    # Example usage
    classifier = EnhancedContentClassifier()

    # Load training data (this would be your labeled dataset)
    # training_data, labels = load_training_data()
    # classifier.ml_classifier.train_classifier(training_data, labels)
    # classifier.ml_classifier.save_model("models/physics_classifier.pkl")

    # Load TOC data
    # classifier.load_toc_data("output/database/general_toc.json")

    # Classify a page
    # with open("output/database/volume_2_ocr_result.json", 'r') as f:
    #     volume_data = json.load(f)
    # page_1_data = volume_data['pages']['1']
    # result = classifier.classify_page(page_1_data, 1)
    # print(f"Page 1 classified as: {result.predicted_class} (confidence: {result.confidence:.2f})")
```

## 3. Advanced Analytics Implementation

### 3.1 Content Analytics Framework

```python
# src/content_analytics.py
"""
Content Analytics Framework for Maxwell EM Processor
Provides comprehensive statistical analysis of extracted content
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from collections import Counter, defaultdict
import re
import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.manifold import TSNE
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import logging
import json
from pathlib import Path

@dataclass
class ContentAnalytics:
    """Content analytics results structure"""
    volume_statistics: Dict
    linguistic_analysis: Dict
    mathematical_analysis: Dict
    structural_analysis: Dict
    visualizations: Dict

class ContentAnalyticsEngine:
    """Main content analytics engine"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.lda_model = LatentDirichletAllocation(
            n_components=10,
            random_state=42,
            learning_method='batch'
        )

    def analyze_volume_content(self, volume_data: Dict) -> ContentAnalytics:
        """Analyze entire volume content"""
        self.logger.info("Starting comprehensive content analysis")

        # Extract all pages data
        pages = volume_data.get('pages', {})

        # Perform analyses
        volume_stats = self._analyze_volume_statistics(pages)
        linguistic_analysis = self._analyze_linguistic_features(pages)
        mathematical_analysis = self._analyze_mathematical_content(pages)
        structural_analysis = self._analyze_structural_features(pages)

        # Generate visualizations metadata
        visualizations = self._create_visualizations_metadata(
            volume_stats, linguistic_analysis, mathematical_analysis, structural_analysis
        )

        return ContentAnalytics(
            volume_statistics=volume_stats,
            linguistic_analysis=linguistic_analysis,
            mathematical_analysis=mathematical_analysis,
            structural_analysis=structural_analysis,
            visualizations=visualizations
        )

    def _analyze_volume_statistics(self, pages: Dict) -> Dict:
        """Analyze volume-level statistics"""
        self.logger.info("Analyzing volume statistics")

        total_pages = len(pages)
        total_lines = 0
        total_equations = 0
        total_figures = 0
        content_type_counts = Counter()
        confidence_scores = []

        page_statistics = {}

        for page_num, page_data in pages.items():
            line_data = page_data.get('line_data', [])
            total_lines += len(line_data)

            page_lines = 0
            page_equations = 0
            page_figures = 0

            for line in line_data:
                line_type = line.get('type', 'unknown')
                content_type_counts[line_type] += 1
                page_lines += 1

                if line_type == 'equation':
                    page_equations += 1
                    total_equations += 1
                elif line_type in ['figure', 'diagram']:
                    page_figures += 1
                    total_figures += 1

                # Collect confidence scores
                if line.get('confidence') is not None:
                    confidence_scores.append(line['confidence'])

            page_statistics[page_num] = {
                'total_lines': page_lines,
                'equations': page_equations,
                'figures': page_figures,
                'equation_density': page_equations / max(page_lines, 1),
                'figure_density': page_figures / max(page_lines, 1)
            }

        # Calculate derived metrics
        avg_lines_per_page = total_lines / total_pages if total_pages > 0 else 0
        avg_equations_per_page = total_equations / total_pages if total_pages > 0 else 0
        avg_figures_per_page = total_figures / total_pages if total_pages > 0 else 0
        equation_to_text_ratio = total_equations / max(total_lines - total_equations, 1)
        figure_to_text_ratio = total_figures / max(total_lines - total_figures, 1)

        # Confidence statistics
        confidence_stats = {}
        if confidence_scores:
            confidence_stats = {
                'mean': np.mean(confidence_scores),
                'std': np.std(confidence_scores),
                'min': np.min(confidence_scores),
                'max': np.max(confidence_scores),
                'low_confidence_percentage': len([c for c in confidence_scores if c < 0.7]) / len(confidence_scores)
            }

        return {
            'total_pages': total_pages,
            'total_lines': total_lines,
            'total_equations': total_equations,
            'total_figures': total_figures,
            'content_type_distribution': dict(content_type_counts),
            'page_statistics': page_statistics,
            'derived_metrics': {
                'avg_lines_per_page': avg_lines_per_page,
                'avg_equations_per_page': avg_equations_per_page,
                'avg_figures_per_page': avg_figures_per_page,
                'equation_to_text_ratio': equation_to_text_ratio,
                'figure_to_text_ratio': figure_to_text_ratio
            },
            'confidence_statistics': confidence_stats
        }

    def _analyze_linguistic_features(self, pages: Dict) -> Dict:
        """Analyze linguistic features of the content"""
        self.logger.info("Analyzing linguistic features")

        all_text = []
        page_texts = {}
        readability_scores = {}
        vocabulary_complexity = {}

        # Extract text content
        for page_num, page_data in pages.items():
            text_lines = []
            for line in page_data.get('line_data', []):
                if line.get('type') == 'text' and line.get('text'):
                    text_lines.append(line['text'])

            page_text = ' '.join(text_lines)
            page_texts[page_num] = page_text
            all_text.append(page_text)

            # Calculate readability and complexity metrics
            readability_scores[page_num] = self._calculate_readability(page_text)
            vocabulary_complexity[page_num] = self._calculate_vocabulary_complexity(page_text)

        # Combine all text for corpus analysis
        combined_text = ' '.join(all_text)

        # TF-IDF analysis
        if all_text:
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(all_text)
            feature_names = self.tfidf_vectorizer.get_feature_names_out()
            top_terms = self._extract_top_terms(tfidf_matrix, feature_names, top_n=20)

            # Topic modeling
            if len(all_text) >= 10:  # Only if we have enough documents
                topic_modeling = self._perform_topic_modeling(all_text)
            else:
                topic_modeling = {}
        else:
            top_terms = {}
            topic_modeling = {}

        # Technical term analysis
        technical_terms = self._extract_technical_terms(combined_text)

        return {
            'corpus_statistics': {
                'total_words': len(combined_text.split()),
                'unique_words': len(set(combined_text.lower().split())),
                'average_word_length': np.mean([len(word) for word in combined_text.split()]) if combined_text else 0,
                'total_sentences': len(re.split(r'[.!?]+', combined_text)) if combined_text else 0
            },
            'readability_analysis': readability_scores,
            'vocabulary_complexity': vocabulary_complexity,
            'top_terms': top_terms,
            'topic_modeling': topic_modeling,
            'technical_terms': technical_terms,
            'page_texts': page_texts
        }

    def _calculate_readability(self, text: str) -> Dict:
        """Calculate readability metrics"""
        if not text.strip():
            return {'flesch_reading_ease': 0, 'flesch_kincaid_grade': 0}

        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        syllables = sum(self._count_syllables(word) for word in words)

        # Flesch Reading Ease
        if len(sentences) > 0 and len(words) > 0:
            flesch_ease = 206.835 - 1.015 * (len(words) / len(sentences)) - 84.6 * (syllables / len(words))
            flesch_grade = 0.39 * (len(words) / len(sentences)) + 11.8 * (syllables / len(words)) - 15.59
        else:
            flesch_ease = 0
            flesch_grade = 0

        return {
            'flesch_reading_ease': max(0, min(100, flesch_ease)),
            'flesch_kincaid_grade': flesch_grade
        }

    def _count_syllables(self, word: str) -> int:
        """Simple syllable counter"""
        word = word.lower()
        vowels = 'aeiouy'
        syllable_count = 0
        prev_char_vowel = False

        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_char_vowel:
                syllable_count += 1
            prev_char_vowel = is_vowel

        # Subtract silent e at the end
        if word.endswith('e') and syllable_count > 1:
            syllable_count -= 1

        return max(1, syllable_count)

    def _calculate_vocabulary_complexity(self, text: str) -> float:
        """Calculate vocabulary complexity score"""
        if not text.strip():
            return 0.0

        words = text.split()
        if len(words) < 10:  # Too short to analyze
            return 0.0

        # Count complex words (3+ syllables)
        complex_words = sum(1 for word in words if self._count_syllables(word) >= 3)
        complexity_ratio = complex_words / len(words)

        # Calculate type-token ratio (vocabulary diversity)
        unique_words = set(word.lower() for word in words)
        ttr = len(unique_words) / len(words)

        # Combined complexity score
        complexity_score = (complexity_ratio * 0.6) + (ttr * 0.4)
        return min(complexity_score, 1.0)

    def _extract_top_terms(self, tfidf_matrix, feature_names: List[str], top_n: int = 20) -> Dict:
        """Extract top terms by TF-IDF score"""
        mean_scores = np.asarray(tfidf_matrix.mean(axis=0)).ravel()
        top_indices = mean_scores.argsort()[-top_n:][::-1]

        top_terms = {}
        for idx in top_indices:
            term = feature_names[idx]
            score = float(mean_scores[idx])
            top_terms[term] = score

        return top_terms

    def _perform_topic_modeling(self, documents: List[str]) -> Dict:
        """Perform LDA topic modeling"""
        try:
            # Fit LDA model
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(documents)
            self.lda_model.fit(tfidf_matrix)

            # Extract topics
            feature_names = self.tfidf_vectorizer.get_feature_names_out()
            topics = []

            for topic_idx, topic in enumerate(self.lda_model.components_):
                top_words_idx = topic.argsort()[-10:][::-1]
                top_words = [feature_names[i] for i in top_words_idx]
                top_scores = [topic[i] for i in top_words_idx]

                topics.append({
                    'topic_id': topic_idx,
                    'words': top_words,
                    'scores': top_scores
                })

            # Transform documents to topic space
            doc_topics = self.lda_model.transform(tfidf_matrix)
            document_topics = {}
            for i, doc_topic in enumerate(doc_topics):
                document_topics[str(i)] = {
                    'dominant_topic': int(np.argmax(doc_topic)),
                    'topic_distribution': doc_topic.tolist()
                }

            return {
                'topics': topics,
                'document_topics': document_topics,
                'model_parameters': {
                    'n_topics': len(topics),
                    'perplexity': self.lda_model.perplexity(tfidf_matrix),
                    'log_likelihood': self.lda_model.score(tfidf_matrix)
                }
            }

        except Exception as e:
            self.logger.error(f"Topic modeling failed: {str(e)}")
            return {'error': str(e)}

    def _extract_technical_terms(self, text: str) -> Dict:
        """Extract technical/scientific terms"""
        # Physics-specific patterns
        physics_patterns = {
            'mathematical_operators': [
                r'\bintegral\b', r'\bderivative\b', r'\bdifferential\b', r'\bpartial\b',
                r'\bgradient\b', r'\bdivergence\b', r'\bcurl\b', r'\blaplacian\b'
            ],
            'physics_concepts': [
                r'\belectric field\b', r'\bmagnetic field\b', r'\bquantum\b', r'\brelativity\b',
                r'\bthermodynamics\b', r'\boptics\b', r'\bmechanics\b'
            ],
            'mathematical_symbols': [r'∫', r'∑', r'∂', r'∇', r'∏', r'∞', r'∀', r'∃', r'∈']
        }

        technical_terms = {}
        text_lower = text.lower()

        for category, patterns in physics_patterns.items():
            count = 0
            for pattern in patterns:
                count += len(re.findall(pattern, text_lower))
            technical_terms[category] = count

        # Count LaTeX equations
        latex_patterns = [
            r'\\begin\{equation\}',
            r'\$.*\$',
            r'\\[.*\\]',
            r'\\frac\{.*\}\{.*\}'
        ]
        equation_count = sum(len(re.findall(pattern, text, re.DOTALL)) for pattern in latex_patterns)
        technical_terms['latex_equations'] = equation_count

        return technical_terms

    def _analyze_mathematical_content(self, pages: Dict) -> Dict:
        """Analyze mathematical content features"""
        self.logger.info("Analyzing mathematical content")

        equation_analysis = self._analyze_equations(pages)
        mathematical_operator_frequency = self._analyze_mathematical_operators(pages)
        symbol_usage_patterns = self._analyze_symbol_usage(pages)
        complexity_progression = self._analyze_complexity_progression(pages)

        return {
            'equation_analysis': equation_analysis,
            'mathematical_operator_frequency': mathematical_operator_frequency,
            'symbol_usage_patterns': symbol_usage_patterns,
            'complexity_progression': complexity_progression
        }

    def _analyze_equations(self, pages: Dict) -> Dict:
        """Analyze equation characteristics"""
        equations_by_page = {}
        equation_lengths = []
        equation_complexity_scores = []

        for page_num, page_data in pages.items():
            page_equations = []

            for line in page_data.get('line_data', []):
                if line.get('type') == 'equation' and line.get('text'):
                    equation_text = line['text']
                    equation_length = len(equation_text)
                    equation_complexity = self._calculate_equation_complexity(equation_text)

                    page_equations.append({
                        'text': equation_text,
                        'length': equation_length,
                        'complexity': equation_complexity
                    })

                    equation_lengths.append(equation_length)
                    equation_complexity_scores.append(equation_complexity)

            equations_by_page[page_num] = page_equations

        return {
            'equations_by_page': equations_by_page,
            'statistics': {
                'total_equations': len(equation_lengths),
                'avg_length': np.mean(equation_lengths) if equation_lengths else 0,
                'length_std': np.std(equation_lengths) if equation_lengths else 0,
                'avg_complexity': np.mean(equation_complexity_scores) if equation_complexity_scores else 0,
                'complexity_std': np.std(equation_complexity_scores) if equation_complexity_scores else 0,
                'max_length': max(equation_lengths) if equation_lengths else 0,
                'min_length': min(equation_lengths) if equation_lengths else 0
            }
        }

    def _calculate_equation_complexity(self, equation: str) -> float:
        """Calculate mathematical complexity of an equation"""
        complexity_factors = {
            'integrals': equation.count('∫') * 3,
            'sums': equation.count('∑') * 2,
            'derivatives': equation.count('∂') * 2,
            'fractions': equation.count('\\frac') * 1.5,
            'superscripts': equation.count('^') * 1,
            'subscripts': equation.count('_') * 0.5,
            'greek_letters': len(re.findall(r'\\[a-zA-Z]+', equation)) * 0.3,
            'parentheses_depth': self._calculate_parentheses_depth(equation) * 0.2
        }

        total_complexity = sum(complexity_factors.values())
        normalized_complexity = min(total_complexity / len(equation) * 10 if equation else 0, 1.0)

        return normalized_complexity

    def _calculate_parentheses_depth(self, equation: str) -> int:
        """Calculate maximum nesting depth of parentheses"""
        max_depth = 0
        current_depth = 0

        for char in equation:
            if char in '({[':
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char in ')}]':
                current_depth -= 1

        return max_depth

    def _analyze_mathematical_operators(self, pages: Dict) -> Dict:
        """Analyze frequency of mathematical operators"""
        operator_counts = Counter()

        for page_data in pages.values():
            for line in page_data.get('line_data', []):
                if line.get('type') == 'equation' and line.get('text'):
                    equation = line['text']
                    # Count mathematical operators
                    operators = ['+', '-', '=', '×', '÷', '±', '∓', '≠', '≈', '≤', '≥',
                               '<', '>', '∫', '∑', '∏', '∂', '∇', '√', '∞', '∀', '∃']

                    for operator in operators:
                        count = equation.count(operator)
                        if count > 0:
                            operator_counts[operator] += count

        return dict(operator_counts)

    def _analyze_symbol_usage(self, pages: Dict) -> Dict:
        """Analyze symbol usage patterns"""
        symbol_patterns = {
            'greek_letters': [],
            'mathematical_symbols': [],
            'physics_notation': []
        }

        greek_letters = ['α', 'β', 'γ', 'δ', 'ε', 'ζ', 'η', 'θ', 'ι', 'κ', 'λ', 'μ',
                        'ν', 'ξ', 'π', 'ρ', 'σ', 'τ', 'υ', 'φ', 'χ', 'ψ', 'ω']

        for page_data in pages.values():
            text_content = ' '.join([
                line.get('text', '') for line in page_data.get('line_data', [])
                if line.get('text')
            ])

            # Count Greek letters
            for letter in greek_letters:
                count = text_content.count(letter)
                if count > 0:
                    symbol_patterns['greek_letters'].append((letter, count))

            # Count mathematical symbols
            math_symbols = ['∫', '∑', '∏', '∂', '∇', '√', '∞', '∀', '∃', '∈', '∉', '⊂', '⊃', '∪', '∩']
            for symbol in math_symbols:
                count = text_content.count(symbol)
                if count > 0:
                    symbol_patterns['mathematical_symbols'].append((symbol, count))

        return symbol_patterns

    def _analyze_complexity_progression(self, pages: Dict) -> Dict:
        """Analyze how complexity progresses through the volume"""
        page_complexities = {}

        for page_num, page_data in pages.items():
            # Calculate page complexity
            text_complexity = 0
            equation_complexity = 0

            # Text complexity
            text_lines = [
                line.get('text', '') for line in page_data.get('line_data', [])
                if line.get('type') == 'text' and line.get('text')
            ]
            if text_lines:
                combined_text = ' '.join(text_lines)
                text_complexity = self._calculate_vocabulary_complexity(combined_text)

            # Equation complexity
            equations = [
                line.get('text', '') for line in page_data.get('line_data', [])
                if line.get('type') == 'equation' and line.get('text')
            ]
            if equations:
                equation_complexities = [
                    self._calculate_equation_complexity(eq) for eq in equations
                ]
                equation_complexity = np.mean(equation_complexities)

            # Combined complexity
            combined_complexity = (text_complexity * 0.4) + (equation_complexity * 0.6)
            page_complexities[page_num] = {
                'text_complexity': text_complexity,
                'equation_complexity': equation_complexity,
                'combined_complexity': combined_complexity
            }

        # Analyze progression trends
        sorted_pages = sorted(page_complexities.items())
        complexities = [data['combined_complexity'] for _, data in sorted_pages]
        page_numbers = [int(page) for page, _ in sorted_pages]

        if complexities:
            # Calculate trend
            x = np.array(page_numbers)
            y = np.array(complexities)
            correlation = np.corrcoef(x, y)[0, 1] if len(x) > 1 else 0

            # Calculate moving average
            window_size = min(20, len(complexities))
            moving_avg = np.convolve(complexities, np.ones(window_size)/window_size, mode='valid')

            trend_analysis = {
                'complexity_trend_correlation': correlation,
                'trend_direction': 'increasing' if correlation > 0.1 else 'decreasing' if correlation < -0.1 else 'stable',
                'complexity_range': (min(complexities), max(complexities)),
                'average_complexity': np.mean(complexities),
                'moving_average': moving_avg.tolist(),
                'moving_average_start_page': page_numbers[window_size//2] if len(moving_avg) > 0 else 0
            }
        else:
            trend_analysis = {}

        return {
            'page_complexities': page_complexities,
            'trend_analysis': trend_analysis
        }

    def _analyze_structural_features(self, pages: Dict) -> Dict:
        """Analyze structural features and organization"""
        self.logger.info("Analyzing structural features")

        # Layout analysis
        layout_analysis = self._analyze_layout_patterns(pages)

        # Cross-reference analysis
        cross_reference_analysis = self._analyze_cross_references(pages)

        # Section hierarchy analysis
        hierarchy_analysis = self._analyze_section_hierarchy(pages)

        return {
            'layout_analysis': layout_analysis,
            'cross_reference_analysis': cross_reference_analysis,
            'hierarchy_analysis': hierarchy_analysis
        }

    def _analyze_layout_patterns(self, pages: Dict) -> Dict:
        """Analyze page layout patterns"""
        layout_features = {}

        for page_num, page_data in pages.items():
            line_data = page_data.get('line_data', [])
            if not line_data:
                continue

            # Analyze spatial distribution
            positions = []
            line_types = []

            for line in line_data:
                region = line.get('region', {})
                if region:
                    positions.append((
                        region.get('top_left_x', 0),
                        region.get('top_left_y', 0),
                        region.get('width', 0),
                        region.get('height', 0)
                    ))
                line_types.append(line.get('type', 'unknown'))

            # Calculate layout metrics
            if positions:
                x_coords = [pos[0] for pos in positions]
                y_coords = [pos[1] for pos in positions]

                layout_features[page_num] = {
                    'horizontal_distribution': {
                        'mean': np.mean(x_coords),
                        'std': np.std(x_coords),
                        'range': (min(x_coords), max(x_coords))
                    },
                    'vertical_distribution': {
                        'mean': np.mean(y_coords),
                        'std': np.std(y_coords),
                        'range': (min(y_coords), max(y_coords))
                    },
                    'line_type_distribution': dict(Counter(line_types))
                }

        return layout_features

    def _analyze_cross_references(self, pages: Dict) -> Dict:
        """Analyze cross-references within the document"""
        cross_references = []
        reference_patterns = [
            r'equation\s+(\d+\.\d+)',
            r'figure\s+(\d+\.\d+)',
            r'chapter\s+(\d+)',
            r'article\s+(\d+)',
            r'section\s+(\d+\.\d+)',
            r'page\s+(\d+)',
            r'theorem\s+(\d+\.\d+)',
            r'lemma\s+(\d+\.\d+)',
            r'proof\s+of\s+theorem\s+(\d+\.\d+)'
        ]

        for page_num, page_data in pages.items():
            text_content = ' '.join([
                line.get('text', '') for line in page_data.get('line_data', [])
                if line.get('type') == 'text' and line.get('text')
            ])

            page_references = []
            for pattern in reference_patterns:
                matches = re.findall(pattern, text_content, re.IGNORECASE)
                for match in matches:
                    page_references.append({
                        'pattern': pattern,
                        'reference': match,
                        'context': 'found'
                    })

            if page_references:
                cross_references.append({
                    'page': page_num,
                    'references': page_references
                })

        # Build reference network
        reference_network = self._build_reference_network(cross_references)

        return {
            'total_cross_references': sum(len(ref['references']) for ref in cross_references),
            'references_by_page': {ref['page']: len(ref['references']) for ref in cross_references},
            'reference_types': self._categorize_reference_types(cross_references),
            'reference_network': reference_network
        }

    def _build_reference_network(self, cross_references: List[Dict]) -> Dict:
        """Build network graph of cross-references"""
        try:
            G = nx.Graph()

            # Add nodes for pages
            for ref in cross_references:
                page = ref['page']
                G.add_node(f"page_{page}", type='page')

            # Add edges for references
            for ref in cross_references:
                source_page = ref['page']
                for reference in ref['references']:
                    if reference['pattern'].startswith(r'equation'):
                        target = f"equation_{reference['reference']}"
                    elif reference['pattern'].startswith(r'figure'):
                        target = f"figure_{reference['reference']}"
                    elif reference['pattern'].startswith(r'chapter'):
                        target = f"chapter_{reference['reference']}"
                    else:
                        target = f"ref_{reference['reference']}"

                    G.add_node(target, type='reference')
                    G.add_edge(f"page_{source_page}", target)

            # Calculate network metrics
            if G.number_of_nodes() > 1:
                centrality = nx.degree_centrality(G)
                clustering = nx.clustering(G)
                connected_components = nx.number_connected_components(G)

                return {
                    'nodes': G.number_of_nodes(),
                    'edges': G.number_of_edges(),
                    'connected_components': connected_components,
                    'avg_centrality': np.mean(list(centrality.values())) if centrality else 0,
                    'avg_clustering': np.mean(list(clustering.values())) if clustering else 0,
                    'diameter': nx.diameter(G) if nx.is_connected(G) else float('inf')
                }
            else:
                return {'error': 'Network too small to analyze'}

        except Exception as e:
            self.logger.error(f"Reference network analysis failed: {str(e)}")
            return {'error': str(e)}

    def _categorize_reference_types(self, cross_references: List[Dict]) -> Dict:
        """Categorize types of references found"""
        reference_types = Counter()

        for ref in cross_references:
            for reference in ref['references']:
                if 'equation' in reference['pattern']:
                    reference_types['equation'] += 1
                elif 'figure' in reference['pattern']:
                    reference_types['figure'] += 1
                elif 'chapter' in reference['pattern']:
                    reference_types['chapter'] += 1
                elif 'article' in reference['pattern']:
                    reference_types['article'] += 1
                elif 'section' in reference['pattern']:
                    reference_types['section'] += 1
                else:
                    reference_types['other'] += 1

        return dict(reference_types)

    def _analyze_section_hierarchy(self, pages: Dict) -> Dict:
        """Analyze document section hierarchy"""
        # Look for section headers and their patterns
        section_patterns = [
            r'^\s*(chapter|article|section|subsection)\s+\d+',
            r'^\s*\d+\.\s+[A-Z]',
            r'^\s*[A-Z][A-Z\s]+$',  # All caps headers
            r'^\s*Part\s+[IVX]+',  # Roman numeral parts
        ]

        hierarchy_levels = {}
        section_boundaries = []

        for page_num, page_data in pages.items():
            for line in page_data.get('line_data', []):
                if line.get('type') == 'text' and line.get('text'):
                    text = line['text'].strip()

                    # Check for section patterns
                    for i, pattern in enumerate(section_patterns):
                        if re.match(pattern, text, re.IGNORECASE):
                            hierarchy_levels[page_num] = {
                                'level': i,
                                'text': text,
                                'pattern': pattern
                            }
                            section_boundaries.append({
                                'page': page_num,
                                'level': i,
                                'text': text
                            })
                            break

        return {
            'hierarchy_levels': hierarchy_levels,
            'section_boundaries': section_boundaries,
            'total_sections': len(section_boundaries),
            'avg_section_length': len(pages) / max(len(section_boundaries), 1)
        }

    def _create_visualizations_metadata(self, volume_stats: Dict, linguistic_analysis: Dict,
                                      mathematical_analysis: Dict, structural_analysis: Dict) -> Dict:
        """Create metadata for generating visualizations"""
        return {
            'volume_statistics_charts': [
                'content_type_pie_chart',
                'quality_metrics_gauge',
                'page_statistics_heatmap'
            ],
            'linguistic_analysis_charts': [
                'word_frequency_bar_chart',
                'readability_progression_line',
                'topic_modeling_scatter'
            ],
            'mathematical_analysis_charts': [
                'equation_complexity_distribution',
                'operator_frequency_chart',
                'complexity_progression_trend'
            ],
            'structural_analysis_charts': [
                'layout_heatmap',
                'reference_network_graph',
                'section_hierarchy_tree'
            ],
            'interactive_dashboards': [
                'content_explorer',
                'mathematical_analysis_dashboard',
                'structural_insights'
            ]
        }

    def save_analytics_report(self, analytics: ContentAnalytics, output_path: str):
        """Save comprehensive analytics report"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Convert numpy types to JSON serializable types
        def convert_numpy_types(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, dict):
                return {key: convert_numpy_types(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy_types(item) for item in obj]
            return obj

        analytics_dict = {
            'volume_statistics': analytics.volume_statistics,
            'linguistic_analysis': analytics.linguistic_analysis,
            'mathematical_analysis': analytics.mathematical_analysis,
            'structural_analysis': analytics.structural_analysis,
            'visualizations': analytics.visualizations
        }

        analytics_dict = convert_numpy_types(analytics_dict)

        with open(output_file, 'w') as f:
            json.dump(analytics_dict, f, indent=2)

        self.logger.info(f"Analytics report saved to {output_file}")

if __name__ == "__main__":
    # Example usage
    analytics_engine = ContentAnalyticsEngine()

    # Load volume data
    # with open("output/database/volume_2_ocr_result.json", 'r') as f:
    #     volume_data = json.load(f)

    # Perform analysis
    # analytics = analytics_engine.analyze_volume_content(volume_data)

    # Save results
    # analytics_engine.save_analytics_report(analytics, "output/analytics/volume_2_content_analytics.json")

    print("Content Analytics Engine initialized successfully!")
```

## 4. Implementation Integration Guide

### 4.1 Pipeline Integration

```python
# src/integrated_pipeline.py
"""
Integrated Pipeline for Enhanced Maxwell EM Processor
Combines quality assessment, ML classification, and content analytics
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
import logging
from datetime import datetime

from src.quality_assessment import QualityAssessmentPipeline
from src.ml_content_classifier import EnhancedContentClassifier
from src.content_analytics import ContentAnalyticsEngine
from src.data_models import PDFOCRResult, save_model_to_json

class IntegratedProcessingPipeline:
    """Integrated pipeline combining all data science enhancements"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Initialize components
        self.quality_assessment = QualityAssessmentPipeline()
        self.content_classifier = EnhancedContentClassifier()
        self.content_analytics = ContentAnalyticsEngine()

        self.processing_results = {}

    def process_volume(self, volume_data: Dict, volume_id: str) -> Dict:
        """Process entire volume with all enhancements"""
        self.logger.info(f"Starting integrated processing for {volume_id}")

        processing_start_time = datetime.now()

        try:
            # Step 1: Quality Assessment
            self.logger.info("Step 1: Performing quality assessment")
            quality_results = self._perform_quality_assessment(volume_data, volume_id)

            # Step 2: Content Classification
            self.logger.info("Step 2: Performing ML-enhanced content classification")
            classification_results = self._perform_content_classification(volume_data, volume_id)

            # Step 3: Content Analytics
            self.logger.info("Step 3: Performing comprehensive content analytics")
            analytics_results = self._perform_content_analytics(volume_data, volume_id)

            # Step 4: Generate integrated report
            self.logger.info("Step 4: Generating integrated processing report")
            integrated_report = self._generate_integrated_report(
                volume_id, quality_results, classification_results, analytics_results
            )

            # Step 5: Save all results
            self._save_processing_results(volume_id, integrated_report)

            processing_end_time = datetime.now()
            processing_duration = (processing_end_time - processing_start_time).total_seconds()

            self.logger.info(f"Integrated processing completed for {volume_id} in {processing_duration:.2f} seconds")

            return {
                'volume_id': volume_id,
                'processing_duration_seconds': processing_duration,
                'quality_assessment': quality_results,
                'content_classification': classification_results,
                'content_analytics': analytics_results,
                'integrated_report': integrated_report
            }

        except Exception as e:
            self.logger.error(f"Error in integrated processing for {volume_id}: {str(e)}")
            raise

    def _perform_quality_assessment(self, volume_data: Dict, volume_id: str) -> Dict:
        """Perform comprehensive quality assessment"""
        # Assess overall volume quality
        volume_quality = self.quality_assessment.assess_volume(volume_data)

        # Assess individual page qualities
        page_qualities = {}
        for page_num, page_data in volume_data.get('pages', {}).items():
            page_quality = self.quality_assessment.assess_page(page_data)
            page_qualities[page_num] = {
                'overall_quality': page_quality.overall_quality,
                'ocr_quality': page_quality.ocr_quality,
                'content_quality': page_quality.content_quality,
                'processing_quality': page_quality.processing_quality,
                'quality_class': page_quality.quality_class,
                'issues': page_quality.issues
            }

        return {
            'volume_quality_summary': volume_quality.get('volume_quality_summary', {}),
            'page_qualities': page_qualities,
            'quality_issues': volume_quality.get('quality_issues', []),
            'recommendations': volume_quality.get('recommendations', [])
        }

    def _perform_content_classification(self, volume_data: Dict, volume_id: str) -> Dict:
        """Perform ML-enhanced content classification"""
        # Load TOC data if available
        toc_file = Path(f"output/database/general_toc.json")
        if toc_file.exists():
            self.content_classifier.load_toc_data(str(toc_file))

        # Perform batch classification
        classification_results = self.content_classifier.batch_classify(volume_data)

        # Analyze classification confidence distribution
        confidence_scores = [
            result.get('confidence', 0.0) for result in classification_results.values()
        ]
        confidence_stats = {
            'mean_confidence': sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0,
            'high_confidence_pages': len([c for c in confidence_scores if c >= 0.8]),
            'medium_confidence_pages': len([c for c in confidence_scores if 0.5 <= c < 0.8]),
            'low_confidence_pages': len([c for c in confidence_scores if c < 0.5])
        }

        return {
            'classification_results': classification_results,
            'confidence_statistics': confidence_stats,
            'classification_summary': self._summarize_classifications(classification_results)
        }

    def _summarize_classifications(self, classification_results: Dict) -> Dict:
        """Summarize classification results"""
        classifications = [result.get('classification', 'unknown') for result in classification_results.values()]

        # Count classifications
        classification_counts = {}
        for classification in classifications:
            classification_counts[classification] = classification_counts.get(classification, 0) + 1

        # Calculate percentages
        total_pages = len(classification_results)
        classification_percentages = {
            cls: count / total_pages * 100 for cls, count in classification_counts.items()
        }

        return {
            'classification_distribution': classification_counts,
            'classification_percentages': classification_percentages,
            'total_classified_pages': total_pages,
            'most_common_classification': max(classification_counts.items(), key=lambda x: x[1])[0] if classification_counts else 'none'
        }

    def _perform_content_analytics(self, volume_data: Dict, volume_id: str) -> Dict:
        """Perform comprehensive content analytics"""
        # Perform analytics
        analytics = self.content_analytics.analyze_volume_content(volume_data)

        # Convert to dictionary format
        analytics_dict = {
            'volume_statistics': analytics.volume_statistics,
            'linguistic_analysis': analytics.linguistic_analysis,
            'mathematical_analysis': analytics.mathematical_analysis,
            'structural_analysis': analytics.structural_analysis,
            'visualizations': analytics.visualizations
        }

        return analytics_dict

    def _generate_integrated_report(self, volume_id: str, quality_results: Dict,
                                  classification_results: Dict, analytics_results: Dict) -> Dict:
        """Generate comprehensive integrated processing report"""
        # Calculate overall processing score
        quality_score = quality_results.get('volume_quality_summary', {}).get('avg_overall_quality', 0.0)
        classification_confidence = classification_results.get('confidence_statistics', {}).get('mean_confidence', 0.0)
        analytics_completeness = self._calculate_analytics_completeness(analytics_results)

        overall_score = (quality_score * 0.4) + (classification_confidence * 0.3) + (analytics_completeness * 0.3)

        # Generate insights
        insights = self._generate_processing_insights(quality_results, classification_results, analytics_results)

        return {
            'processing_metadata': {
                'volume_id': volume_id,
                'processing_timestamp': datetime.now().isoformat(),
                'overall_processing_score': overall_score,
                'processing_status': 'completed'
            },
            'key_metrics': {
                'quality_score': quality_score,
                'classification_confidence': classification_confidence,
                'analytics_completeness': analytics_completeness,
                'total_pages_processed': len(quality_results.get('page_qualities', {})),
                'total_equations_found': analytics_results.get('volume_statistics', {}).get('total_equations', 0),
                'total_figures_found': analytics_results.get('volume_statistics', {}).get('total_figures', 0)
            },
            'processing_insights': insights,
            'quality_summary': self._summarize_quality(quality_results),
            'content_summary': self._summarize_content(classification_results, analytics_results),
            'recommendations': self._generate_overall_recommendations(quality_results, classification_results)
        }

    def _calculate_analytics_completeness(self, analytics_results: Dict) -> float:
        """Calculate completeness score for analytics"""
        required_sections = ['volume_statistics', 'linguistic_analysis', 'mathematical_analysis', 'structural_analysis']
        completed_sections = sum(1 for section in required_sections if section in analytics_results)

        return completed_sections / len(required_sections)

    def _generate_processing_insights(self, quality_results: Dict, classification_results: Dict,
                                    analytics_results: Dict) -> List[str]:
        """Generate key insights from processing results"""
        insights = []

        # Quality insights
        quality_summary = quality_results.get('volume_quality_summary', {})
        if quality_summary.get('avg_overall_quality', 0) < 0.6:
            insights.append("⚠️ Quality Alert: Overall quality score is below target threshold")

        # Classification insights
        confidence_stats = classification_results.get('confidence_statistics', {})
        if confidence_stats.get('low_confidence_pages', 0) > 10:
            insights.append("🔍 Classification Alert: High number of low-confidence classifications detected")

        # Content insights
        volume_stats = analytics_results.get('volume_statistics', {})
        equation_count = volume_stats.get('total_equations', 0)
        if equation_count > 1000:
            insights.append(f"📊 Content Insight: High equation density ({equation_count} equations) suggests advanced mathematical content")

        # Analytics insights
        linguistic_analysis = analytics_results.get('linguistic_analysis', {})
        top_terms = linguistic_analysis.get('top_terms', {})
        if 'quantum' in top_terms or 'electromagnetic' in top_terms:
            insights.append("🎯 Domain Insight: Content appears to be specialized physics literature")

        if not insights:
            insights.append("✅ Processing completed successfully with good quality metrics")

        return insights

    def _summarize_quality(self, quality_results: Dict) -> Dict:
        """Summarize quality assessment results"""
        quality_summary = quality_results.get('volume_quality_summary', {})
        page_qualities = quality_results.get('page_qualities', {})

        # Count quality classes
        quality_class_counts = {}
        for page_data in page_qualities.values():
            quality_class = page_data.get('quality_class', 'unknown')
            quality_class_counts[quality_class] = quality_class_counts.get(quality_class, 0) + 1

        return {
            'avg_quality_score': quality_summary.get('avg_overall_quality', 0),
            'quality_distribution': quality_class_counts,
            'quality_issues_count': len(quality_results.get('quality_issues', [])),
            'recommendations_count': len(quality_results.get('recommendations', []))
        }

    def _summarize_content(self, classification_results: Dict, analytics_results: Dict) -> Dict:
        """Summarize content analysis results"""
        classification_summary = classification_results.get('classification_summary', {})
        volume_stats = analytics_results.get('volume_statistics', {})
        linguistic_analysis = analytics_results.get('linguistic_analysis', {})
        mathematical_analysis = analytics_results.get('mathematical_analysis', {})

        return {
            'content_types': classification_summary.get('classification_distribution', {}),
            'volume_statistics': {
                'total_pages': volume_stats.get('total_pages', 0),
                'total_lines': volume_stats.get('total_lines', 0),
                'total_equations': volume_stats.get('total_equations', 0),
                'total_figures': volume_stats.get('total_figures', 0)
            },
            'linguistic_features': {
                'top_terms': list(linguistic_analysis.get('top_terms', {}).keys())[:10],
                'vocabulary_complexity': linguistic_analysis.get('corpus_statistics', {}).get('unique_words', 0) / max(linguistic_analysis.get('corpus_statistics', {}).get('total_words', 1), 1)
            },
            'mathematical_features': {
                'equation_statistics': mathematical_analysis.get('equation_analysis', {}).get('statistics', {}),
                'operator_frequency': mathematical_analysis.get('mathematical_operator_frequency', {})
            }
        }

    def _generate_overall_recommendations(self, quality_results: Dict, classification_results: Dict) -> List[str]:
        """Generate overall processing recommendations"""
        recommendations = []

        # Quality-based recommendations
        quality_issues = quality_results.get('quality_issues', [])
        if any('Low OCR confidence' in issue for issue in quality_issues):
            recommendations.append("IMPROVE OCR: Consider reprocessing with higher resolution or better image quality")

        if any('Processing inefficiency' in issue for issue in quality_issues):
            recommendations.append("OPTIMIZE PROCESSING: Review and optimize processing pipeline parameters")

        # Classification-based recommendations
        confidence_stats = classification_results.get('confidence_statistics', {})
        if confidence_stats.get('low_confidence_pages', 0) > len(confidence_stats) * 0.2:  # More than 20% low confidence
            recommendations.append("ENHANCE CLASSIFICATION: Consider additional training data or model refinement")

        # Default recommendation
        if not recommendations:
            recommendations.append("PROCESSING SUCCESS: Current processing quality meets standards. Continue monitoring.")

        return recommendations

    def _save_processing_results(self, volume_id: str, integrated_report: Dict):
        """Save all processing results"""
        output_dir = Path(f"output/integrated_processing/{volume_id}")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save integrated report
        report_file = output_dir / f"integrated_processing_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(integrated_report, f, indent=2, default=str)

        self.logger.info(f"Integrated processing results saved to {report_file}")

def main():
    """Main execution function for integrated pipeline"""
    import argparse

    parser = argparse.ArgumentParser(description='Run integrated Maxwell EM processor with data science enhancements')
    parser.add_argument('--volume-data', required=True, help='Path to volume OCR result JSON file')
    parser.add_argument('--volume-id', required=True, help='Volume identifier (e.g., volume_2)')
    parser.add_argument('--output-dir', default='output/integrated_processing', help='Output directory')

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('output/logs/integrated_processing.log'),
            logging.StreamHandler()
        ]
    )

    logger = logging.getLogger(__name__)

    try:
        # Load volume data
        with open(args.volume_data, 'r') as f:
            volume_data = json.load(f)

        # Initialize and run integrated pipeline
        pipeline = IntegratedProcessingPipeline()
        results = pipeline.process_volume(volume_data, args.volume_id)

        logger.info(f"Integrated processing completed successfully for {args.volume_id}")
        logger.info(f"Overall processing score: {results['integrated_report']['processing_metadata']['overall_processing_score']:.3f}")

    except Exception as e:
        logger.error(f"Integrated processing failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
```

This comprehensive implementation plan provides:

1. **Quality Assessment System**: Automated quality scoring with ML models and real-time monitoring dashboard
2. **ML-Enhanced Classification**: BERT-based physics content classification with TOC integration
3. **Advanced Analytics Framework**: Comprehensive content analysis including linguistic, mathematical, and structural analysis
4. **Integrated Pipeline**: Complete workflow combining all enhancements

The implementation uses industry-standard libraries and follows best practices for:
- Error handling and logging
- Model training and evaluation
- Data validation and quality assurance
- Scalable architecture design
- Comprehensive documentation

This provides a solid foundation for transforming the Maxwell EM processor into a comprehensive scientific document intelligence platform.
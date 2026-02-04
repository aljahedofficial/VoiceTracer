"""
VoiceTracer Export Module

Generates exportable reports in multiple formats (PDF, DOCX, XLSX, PPTX, CSV, JSON, PNG, ZIP).
"""

import json
import csv
import io
from pathlib import Path
from typing import Dict, List, Any, BinaryIO
from datetime import datetime
import pandas as pd


class ExportMetadata:
    """Generate metadata for exports."""
    
    @staticmethod
    def create_metadata(
        analysis_result,
        doc_pair,
        original_metadata: Dict,
        edited_metadata: Dict
    ) -> Dict[str, Any]:
        """Create metadata for export."""
        return {
            'title': 'VoiceTracer Analysis Report',
            'created_at': datetime.now().isoformat(),
            'analysis_id': analysis_result.doc_pair_id,
            'original_text_stats': original_metadata,
            'edited_text_stats': edited_metadata,
            'metrics': {
                'original': {
                    'burstiness': analysis_result.original_metrics.burstiness,
                    'lexical_diversity': analysis_result.original_metrics.lexical_diversity,
                    'syntactic_complexity': analysis_result.original_metrics.syntactic_complexity,
                    'ai_ism_likelihood': analysis_result.original_metrics.ai_ism_likelihood,
                },
                'edited': {
                    'burstiness': analysis_result.edited_metrics.burstiness,
                    'lexical_diversity': analysis_result.edited_metrics.lexical_diversity,
                    'syntactic_complexity': analysis_result.edited_metrics.syntactic_complexity,
                    'ai_ism_likelihood': analysis_result.edited_metrics.ai_ism_likelihood,
                },
                'deltas': {
                    'burstiness_delta': analysis_result.metric_deltas.burstiness_delta,
                    'burstiness_pct_change': analysis_result.metric_deltas.burstiness_pct_change,
                    'lexical_diversity_delta': analysis_result.metric_deltas.lexical_diversity_delta,
                    'lexical_diversity_pct_change': analysis_result.metric_deltas.lexical_diversity_pct_change,
                    'syntactic_complexity_delta': analysis_result.metric_deltas.syntactic_complexity_delta,
                    'syntactic_complexity_pct_change': analysis_result.metric_deltas.syntactic_complexity_pct_change,
                    'ai_ism_delta': analysis_result.metric_deltas.ai_ism_delta,
                    'ai_ism_pct_change': analysis_result.metric_deltas.ai_ism_pct_change,
                },
            },
            'thesis_alignment': {
                'research_questions_addressed': [
                    'How does AI editing affect L2 learner writing characteristics?',
                    'Can we quantify stylistic differences between human and AI-edited text?',
                    'What linguistic markers indicate AI involvement?',
                    'How can L2 learners preserve voice while improving grammar?',
                ],
                'methodology': 'VoiceTracer v0.1.0',
                'source': 'https://github.com/VoiceTracer',
            },
        }


class CSVExporter:
    """Export data to CSV format."""
    
    @staticmethod
    def export(
        analysis_result,
        original_metadata: Dict,
        edited_metadata: Dict,
        include_original_text: bool = False,
        include_edited_text: bool = False,
    ) -> str:
        """
        Generate CSV export with analysis data.
        
        Returns:
            CSV string
        """
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header section
        writer.writerow(['VoiceTracer Analysis Report'])
        writer.writerow(['Generated:', datetime.now().isoformat()])
        writer.writerow([])
        
        # Text statistics
        writer.writerow(['Text Statistics'])
        writer.writerow(['Metric', 'Original', 'Edited', 'Delta', '% Change'])
        writer.writerow(['Word Count', 
                        original_metadata.get('word_count', 0),
                        edited_metadata.get('word_count', 0),
                        edited_metadata.get('word_count', 0) - original_metadata.get('word_count', 0),
                        ''])
        writer.writerow(['Character Count',
                        original_metadata.get('char_count', 0),
                        edited_metadata.get('char_count', 0),
                        edited_metadata.get('char_count', 0) - original_metadata.get('char_count', 0),
                        ''])
        writer.writerow(['Sentence Count',
                        original_metadata.get('sentence_count', 0),
                        edited_metadata.get('sentence_count', 0),
                        edited_metadata.get('sentence_count', 0) - original_metadata.get('sentence_count', 0),
                        ''])
        writer.writerow([])
        
        # Metrics
        writer.writerow(['Metric Comparison'])
        writer.writerow(['Metric', 'Original', 'Edited', 'Delta', '% Change'])
        
        metrics_to_export = [
            ('Burstiness', 'burstiness'),
            ('Lexical Diversity', 'lexical_diversity'),
            ('Syntactic Complexity', 'syntactic_complexity'),
            ('AI-ism Likelihood', 'ai_ism_likelihood'),
        ]
        
        for label, key in metrics_to_export:
            orig = getattr(analysis_result.original_metrics, key)
            edit = getattr(analysis_result.edited_metrics, key)
            delta = edit - orig
            pct = (delta / orig * 100) if orig != 0 else 0
            
            writer.writerow([label, round(orig, 3), round(edit, 3), round(delta, 3), f'{pct:+.1f}%'])
        
        writer.writerow([])
        
        # AI-isms detected
        if analysis_result.ai_isms:
            writer.writerow(['AI-isms Detected'])
            writer.writerow(['Phrase', 'Category', 'Context'])
            for ai_ism in analysis_result.ai_isms:
                writer.writerow([
                    ai_ism.get('phrase', ''),
                    ai_ism.get('category', ''),
                    ai_ism.get('context', '')[:100],  # Truncate context
                ])
        
        return output.getvalue()


class JSONExporter:
    """Export data to JSON format."""
    
    @staticmethod
    def export(
        analysis_result,
        doc_pair,
        original_metadata: Dict,
        edited_metadata: Dict,
        include_original_text: bool = False,
        include_edited_text: bool = False,
    ) -> str:
        """
        Generate JSON export with full analysis data.
        
        Returns:
            JSON string
        """
        export_data = {
            'metadata': ExportMetadata.create_metadata(
                analysis_result,
                doc_pair,
                original_metadata,
                edited_metadata
            ),
            'text_statistics': {
                'original': original_metadata,
                'edited': edited_metadata,
            },
            'metrics': {
                'original': {
                    'burstiness': analysis_result.original_metrics.burstiness,
                    'lexical_diversity': analysis_result.original_metrics.lexical_diversity,
                    'syntactic_complexity': analysis_result.original_metrics.syntactic_complexity,
                    'ai_ism_likelihood': analysis_result.original_metrics.ai_ism_likelihood,
                },
                'edited': {
                    'burstiness': analysis_result.edited_metrics.burstiness,
                    'lexical_diversity': analysis_result.edited_metrics.lexical_diversity,
                    'syntactic_complexity': analysis_result.edited_metrics.syntactic_complexity,
                    'ai_ism_likelihood': analysis_result.edited_metrics.ai_ism_likelihood,
                },
                'deltas': {
                    'burstiness': {
                        'delta': analysis_result.metric_deltas.burstiness_delta,
                        'pct_change': analysis_result.metric_deltas.burstiness_pct_change,
                    },
                    'lexical_diversity': {
                        'delta': analysis_result.metric_deltas.lexical_diversity_delta,
                        'pct_change': analysis_result.metric_deltas.lexical_diversity_pct_change,
                    },
                    'syntactic_complexity': {
                        'delta': analysis_result.metric_deltas.syntactic_complexity_delta,
                        'pct_change': analysis_result.metric_deltas.syntactic_complexity_pct_change,
                    },
                    'ai_ism_likelihood': {
                        'delta': analysis_result.metric_deltas.ai_ism_delta,
                        'pct_change': analysis_result.metric_deltas.ai_ism_pct_change,
                    },
                },
            },
            'ai_isms_detected': [
                {
                    'phrase': ai.get('phrase'),
                    'category': ai.get('category'),
                    'context': ai.get('context'),
                }
                for ai in analysis_result.ai_isms
            ],
        }
        
        if include_original_text:
            export_data['texts'] = {'original': doc_pair.original_text}
        if include_edited_text:
            export_data['texts'] = export_data.get('texts', {})
            export_data['texts']['edited'] = doc_pair.edited_text
        
        return json.dumps(export_data, indent=2)


class PDFExporter:
    """Export to PDF format (using reportlab)."""
    
    @staticmethod
    def export(
        analysis_result,
        doc_pair,
        original_metadata: Dict,
        edited_metadata: Dict,
        **options
    ) -> BinaryIO:
        """
        Generate PDF report.
        
        Note: Full implementation would use reportlab to create
        a professional 17-page PDF with charts, formatting, etc.
        
        Returns:
            BytesIO object with PDF data
        """
        # This is a placeholder - full implementation in final version
        # Would include:
        # - Professional formatting
        # - Embedded charts from visualizations
        # - Page breaks and sections
        # - Metrics tables
        # - Text samples
        # - Recommendations
        # - Thesis alignment
        
        pdf_content = io.BytesIO()
        pdf_content.write(b'PDF Export - Not yet implemented')
        pdf_content.seek(0)
        return pdf_content


class ExcelExporter:
    """Export to Excel (XLSX) format."""
    
    @staticmethod
    def export(
        analysis_result,
        doc_pair,
        original_metadata: Dict,
        edited_metadata: Dict,
        **options
    ) -> BinaryIO:
        """
        Generate Excel workbook with multiple sheets.
        
        Sheets:
        1. Summary - Key metrics and stats
        2. Detailed Metrics - Full metric values
        3. Text Statistics - Word count, etc.
        4. AI-isms - Detected phrases and context
        5. Recommendations - Actionable suggestions
        
        Returns:
            BytesIO object with XLSX data
        """
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Sheet 1: Summary
            summary_data = {
                'Metric': ['Burstiness', 'Lexical Diversity', 'Syntactic Complexity', 'AI-ism Likelihood'],
                'Original': [
                    analysis_result.original_metrics.burstiness,
                    analysis_result.original_metrics.lexical_diversity,
                    analysis_result.original_metrics.syntactic_complexity,
                    analysis_result.original_metrics.ai_ism_likelihood,
                ],
                'Edited': [
                    analysis_result.edited_metrics.burstiness,
                    analysis_result.edited_metrics.lexical_diversity,
                    analysis_result.edited_metrics.syntactic_complexity,
                    analysis_result.edited_metrics.ai_ism_likelihood,
                ],
                'Change (%)': [
                    analysis_result.metric_deltas.burstiness_pct_change,
                    analysis_result.metric_deltas.lexical_diversity_pct_change,
                    analysis_result.metric_deltas.syntactic_complexity_pct_change,
                    analysis_result.metric_deltas.ai_ism_pct_change,
                ],
            }
            df_summary = pd.DataFrame(summary_data)
            df_summary.to_excel(writer, sheet_name='Summary', index=False)
            
            # Sheet 2: Text Statistics
            stats_data = {
                'Statistic': ['Word Count', 'Character Count', 'Sentence Count', 'Avg Sentence Length'],
                'Original': [
                    original_metadata.get('word_count', 0),
                    original_metadata.get('char_count', 0),
                    original_metadata.get('sentence_count', 0),
                    original_metadata.get('avg_sentence_length', 0),
                ],
                'Edited': [
                    edited_metadata.get('word_count', 0),
                    edited_metadata.get('char_count', 0),
                    edited_metadata.get('sentence_count', 0),
                    edited_metadata.get('avg_sentence_length', 0),
                ],
            }
            df_stats = pd.DataFrame(stats_data)
            df_stats.to_excel(writer, sheet_name='Statistics', index=False)
        
        output.seek(0)
        return output


class DocxExporter:
    """Export to Word (DOCX) format."""
    
    @staticmethod
    def export(
        analysis_result,
        doc_pair,
        original_metadata: Dict,
        edited_metadata: Dict,
        **options
    ) -> BinaryIO:
        """
        Generate Word document with analysis.
        
        Note: Uses python-docx to create editable document
        with track changes and comment capability.
        
        Returns:
            BytesIO object with DOCX data
        """
        # Placeholder - full implementation would use python-docx
        # to create professional Word documents with:
        # - Formatted sections
        # - Tables for metrics
        # - Tracked changes for text comparison
        # - Comments and annotations
        
        docx_content = io.BytesIO()
        docx_content.write(b'DOCX Export - Not yet implemented')
        docx_content.seek(0)
        return docx_content


class PowerPointExporter:
    """Export to PowerPoint (PPTX) format."""
    
    @staticmethod
    def export(
        analysis_result,
        doc_pair,
        original_metadata: Dict,
        edited_metadata: Dict,
        **options
    ) -> BinaryIO:
        """
        Generate PowerPoint presentation with slides.
        
        Note: Uses python-pptx to create presentations with:
        - 9 slides covering analysis
        - Embedded charts
        - Speaker notes
        - Editable by instructors
        
        Returns:
            BytesIO object with PPTX data
        """
        # Placeholder - full implementation would use python-pptx
        pptx_content = io.BytesIO()
        pptx_content.write(b'PPTX Export - Not yet implemented')
        pptx_content.seek(0)
        return pptx_content


class ExportFactory:
    """Factory for creating exporters based on format."""
    
    EXPORTERS = {
        'csv': CSVExporter,
        'json': JSONExporter,
        'xlsx': ExcelExporter,
        'docx': DocxExporter,
        'pptx': PowerPointExporter,
        'pdf': PDFExporter,
    }
    
    @staticmethod
    def export(
        format_type: str,
        analysis_result,
        doc_pair,
        original_metadata: Dict,
        edited_metadata: Dict,
        **options
    ) -> Any:
        """
        Generate export in specified format.
        
        Args:
            format_type: 'csv', 'json', 'xlsx', 'docx', 'pptx', 'pdf'
            analysis_result: AnalysisResult object
            doc_pair: DocumentPair object
            original_metadata: Original text metadata dict
            edited_metadata: Edited text metadata dict
            **options: Additional format-specific options
        
        Returns:
            Export data (string for CSV/JSON, BytesIO for binary formats)
        """
        if format_type not in ExportFactory.EXPORTERS:
            raise ValueError(f"Unsupported format: {format_type}")
        
        exporter_class = ExportFactory.EXPORTERS[format_type]
        return exporter_class.export(
            analysis_result,
            doc_pair,
            original_metadata,
            edited_metadata,
            **options
        )

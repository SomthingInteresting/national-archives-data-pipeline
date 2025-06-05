from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import pandas as pd
from typing import Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def generate_pdf_report(metadata: Dict[str, Any], output_path: str) -> None:
    """
    Generate a PDF report from legislation metadata.
    
    Args:
        metadata: Dictionary containing legislation metadata
        output_path: Path to save the PDF report
        
    Raises:
        IOError: If PDF cannot be created
    """
    try:
        # Create document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Get styles
        styles = getSampleStyleSheet()
        title_style = styles['Heading1']
        heading_style = styles['Heading2']
        normal_style = styles['Normal']
        
        # Create content
        content = []
        
        # Title
        content.append(Paragraph(metadata['title'], title_style))
        content.append(Spacer(1, 12))
        
        # Basic Information
        content.append(Paragraph('Basic Information', heading_style))
        content.append(Spacer(1, 12))
        
        basic_info = [
            ['Year:', str(metadata['year'])],
            ['Document URI:', metadata['document_uri']],
            ['Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        ]
        
        basic_table = Table(basic_info, colWidths=[2*inch, 4*inch])
        basic_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT')
        ]))
        content.append(basic_table)
        content.append(Spacer(1, 24))
        
        # Sections
        content.append(Paragraph('Sections', heading_style))
        content.append(Spacer(1, 12))
        
        sections_df = pd.DataFrame(metadata['sections'])
        if not sections_df.empty:
            sections_data = [['ID', 'Title', 'Content']]
            for _, row in sections_df.iterrows():
                sections_data.append([
                    row['id'],
                    row['title'],
                    row['content'][:100] + '...' if len(row['content']) > 100 else row['content']
                ])
            
            sections_table = Table(sections_data, colWidths=[1*inch, 2*inch, 3*inch])
            sections_table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('PADDING', (0, 0), (-1, -1), 6),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT')
            ]))
            content.append(sections_table)
        else:
            content.append(Paragraph('No sections found.', normal_style))
        
        content.append(Spacer(1, 24))
        
        # Amendments
        content.append(Paragraph('Amendments', heading_style))
        content.append(Spacer(1, 12))
        
        amendments_df = pd.DataFrame(metadata['amendments'])
        if not amendments_df.empty:
            amendments_data = [['ID', 'Type', 'Date', 'Description']]
            for _, row in amendments_df.iterrows():
                amendments_data.append([
                    row['id'],
                    row['type'],
                    row['date'],
                    row['description'][:100] + '...' if len(row['description']) > 100 else row['description']
                ])
            
            amendments_table = Table(amendments_data, colWidths=[1*inch, 1*inch, 1*inch, 3*inch])
            amendments_table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('PADDING', (0, 0), (-1, -1), 6),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT')
            ]))
            content.append(amendments_table)
        else:
            content.append(Paragraph('No amendments found.', normal_style))
        
        # Build PDF
        doc.build(content)
        
    except Exception as e:
        logger.error(f'Failed to generate PDF report: {str(e)}')
        raise 
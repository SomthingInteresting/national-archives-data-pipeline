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
            ['Year:', str(metadata.get('year', 'Unknown'))],
            ['Legislation Type:', str(metadata.get('legislation_type', 'Unknown'))],
            ['Number:', str(metadata.get('number', 'Unknown'))],
            ['Document URI:', Paragraph(metadata.get('document_uri', ''), normal_style)],
            ['Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        ]
        
        basic_table = Table(basic_info, colWidths=[2*inch, 4*inch])
        basic_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('PADDING', (0, 0), (-1, -1), 4),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        content.append(basic_table)
        content.append(Spacer(1, 24))
        
        # Sections
        content.append(Paragraph('Sections', heading_style))
        content.append(Spacer(1, 12))
        
        sections_df = pd.DataFrame(metadata['sections'])
        if not sections_df.empty:
            sections_data = [['Number', 'Title', 'Content']]
            for _, row in sections_df.iterrows():
                # Truncate content more aggressively and wrap in Paragraph
                content_text = row['content'][:150] + '...' if len(row['content']) > 150 else row['content']
                title_text = row['title'][:80] + '...' if len(row['title']) > 80 else row['title']
                
                sections_data.append([
                    Paragraph(str(row.get('number', row['id'])), normal_style),
                    Paragraph(title_text, normal_style),
                    Paragraph(content_text, normal_style)
                ])
            
            sections_table = Table(sections_data, colWidths=[0.8*inch, 2.2*inch, 3*inch])
            sections_table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('PADDING', (0, 0), (-1, -1), 4),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP')
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
            amendments_data = [['Type', 'Description', 'Affecting URI']]
            for _, row in amendments_df.iterrows():
                # Truncate and wrap long descriptions
                desc_text = row['description'][:120] + '...' if len(row['description']) > 120 else row['description']
                uri_text = row['affecting_uri'][-40:] if len(row['affecting_uri']) > 40 else row['affecting_uri']
                
                amendments_data.append([
                    Paragraph(str(row['type']), normal_style),
                    Paragraph(desc_text, normal_style),
                    Paragraph(uri_text, normal_style)
                ])
            
            amendments_table = Table(amendments_data, colWidths=[1.5*inch, 3*inch, 1.5*inch])
            amendments_table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('PADDING', (0, 0), (-1, -1), 4),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP')
            ]))
            content.append(amendments_table)
        else:
            content.append(Paragraph('No amendments found.', normal_style))
        
        # Build PDF
        doc.build(content)
        
    except Exception as e:
        logger.error(f'Failed to generate PDF report: {str(e)}')
        raise 
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
        content.append(Paragraph(metadata.get('title', 'Unknown Title'), title_style))
        content.append(Spacer(1, 12))
        
        # Basic Information
        content.append(Paragraph('Basic Information', heading_style))
        content.append(Spacer(1, 12))
        
        basic_info = [
            ['Year:', str(metadata.get('year', 'Unknown'))],
            ['Legislation Type:', str(metadata.get('legislation_type', 'Unknown'))],
            ['Number:', str(metadata.get('legislation_number', metadata.get('number', 'Unknown')))],
            ['Sections Count:', str(metadata.get('sections_count', 'Unknown'))],
            ['Schedules Count:', str(metadata.get('schedules_count', 'Unknown'))],
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
        
        # Long Title if available
        if metadata.get('long_title'):
            content.append(Paragraph('Long Title', heading_style))
            content.append(Spacer(1, 12))
            content.append(Paragraph(metadata['long_title'], normal_style))
            content.append(Spacer(1, 24))
        
        # Key Sections
        content.append(Paragraph('Key Sections', heading_style))
        content.append(Spacer(1, 12))
        
        # Use key_sections instead of sections
        key_sections = metadata.get('key_sections', [])
        if key_sections:
            sections_data = [['Number', 'Title']]
            for section in key_sections[:20]:  # Limit to first 20 sections
                section_num = section.get('number', 'N/A')
                section_title = section.get('title', 'N/A')
                
                # Truncate title if too long
                if len(section_title) > 80:
                    section_title = section_title[:80] + '...'
                
                sections_data.append([
                    Paragraph(str(section_num), normal_style),
                    Paragraph(section_title, normal_style)
                ])
            
            sections_table = Table(sections_data, colWidths=[1*inch, 5*inch])
            sections_table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('PADDING', (0, 0), (-1, -1), 4),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP')
            ]))
            content.append(sections_table)
        else:
            content.append(Paragraph('No key sections extracted.', normal_style))
        
        content.append(Spacer(1, 24))
        
        # Amendments (if available)
        amendments = metadata.get('amendments', [])
        if amendments:
            content.append(Paragraph('Amendments', heading_style))
            content.append(Spacer(1, 12))
            
            amendments_data = [['Type', 'Description', 'Affecting URI']]
            for amendment in amendments:
                # Handle different amendment data structures
                if isinstance(amendment, dict):
                    amend_type = amendment.get('type', 'Unknown')
                    description = amendment.get('description', 'No description')
                    affecting_uri = amendment.get('affecting_uri', 'No URI')
                else:
                    amend_type = str(amendment)
                    description = 'Amendment record'
                    affecting_uri = 'N/A'
                
                # Truncate and wrap long descriptions
                if len(description) > 120:
                    description = description[:120] + '...'
                if len(affecting_uri) > 40:
                    affecting_uri = '...' + affecting_uri[-40:]
                
                amendments_data.append([
                    Paragraph(str(amend_type), normal_style),
                    Paragraph(description, normal_style),
                    Paragraph(affecting_uri, normal_style)
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
            content.append(Paragraph('Amendments', heading_style))
            content.append(Spacer(1, 12))
            content.append(Paragraph('No amendments data available.', normal_style))
        
        # Build PDF
        doc.build(content)
        logger.info(f'PDF report successfully generated: {output_path}')
        
    except Exception as e:
        logger.error(f'Failed to generate PDF report: {str(e)}')
        raise 
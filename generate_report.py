#!/usr/bin/env python3
"""
Generate a PDF report for a specific piece of legislation.
"""

import sys
sys.path.append('src')

from api_client import LegislationAPIClient
from metadata_extractor import LegislationMetadataExtractor
from reporting import generate_pdf_report

def create_report(legislation_id, output_filename=None):
    """
    Create a PDF report for the specified legislation.
    
    Args:
        legislation_id: ID of legislation (e.g., 'ukpga/2020/1')
        output_filename: Optional custom filename for the PDF
    """
    print(f"Generating report for {legislation_id}...")
    
    # Set default filename if not provided
    if output_filename is None:
        safe_id = legislation_id.replace('/', '_')
        output_filename = f"data/processed/report_{safe_id}.pdf"
    
    try:
        # 1. Fetch XML data
        print("Fetching XML data...")
        client = LegislationAPIClient()
        xml_content = client.get_legislation_xml(legislation_id)
        
        # 2. Extract metadata
        print("Extracting metadata...")
        extractor = LegislationMetadataExtractor()
        metadata = extractor.extract_metadata(xml_content)
        
        # 3. Generate PDF report
        print(f"Generating PDF report: {output_filename}")
        generate_pdf_report(metadata, output_filename)
        
        print(f"✅ Report successfully generated: {output_filename}")
        return output_filename
        
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        return None

if __name__ == '__main__':
    # Example usage
    examples = [
        'ukpga/2020/1',  # Coronavirus Act 2020
        'ukpga/2023/52', # Data Protection and Digital Information Act 2023
        'uksi/2020/350'  # Example Statutory Instrument
    ]
    
    if len(sys.argv) > 1:
        # Use command line argument
        legislation_id = sys.argv[1]
        create_report(legislation_id)
    else:
        # Use first example
        print("No legislation ID provided. Using example...")
        create_report(examples[0])
        print(f"\nTo generate a report for a specific legislation, run:")
        print(f"python generate_report.py <legislation_id>")
        print(f"\nExamples:")
        for example in examples:
            print(f"  python generate_report.py {example}") 
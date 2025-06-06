# National Archives Data Pipeline

A Python-based data pipeline for processing and analysing UK legislation data from legislation.gov.uk. This project serves as a **technical demonstration** of data engineering concepts, API integration, and automated document processing.

## 🎯 Purpose

This project is designed for **educational, technical, and demonstrative purposes**:

- **Data Engineering Learning**: Demonstrates ETL pipeline patterns, XML processing, and API integration
- **Technical Skills Showcase**: Shows proficiency in Python, XML parsing, PDF generation, and error handling
- **Automation Example**: Illustrates how to build robust data processing workflows
- **Analysis Tool**: Enables systematic analysis of UK legislation structure and content

**Note**: This is a learning tool and analysis framework, not intended as a replacement for official systems.

## ✨ Features

- **API Integration**: Robust client for legislation.gov.uk API with error handling
- **XML Processing**: Advanced parsing with proper namespace handling
- **Metadata Extraction**: Comprehensive extraction of legislation metadata and structure
- **PDF Report Generation**: Automated creation of formatted legislation reports
- **Data Validation**: XML schema validation against official legislation schemas
- **Error Handling**: Comprehensive logging and graceful error management

## 🛠️ Technical Achievements

### XML Namespace Resolution & CLML Integration

- Integrated official Crown Legislation Markup Language (CLML) schemas
- Solved complex XML namespace issues using government standards instead of guesswork
- Implemented proper namespace mapping for leg (legislation), dc (Dublin Core), and xsi schemas
- Built schema-driven validation against official UK government XML standards

### Section Title Extraction

- Reverse-engineered legislation XML structure to extract meaningful section titles
- Implemented smart text parsing to handle various legislation formats
- Overcame challenges with nested XML elements and missing title tags

### Robust Pipeline Architecture

- Built fault-tolerant data processing pipeline
- Implemented proper separation of concerns across modules
- Created reusable components for different legislation types

## 🚀 Quick Start

1. **Setup Environment**:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Test the Pipeline**:

```bash
python test_pipeline.py
```

3. **Generate a Report**:

```bash
python generate_report.py
```

4. **Test CLML Schema Validation**:

```bash
python validate_with_schema.py
```

## 📊 Usage Examples

### Basic Pipeline Test

```python
from src.api_client import LegislationAPIClient
from src.metadata_extractor import MetadataExtractor

# Initialize components
client = LegislationAPIClient()
extractor = MetadataExtractor()

# Fetch and process legislation
xml_content = client.get_legislation_xml('ukpga', '2020', '7')  # Coronavirus Act 2020
metadata = extractor.extract_metadata(xml_content)

print(f"Title: {metadata['title']}")
print(f"Sections: {len(metadata['key_sections'])}")
```

### Generate PDF Report

The pipeline can automatically generate formatted PDF reports:

```bash
python generate_report.py
# Outputs: data/processed/report_ukpga_2020_7.pdf
```

## 🏗️ Project Structure

```
national-archives-data-pipeline/
├── src/
│   ├── api_client.py         # legislation.gov.uk API client
│   ├── atom_parser.py        # Atom feed parser
│   ├── xml_validator.py      # XML schema validator
│   ├── metadata_extractor.py # Metadata extraction engine
│   └── reporting.py          # PDF report generator
├── data/
│   ├── raw/schemas/          # Official CLML schemas and documentation
│   └── processed/            # Generated reports
├── test_pipeline.py          # Pipeline testing script
├── generate_report.py        # Report generation script
├── validate_with_schema.py   # CLML schema validation demo
├── requirements.txt
└── README.md
```

## 🔍 What This Project Demonstrates

### Data Engineering Skills

- **ETL Pipeline Design**: Extract from API, Transform XML data, Load into reports
- **Error Handling**: Robust exception handling and logging
- **Data Validation**: XML schema validation and data quality checks
- **Modular Architecture**: Clean separation of concerns and reusable components

### Technical Problem Solving

- **XML Namespace Challenges**: Solved complex namespace issues in government XML data
- **API Integration**: Built reliable client for external government API
- **Document Processing**: Automated extraction of structured data from legislation
- **Report Generation**: Created professional PDF reports from raw XML data

### Python Proficiency

- **Object-Oriented Design**: Well-structured classes and inheritance
- **External Libraries**: Effective use of requests, lxml, reportlab, pandas
- **Testing**: Comprehensive testing and validation scripts
- **Documentation**: Clear code documentation and error messages

## 🧪 Sample Output

The pipeline successfully processes legislation like the **Coronavirus Act 2020** and extracts:

- **Title**: "Coronavirus Act 2020"
- **Type**: "ukpga" (UK Public General Act)
- **Year**: 2020, **Number**: 7
- **Sections**: 102 sections with meaningful titles
- **Structure**: Detailed breakdown of schedules and provisions

## 📚 Learning Outcomes

This project showcases:

1. **Real-world API integration** with government data sources
2. **Advanced XML processing** with namespace handling
3. **Automated document generation** from structured data
4. **Error-resilient pipeline architecture**
5. **Professional Python development practices**

## 🔧 Dependencies

- **requests**: HTTP API client
- **lxml**: XML processing and parsing
- **pandas**: Data manipulation and analysis
- **reportlab**: PDF generation
- **xmlschema**: XML validation

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

_This project demonstrates technical proficiency in data engineering, API integration, and automated document processing. It serves as both a learning tool and a practical example of building robust data pipelines with Python._

# National Archives Data Pipeline

A Python-based data pipeline for processing and analyzing legislation data from legislation.gov.uk.

## Overview

This project provides tools for:

- Fetching legislation data via the legislation.gov.uk API
- Parsing Atom feeds and XML documents
- Validating XML against official schemas
- Extracting and analyzing metadata
- Generating reports and visualizations

## Setup

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables:
   Create a `.env` file with:

```
LEGISLATION_API_KEY=your_api_key_here
```

## Project Structure

```
national-archives-data-pipeline/
├── data/
│   ├── raw/          # Raw XML and Atom feed data
│   └── processed/    # Processed and cleaned data
├── src/
│   ├── api_client.py         # API client for legislation.gov.uk
│   ├── atom_parser.py        # Atom feed parser
│   ├── xml_validator.py      # XML schema validator
│   ├── metadata_extractor.py # Metadata extraction tools
│   └── reporting.py          # Report generation
├── notebooks/
│   └── analysis.ipynb        # Jupyter notebook for analysis
├── requirements.txt
└── README.md
```

## Usage

See `notebooks/analysis.ipynb` for example usage and analysis.

## Data Model

The project follows the data model described in the [legislation.gov.uk documentation](https://legislation.github.io/data-documentation/).

## License

This project is licensed under the MIT License - see the LICENSE file for details.

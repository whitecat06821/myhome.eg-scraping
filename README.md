# MyHome.ge Web Scraper

A Python web scraper for extracting phone numbers from myhome.ge.

## Installation

1. Create virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # macOS/Linux
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the scraper:
```bash
python main.py
```

Run tests:
```bash
pytest
```

## Output

Generates two CSV files:
- `agents.csv`: Agent phone numbers
- `owners.csv`: Property owner phone numbers

## Features

- Modular design with clear separation of concerns
- Handles dynamic JavaScript content
- Comprehensive error handling and logging
- Unit tests for parsing logic
- Respects rate limiting and robots.txt

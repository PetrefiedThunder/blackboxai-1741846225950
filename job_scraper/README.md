# Job Search Assistant

A personalized job scraping tool built with Python and Flask that searches and refines job listings based on Christopher's professional profile. The tool scrapes job listings from major job boards, scores them based on relevance, and presents them in a modern web interface.

## Features

- **Intelligent Job Scraping**: Scrapes jobs from Indeed and LinkedIn
- **Smart Job Refinement**: Scores jobs based on:
  - Title match
  - Required skills match
  - Technical skills match
  - Industry relevance
  - Location preference
  - Salary range
- **Modern Web Interface**:
  - Clean, responsive design using Tailwind CSS
  - Real-time job searching and filtering
  - Sort by match score, date, or salary
  - Interactive job cards with detailed information
- **Customizable Search Parameters**:
  - Multiple job titles
  - Location and radius
  - Salary range
  - Industry preferences
- **Robust Error Handling**:
  - Rate limiting protection
  - Automatic retries
  - Comprehensive logging

## Setup

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Access the web interface:
```
http://localhost:8000
```

## Project Structure

```
job_scraper/
├── src/
│   ├── __init__.py
│   ├── config.py           # Configuration settings
│   ├── scraper.py         # Core scraping logic
│   ├── logger.py          # Logging configuration
│   └── parsers/           # Job board specific parsers
├── templates/
│   └── index.html         # Web interface template
├── data/
│   └── jobs.json          # Scraped job data
├── logs/                  # Log files
├── requirements.txt       # Project dependencies
├── app.py                # Flask application
└── README.md             # Documentation
```

## Configuration

The scraper can be customized by modifying `src/config.py`:

- `SEARCH_TITLES`: List of job titles to search for
- `REQUIRED_SKILLS`: Essential skills to match
- `TECHNICAL_SKILLS`: Technical skills to look for
- `TARGET_INDUSTRIES`: Preferred industries
- `LOCATION`: Geographic preferences
- `SCORING_WEIGHTS`: Adjust importance of different matching criteria

## Usage

1. Start the application:
```bash
python app.py
```

2. Open your web browser and navigate to `http://localhost:8000`

3. Use the search form to:
   - Select desired job titles
   - Set location and radius
   - Specify salary range
   - Click "Search Jobs" to start scraping

4. View results:
   - Jobs are displayed as cards with match scores
   - Sort by match score, date, or salary
   - Click "View Job" to open the original posting
   - Use "Refresh Jobs" to update listings

## Error Handling

The application includes comprehensive error handling:

- Network request retries with exponential backoff
- Rate limiting protection
- Detailed logging of errors and operations
- User-friendly error messages in the UI

## Logging

Logs are stored in the `logs` directory with:

- Timestamp
- Log level
- Detailed message
- Error context when applicable

## Development

To contribute or modify:

1. Clone the repository
2. Create a virtual environment
3. Install development dependencies
4. Make changes
5. Test thoroughly
6. Submit pull request

## Security Notes

- Change the Flask secret key in production
- Use appropriate rate limiting
- Handle sensitive data securely
- Follow job board terms of service

## License

MIT License - Feel free to modify and use as needed.

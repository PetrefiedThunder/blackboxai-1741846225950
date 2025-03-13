"""
Configuration settings for the job scraper.
Contains search parameters, URLs, and other constants.
"""

# Base URLs for job boards
BASE_URLS = {
    'indeed': 'https://www.indeed.com/jobs',
    'linkedin': 'https://www.linkedin.com/jobs/search'
}

# Search parameters based on Christopher's profile
SEARCH_TITLES = [
    'Program Manager',
    'Business Development Manager',
    'Digital Transformation Lead',
    'Technical Product Manager',
    'Operations Manager',
    'Stakeholder Engagement Manager'
]

# Key skills to look for in job descriptions
REQUIRED_SKILLS = [
    'Salesforce',
    'CRM',
    'Project Management',
    'Business Intelligence',
    'Process Automation',
    'Change Management',
    'Stakeholder Engagement'
]

# Technical skills to match
TECHNICAL_SKILLS = [
    'Python',
    'SQL',
    'Tableau',
    'Looker',
    'Workflow Automation'
]

# Target industries
TARGET_INDUSTRIES = [
    'Technology',
    'Healthcare',
    'Nonprofit',
    'Privacy',
    'Security',
    'Government',
    'Public Sector'
]

# Location preferences
LOCATION = {
    'city': 'Los Angeles',
    'state': 'CA',
    'radius': 25  # miles
}

# Experience level (in years)
MIN_EXPERIENCE = 5
MAX_EXPERIENCE = 15

# Salary range (annual, USD)
MIN_SALARY = 80000
MAX_SALARY = 200000

# HTTP request configuration
REQUEST_CONFIG = {
    'timeout': 30,
    'max_retries': 3,
    'retry_delay': 5,
    'headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
}

# Refinement scoring weights (0-1)
SCORING_WEIGHTS = {
    'title_match': 0.3,
    'skills_match': 0.25,
    'industry_match': 0.2,
    'location_match': 0.15,
    'salary_match': 0.1
}

# Job post age limit (in days)
MAX_JOB_AGE = 30

# Output settings
OUTPUT_DIRECTORY = 'data'
JSON_FILENAME = 'jobs.json'
CSV_FILENAME = 'jobs.csv'

# Logging configuration
LOG_CONFIG = {
    'filename': 'job_scraper.log',
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
}

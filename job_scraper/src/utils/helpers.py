"""
Helper functions for the job scraper.
"""

import random
import time
from typing import Dict, Any, Optional
import re
from datetime import datetime, timedelta
from fake_useragent import UserAgent

def get_random_user_agent() -> str:
    """
    Get a random user agent string.
    
    Returns:
        str: Random user agent string
    """
    try:
        ua = UserAgent()
        return ua.random
    except:
        # Fallback user agents if fake-useragent fails
        default_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
        ]
        return random.choice(default_agents)

def sleep_with_jitter(base_delay: float = 2.0, jitter: float = 1.0) -> None:
    """
    Sleep for a random amount of time to avoid detection.
    
    Args:
        base_delay (float): Base delay in seconds
        jitter (float): Maximum random jitter to add
    """
    jitter_time = random.uniform(0, jitter)
    time.sleep(base_delay + jitter_time)

def extract_salary(text: str) -> Optional[Dict[str, float]]:
    """
    Extract salary information from text.
    
    Args:
        text (str): Text containing salary information
        
    Returns:
        dict: Dictionary with min and max salary, or None if no salary found
    """
    # Common salary patterns
    patterns = [
        r'\$(\d{2,3}(?:,\d{3})*(?:\.\d{2})?)\s*-\s*\$(\d{2,3}(?:,\d{3})*(?:\.\d{2})?)',  # $50,000 - $70,000
        r'\$(\d{2,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:to|–)\s*\$(\d{2,3}(?:,\d{3})*(?:\.\d{2})?)',  # $50,000 to $70,000
        r'\$(\d{2,3}(?:,\d{3})*(?:\.\d{2})?)/(?:yr|year|annual)',  # $50,000/yr
        r'(\d{2,3}(?:,\d{3})*(?:\.\d{2})?)[Kk]',  # 50K
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            groups = match.groups()
            if len(groups) == 2:  # Range found
                min_salary = float(groups[0].replace(',', ''))
                max_salary = float(groups[1].replace(',', ''))
                return {'min': min_salary, 'max': max_salary}
            elif len(groups) == 1:  # Single value found
                salary = float(groups[0].replace(',', ''))
                if 'k' in text.lower():
                    salary *= 1000
                return {'min': salary * 0.9, 'max': salary * 1.1}  # Estimate range
    return None

def parse_date_posted(text: str) -> Optional[datetime]:
    """
    Parse job posting date from text.
    
    Args:
        text (str): Text containing date information
        
    Returns:
        datetime: Parsed date, or None if parsing fails
    """
    now = datetime.now()
    
    # Common patterns
    patterns = {
        r'(\d+)\s*hours?\s*ago': lambda x: now - timedelta(hours=int(x)),
        r'(\d+)\s*days?\s*ago': lambda x: now - timedelta(days=int(x)),
        r'(\d+)\s*weeks?\s*ago': lambda x: now - timedelta(weeks=int(x)),
        r'(\d+)\s*months?\s*ago': lambda x: now - timedelta(days=int(x)*30),
        r'today': lambda x: now,
        r'yesterday': lambda x: now - timedelta(days=1),
        r'just\s*posted': lambda x: now,
    }
    
    text = text.lower()
    for pattern, date_func in patterns.items():
        match = re.search(pattern, text)
        if match:
            groups = match.groups()
            return date_func(groups[0] if groups else None)
    
    return None

def clean_job_title(title: str) -> str:
    """
    Clean and standardize job title.
    
    Args:
        title (str): Raw job title
        
    Returns:
        str: Cleaned job title
    """
    # Remove special characters and extra whitespace
    title = re.sub(r'[^\w\s-]', '', title)
    title = ' '.join(title.split())
    
    # Standardize common variations
    replacements = {
        'sr': 'senior',
        'jr': 'junior',
        'mgr': 'manager',
        'dev': 'developer',
        'eng': 'engineer',
        'prog': 'programmer',
    }
    
    words = title.lower().split()
    words = [replacements.get(word, word) for word in words]
    return ' '.join(words).title()

def calculate_experience_years(text: str) -> Optional[Dict[str, int]]:
    """
    Extract years of experience requirement from text.
    
    Args:
        text (str): Job description text
        
    Returns:
        dict: Dictionary with min and max years, or None if not found
    """
    patterns = [
        r'(\d+)\+?\s*-\s*(\d+)\+?\s*years?(?:\s+of)?\s+experience',  # 5-7 years experience
        r'(\d+)\+?\s*years?(?:\s+of)?\s+experience',  # 5+ years experience
        r'minimum\s+(?:of\s+)?(\d+)\s+years?(?:\s+of)?\s+experience',  # minimum of 5 years experience
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            groups = match.groups()
            if len(groups) == 2:  # Range found
                return {'min': int(groups[0]), 'max': int(groups[1])}
            elif len(groups) == 1:  # Single value found
                years = int(groups[0])
                return {'min': years, 'max': years + 3}
    return None

def extract_skills(text: str, skill_list: list) -> list:
    """
    Extract mentioned skills from text.
    
    Args:
        text (str): Text to search for skills
        skill_list (list): List of skills to look for
        
    Returns:
        list: List of found skills
    """
    found_skills = []
    text = text.lower()
    
    for skill in skill_list:
        # Create pattern that handles variations
        pattern = r'\b' + re.escape(skill.lower()) + r'(?:ing|ed|s)?\b'
        if re.search(pattern, text):
            found_skills.append(skill)
    
    return found_skills

def format_salary(salary_dict: Dict[str, float]) -> str:
    """
    Format salary range for display.
    
    Args:
        salary_dict (dict): Dictionary with min and max salary
        
    Returns:
        str: Formatted salary string
    """
    if not salary_dict:
        return "Salary not specified"
        
    min_salary = salary_dict.get('min', 0)
    max_salary = salary_dict.get('max', 0)
    
    if min_salary and max_salary:
        return f"${min_salary:,.0f} - ${max_salary:,.0f}"
    elif min_salary:
        return f"${min_salary:,.0f}+"
    elif max_salary:
        return f"Up to ${max_salary:,.0f}"
    
    return "Salary not specified"

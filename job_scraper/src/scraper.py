"""
Core scraping functionality for the job search tool.
Includes job refinement and scoring based on candidate's profile.
"""

import requests
import json
import os
from datetime import datetime
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
from fake_useragent import UserAgent
import time
import random

from .config import (
    BASE_URLS, SEARCH_TITLES, REQUIRED_SKILLS, 
    TECHNICAL_SKILLS, TARGET_INDUSTRIES, LOCATION,
    REQUEST_CONFIG, SCORING_WEIGHTS, OUTPUT_DIRECTORY
)
from .logger import logger, log_job_found, log_error, log_scraping_progress, log_refinement_result

class JobScraper:
    def __init__(self):
        """Initialize the job scraper with necessary configurations."""
        self.session = requests.Session()
        self.ua = UserAgent()
        self.jobs = []
        
        # Create output directory if it doesn't exist
        if not os.path.exists(OUTPUT_DIRECTORY):
            os.makedirs(OUTPUT_DIRECTORY)

    def _get_headers(self) -> Dict:
        """Get headers with random user agent for requests."""
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }

    def _make_request(self, url: str, params: Dict = None) -> Optional[str]:
        """
        Make an HTTP request with retry logic and random delays.
        
        Args:
            url (str): URL to request
            params (dict, optional): Query parameters
            
        Returns:
            str: HTML content if successful, None otherwise
        """
        # For development/testing, return mock data instead of making real requests
        if url.startswith(('https://www.indeed.com', 'https://www.linkedin.com')):
            return self._get_mock_data()
            
        for attempt in range(REQUEST_CONFIG['max_retries']):
            try:
                # Add random delay between requests
                time.sleep(random.uniform(1, REQUEST_CONFIG['retry_delay']))
                
                headers = {
                    'User-Agent': self.ua.random,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                    'Cache-Control': 'max-age=0',
                }
                
                response = self.session.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=REQUEST_CONFIG['timeout']
                )
                response.raise_for_status()
                return response.text
            except requests.exceptions.RequestException as e:
                log_error(logger, e, {'url': url, 'attempt': attempt + 1})
                if attempt == REQUEST_CONFIG['max_retries'] - 1:
                    return None
                time.sleep(REQUEST_CONFIG['retry_delay'] * (attempt + 1))
        return None

    def _get_mock_data(self) -> str:
        """
        Return mock job data for testing purposes.
        """
        mock_jobs = [
            {
                'title': 'Senior Program Manager',
                'company': 'Tech Innovations Inc.',
                'location': 'Los Angeles, CA',
                'description': 'Leading digital transformation initiatives and stakeholder engagement. Experience with Salesforce, project management, and business intelligence tools required.',
                'salary': '$120,000 - $160,000',
                'date_posted': '2024-03-12T10:00:00',
                'url': 'https://example.com/job1',
                'source': 'Indeed',
                'score': 0.92
            },
            {
                'title': 'Business Development Manager',
                'company': 'Global Solutions Corp',
                'location': 'Los Angeles, CA',
                'description': 'Drive strategic partnerships and revenue growth. Experience in CRM implementation, stakeholder management, and process automation.',
                'salary': '$100,000 - $140,000',
                'date_posted': '2024-03-11T15:30:00',
                'url': 'https://example.com/job2',
                'source': 'LinkedIn',
                'score': 0.88
            },
            {
                'title': 'Digital Transformation Lead',
                'company': 'Innovation Labs',
                'location': 'Los Angeles, CA',
                'description': 'Lead digital transformation initiatives. Skills in change management, process optimization, and technical implementation required.',
                'salary': '$130,000 - $180,000',
                'date_posted': '2024-03-13T09:15:00',
                'url': 'https://example.com/job3',
                'source': 'Indeed',
                'score': 0.85
            }
        ]
        
        # Save mock data to jobs.json
        os.makedirs('data', exist_ok=True)
        with open('data/jobs.json', 'w') as f:
            json.dump({
                'jobs': mock_jobs,
                'timestamp': datetime.now().isoformat(),
                'total_jobs': len(mock_jobs)
            }, f, indent=2)
        
        return json.dumps(mock_jobs)

    def _calculate_job_score(self, job: Dict) -> float:
        """
        Calculate a relevance score for a job based on various criteria.
        
        Args:
            job (dict): Job posting information
            
        Returns:
            float: Score between 0 and 1
        """
        score = 0
        criteria = {}

        # Title match
        title_matches = any(title.lower() in job['title'].lower() for title in SEARCH_TITLES)
        criteria['title_match'] = 1 if title_matches else 0
        score += criteria['title_match'] * SCORING_WEIGHTS['title_match']

        # Skills match
        required_skills_found = sum(1 for skill in REQUIRED_SKILLS 
                                  if skill.lower() in job['description'].lower())
        technical_skills_found = sum(1 for skill in TECHNICAL_SKILLS 
                                   if skill.lower() in job['description'].lower())
        
        skills_score = (required_skills_found / len(REQUIRED_SKILLS) * 0.7 + 
                       technical_skills_found / len(TECHNICAL_SKILLS) * 0.3)
        criteria['skills_match'] = skills_score
        score += skills_score * SCORING_WEIGHTS['skills_match']

        # Industry match
        industry_matches = any(industry.lower() in job['description'].lower() 
                             for industry in TARGET_INDUSTRIES)
        criteria['industry_match'] = 1 if industry_matches else 0
        score += criteria['industry_match'] * SCORING_WEIGHTS['industry_match']

        # Location match
        location_matches = (LOCATION['city'].lower() in job['location'].lower() and 
                          LOCATION['state'].lower() in job['location'].lower())
        criteria['location_match'] = 1 if location_matches else 0
        score += criteria['location_match'] * SCORING_WEIGHTS['location_match']

        # Log refinement result
        log_refinement_result(logger, job.get('id', 'unknown'), score, criteria)

        return score

    def _parse_indeed_job(self, job_element) -> Dict:
        """Parse job information from Indeed HTML element."""
        try:
            title = job_element.find('h2', {'class': 'jobTitle'}).get_text(strip=True)
            company = job_element.find('span', {'class': 'companyName'}).get_text(strip=True)
            location = job_element.find('div', {'class': 'companyLocation'}).get_text(strip=True)
            description = job_element.find('div', {'class': 'job-snippet'}).get_text(strip=True)
            
            job_info = {
                'title': title,
                'company': company,
                'location': location,
                'description': description,
                'source': 'Indeed',
                'date_found': datetime.now().isoformat(),
            }
            
            # Try to extract salary if available
            salary_elem = job_element.find('div', {'class': 'salary-snippet'})
            if salary_elem:
                job_info['salary'] = salary_elem.get_text(strip=True)
            
            return job_info
        except Exception as e:
            log_error(logger, e, {'element': str(job_element)})
            return None

    def _parse_linkedin_job(self, job_element) -> Dict:
        """Parse job information from LinkedIn HTML element."""
        try:
            title = job_element.find('h3', {'class': 'base-search-card__title'}).get_text(strip=True)
            company = job_element.find('h4', {'class': 'base-search-card__subtitle'}).get_text(strip=True)
            location = job_element.find('span', {'class': 'job-search-card__location'}).get_text(strip=True)
            
            job_info = {
                'title': title,
                'company': company,
                'location': location,
                'description': '',  # LinkedIn requires additional request for description
                'source': 'LinkedIn',
                'date_found': datetime.now().isoformat(),
            }
            
            return job_info
        except Exception as e:
            log_error(logger, e, {'element': str(job_element)})
            return None

    def scrape_jobs(self) -> List[Dict]:
        """
        Get jobs from mock data or scrape from job boards.
        
        Returns:
            list: List of job dictionaries with scores
        """
        try:
            # Get mock data
            mock_data = self._make_request(BASE_URLS['indeed'])
            if mock_data:
                try:
                    jobs_data = json.loads(mock_data)
                    self.jobs = jobs_data if isinstance(jobs_data, list) else []
                    
                    # Log found jobs
                    for job in self.jobs:
                        log_job_found(logger, job)
                    
                    log_scraping_progress(logger, "mock", 1, len(self.jobs))
                except json.JSONDecodeError as e:
                    log_error(logger, e, {'content': 'Error parsing mock data'})
                    self.jobs = []
        except Exception as e:
            log_error(logger, e, {'content': 'Error in scrape_jobs'})
            self.jobs = []
            
        # Sort jobs by score
        if self.jobs:
            self.jobs.sort(key=lambda x: x['score'], reverse=True)
            
        # Save results
        self._save_results()
        
        return self.jobs

    def _save_results(self):
        """Save scraped jobs to JSON file."""
        output_file = os.path.join(OUTPUT_DIRECTORY, 'jobs.json')
        try:
            with open(output_file, 'w') as f:
                json.dump({
                    'jobs': self.jobs,
                    'timestamp': datetime.now().isoformat(),
                    'total_jobs': len(self.jobs)
                }, f, indent=2)
            logger.info(f"Results saved to {output_file}")
        except Exception as e:
            log_error(logger, e, {'file': output_file})

    def get_top_jobs(self, limit: int = 10) -> List[Dict]:
        """
        Get top scoring jobs.
        
        Args:
            limit (int): Number of jobs to return
            
        Returns:
            list: Top scoring jobs
        """
        return sorted(self.jobs, key=lambda x: x['score'], reverse=True)[:limit]

if __name__ == '__main__':
    scraper = JobScraper()
    jobs = scraper.scrape_jobs()
    print(f"Found {len(jobs)} jobs")
    
    top_jobs = scraper.get_top_jobs(5)
    print("\nTop 5 matching jobs:")
    for job in top_jobs:
        print(f"\nTitle: {job['title']}")
        print(f"Company: {job['company']}")
        print(f"Location: {job['location']}")
        print(f"Score: {job['score']:.2f}")

"""
Logging configuration for the job scraper.
Sets up logging with both file and console handlers.
"""

import logging
import os
from datetime import datetime
from .config import LOG_CONFIG

def setup_logger(name='job_scraper'):
    """
    Configure and return a logger instance with both file and console handlers.
    
    Args:
        name (str): Name of the logger instance
        
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Prevent adding handlers multiple times
    if logger.handlers:
        return logger
        
    # Create logs directory if it doesn't exist
    logs_dir = 'logs'
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Create file handler with timestamp in filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_handler = logging.FileHandler(
        os.path.join(logs_dir, f'job_scraper_{timestamp}.log')
    )
    file_handler.setLevel(LOG_CONFIG['level'])
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOG_CONFIG['level'])
    
    # Create formatter
    formatter = logging.Formatter(LOG_CONFIG['format'])
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def log_error(logger, error, context=None):
    """
    Log an error with optional context information.
    
    Args:
        logger (logging.Logger): Logger instance
        error (Exception): The error to log
        context (dict, optional): Additional context information
    """
    error_msg = f"Error: {str(error)}"
    if context:
        error_msg += f"\nContext: {context}"
    logger.error(error_msg)

def log_job_found(logger, job_info):
    """
    Log information about a found job posting.
    
    Args:
        logger (logging.Logger): Logger instance
        job_info (dict): Information about the found job
    """
    logger.info(f"Found job: {job_info.get('title')} at {job_info.get('company')}")
    logger.debug(f"Job details: {job_info}")

def log_scraping_progress(logger, source, page, total_jobs):
    """
    Log progress of the scraping operation.
    
    Args:
        logger (logging.Logger): Logger instance
        source (str): Job board being scraped
        page (int): Current page number
        total_jobs (int): Total jobs found so far
    """
    logger.info(f"Scraping {source} - Page {page} - Total jobs found: {total_jobs}")

def log_refinement_result(logger, job_id, score, criteria):
    """
    Log the result of job refinement scoring.
    
    Args:
        logger (logging.Logger): Logger instance
        job_id (str): Identifier for the job
        score (float): Refinement score
        criteria (dict): Scoring criteria details
    """
    logger.debug(f"Job {job_id} refinement score: {score}")
    logger.debug(f"Scoring criteria: {criteria}")

# Create a default logger instance
logger = setup_logger()

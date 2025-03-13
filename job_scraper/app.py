"""
Flask web application for the job scraper.
Provides a modern UI for job searching and viewing results.
"""

from flask import Flask, render_template, request, jsonify, flash
from src.scraper import JobScraper
from src.logger import logger, log_error
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Initialize the job scraper
scraper = JobScraper()

@app.route('/')
def index():
    """Render the main page."""
    try:
        # Load existing jobs if available
        jobs_file = os.path.join('data', 'jobs.json')
        if os.path.exists(jobs_file):
            with open(jobs_file, 'r') as f:
                data = json.load(f)
                jobs = data.get('jobs', [])
                last_updated = datetime.fromisoformat(data.get('timestamp')).strftime('%Y-%m-%d %H:%M:%S')
        else:
            jobs = []
            last_updated = None
            
        return render_template(
            'index.html',
            jobs=jobs,
            last_updated=last_updated
        )
    except Exception as e:
        log_error(logger, e)
        flash('Error loading jobs. Please try again.', 'error')
        return render_template('index.html', jobs=[], last_updated=None)

@app.route('/search', methods=['POST'])
def search():
    """Handle job search requests."""
    try:
        # Get search parameters from form
        search_params = {
            'titles': request.form.getlist('titles[]'),
            'location': request.form.get('location'),
            'radius': request.form.get('radius', type=int),
            'min_salary': request.form.get('min_salary', type=int),
            'max_salary': request.form.get('max_salary', type=int)
        }
        
        # Update scraper configuration with new parameters
        # (You would need to add this functionality to the scraper)
        
        # Perform the search
        jobs = scraper.scrape_jobs()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Return JSON for AJAX requests
            return jsonify({
                'jobs': jobs,
                'timestamp': datetime.now().isoformat()
            })
        else:
            # Render template for regular requests
            flash(f'Found {len(jobs)} matching jobs!', 'success')
            return render_template(
                'index.html',
                jobs=jobs,
                last_updated=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
    except Exception as e:
        log_error(logger, e)
        error_message = 'Error performing job search. Please try again.'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': error_message}), 500
        else:
            flash(error_message, 'error')
            return render_template('index.html', jobs=[], last_updated=None)

@app.route('/jobs/top')
def top_jobs():
    """Get top matching jobs."""
    try:
        limit = request.args.get('limit', 10, type=int)
        top_jobs = scraper.get_top_jobs(limit)
        return jsonify({
            'jobs': top_jobs,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        log_error(logger, e)
        return jsonify({'error': 'Error fetching top jobs'}), 500

@app.route('/jobs/refresh')
def refresh_jobs():
    """Refresh job listings."""
    try:
        jobs = scraper.scrape_jobs()
        return jsonify({
            'jobs': jobs,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        log_error(logger, e)
        return jsonify({'error': 'Error refreshing jobs'}), 500

@app.template_filter('format_date')
def format_date(date_str):
    """Format ISO date string for display."""
    try:
        date = datetime.fromisoformat(date_str)
        return date.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return date_str

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)

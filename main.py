import argparse
import json
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import schedule
import time
from cookie_manager import PortSwiggerCookieManager

class PortSwiggerTracker:
    def __init__(self, progress_file='progress.json', output_file='README.md'):
        self.progress_file = progress_file
        self.output_file = output_file
        self.base_url = "https://portswigger.net/web-security"
        self.topics_url = f"{self.base_url}/all-topics"
        self.dashboard_url = f"{self.base_url}/dashboard"
        self.progress = self.load_progress()
        self.session = requests.Session()
        self.cookie_manager = PortSwiggerCookieManager()
        
    def init_session(self):
        """Initialize session with stored cookies or prompt for new ones"""
        cookies = self.cookie_manager.get_cookies()
        if not cookies:
            print("No stored cookies found.")
            print("Please run 'python cookie_manager.py store' to store your cookies first.")
            return False
            
        if not self.cookie_manager.validate_cookies(cookies):
            print("Stored cookies are invalid or expired.")
            print("Please run 'python cookie_manager.py store' to update your cookies.")
            return False
            
        self.session.cookies.update(cookies)
        return True
        
    def load_progress(self):
        """Load progress from JSON file or create if not exists"""
        if os.path.exists(self.progress_file):
            with open(self.progress_file, 'r') as f:
                return json.load(f)
        return {
            'topics': {},
            'level_progress': {
                'apprentice': {'completed': 0, 'total': 0},
                'practitioner': {'completed': 0, 'total': 0},
                'expert': {'completed': 0, 'total': 0}
            },
            'last_updated': None
        }

    def fetch_level_progress(self):
        """Fetch level progress from dashboard"""
        try:
            response = self.session.get(self.dashboard_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the level progress container
            progress_container = soup.find('div', class_='container-columns-3')
            if not progress_container:
                print("Warning: Could not find level progress - user might not be logged in")
                return None
                
            level_progress = {}
            
            # Parse progress for each level
            for level in ['apprentice', 'practitioner', 'expert']:
                level_div = progress_container.find('div', class_=f'{level}-progress')
                if level_div:
                    progress_div = level_div.find('div', class_='radial-text-element')
                    if progress_div:
                        completed = int(progress_div.find('div', class_='radial-text-element-progress').text)
                        total = int(progress_div.find('div', class_='radial-text-element-total').text.split('of')[-1])
                        level_progress[level] = {'completed': completed, 'total': total}
            
            return level_progress
            
        except requests.RequestException as e:
            print(f"Error fetching level progress: {e}")
            return None

    def fetch_all_labs(self):
        """Fetch the all-labs page content"""
        try:
            response = self.session.get(f"{self.base_url}/all-labs")
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching all labs: {e}")
            return None


    def get_topic_id(self, topic_title):
        """Map topic titles to their IDs on the all-labs page"""
        topic_map = {
            'SQL injection': 'sql-injection',
            'Authentication': 'authentication',
            'Path traversal': 'path-traversal',
            'Command injection': 'os-command-injection',
            'Business logic vulnerabilities': 'business-logic-vulnerabilities',  # Updated
            'Information disclosure': 'information-disclosure',
            'Access control': 'access-control-vulnerabilities',
            'File upload vulnerabilities': 'file-upload-vulnerabilities',  # Updated
            'Race conditions': 'race-conditions',
            'Server-side request forgery (SSRF)': 'server-side-request-forgery-ssrf',
            'XXE injection': 'xml-external-entity-xxe-injection',
            'NoSQL injection': 'nosql-injection',
            'API testing': 'api-testing',
            'Web cache deception': 'web-cache-deception',
            'Cross-site scripting (XSS)': 'cross-site-scripting',
            'Cross-site request forgery (CSRF)': 'cross-site-request-forgery-csrf',
            'Cross-origin resource sharing (CORS)': 'cross-origin-resource-sharing-cors',
            'Clickjacking': 'clickjacking',
            'DOM-based vulnerabilities': 'dom-based-vulnerabilities',
            'WebSockets': 'websockets',
            'Insecure deserialization': 'insecure-deserialization',
            'Web LLM attacks': 'web-llm-attacks',
            'GraphQL API vulnerabilities': 'graphql-api-vulnerabilities',
            'Server-side template injection': 'server-side-template-injection',
            'Web cache poisoning': 'web-cache-poisoning',
            'HTTP Host header attacks': 'http-host-header-attacks',
            'HTTP request smuggling': 'http-request-smuggling',
            'OAuth authentication': 'oauth-authentication',
            'JWT attacks': 'jwt',
            'Essential skills': 'essential-skills',
            'Prototype pollution': 'prototype-pollution'
        }
        topic_id = topic_map.get(topic_title)
        if not topic_id:
            print(f"DEBUG: No mapping found for topic '{topic_title}'")
        return topic_id

    def count_completed_labs(self, all_labs_soup, topic_title):
        """Count number of completed labs for a given topic"""
        # Get the correct ID for the topic
        topic_id = self.get_topic_id(topic_title)
        if not topic_id:
            print(f"Could not find mapping for topic: {topic_title}")
            return 0
        
        # Find the topic section
        topic_section = all_labs_soup.find('h2', {'id': topic_id})
        if not topic_section:
            print(f"Could not find section for {topic_title} (ID: {topic_id})")
            return 0
        
        # Count solved labs in this section
        completed = 0
        # Get all lab containers between this h2 and the next h2
        current = topic_section.find_next('div', class_='widgetcontainer-lab-link')
        next_section = topic_section.find_next('h2')
        
        while current and (not next_section or current.sourceline < next_section.sourceline):
            if 'is-solved' in current.get('class', []):
                completed += 1
            current = current.find_next('div', class_='widgetcontainer-lab-link')
        
        return completed
    
    def get_progress_emoji(self, completed, total):
        """Get emoji based on completion status"""
        if completed == 0:
            return "🔴"  # No progress
        elif completed == total:
            return "🟢"  # Fully completed
        else:
            return "🔵"  # Partial progress


    def process_section_topics(self, section, soup, all_labs_soup):
        """Process all topics in a section"""
        topics_data = []
        cards_container = section.find_next('div', class_='section-full-width')
        if cards_container:
            all_topics = cards_container.find_all('a')
            for topic in all_topics:
                title_elem = topic.find('h3')
                labs_elem = topic.find('sup')
                if title_elem and labs_elem:
                    title = title_elem.text.strip()
                    try:
                        current_labs = int(labs_elem.text.strip().split()[0])
                        completed = self.count_completed_labs(all_labs_soup, title)
                        
                        # Get progress emoji
                        status_emoji = self.get_progress_emoji(completed, current_labs)
                        
                        # Update progress data
                        self.progress['topics'][title] = {
                            'total_labs': current_labs,
                            'completed': completed,
                            'last_updated': datetime.now().isoformat()
                        }
                        
                        # Create table row (separate progress and status)
                        progress_str = f"{completed}/{current_labs}"
                        last_updated = datetime.fromisoformat(
                            self.progress['topics'][title]['last_updated']
                        ).strftime('%m/%d/%Y')
                        topics_data.append(f"| {title} | {current_labs} | {progress_str} | {status_emoji} | {last_updated} |\n")
                    except (ValueError, AttributeError) as e:
                        print(f"Error processing topic {title}: {e}")
        return topics_data

    def update_progress_table(self):
        """Update the progress table with both topic and level progress"""
        # Fetch required data
        html_content = self.fetch_topics()
        level_progress = self.fetch_level_progress()
        all_labs_html = self.fetch_all_labs()
        
        if not all_labs_html:
            print("Failed to fetch all-labs page")
            return
        
        soup = BeautifulSoup(html_content, 'html.parser')
        all_labs_soup = BeautifulSoup(all_labs_html, 'html.parser')
        
        if level_progress:
            self.progress['level_progress'] = level_progress
        
        # Generate table header with overall progress
        table = "![portswigger.jpg](https://i.imgur.com/kdZjayp.jpeg)\n\n"
        table += "# PortSwigger Academy Progress\n\n"
        
        # Add level progress section if available
        if level_progress:
            table += "## Overall Progress\n"
            for level, progress in level_progress.items():
                percentage = (progress['completed'] / progress['total'] * 100) if progress['total'] > 0 else 0
                table += f"- **{level.capitalize()}**: {progress['completed']}/{progress['total']} ({percentage:.1f}%)\n"
            table += "\n"
        
        # Add topics table with Status column
        table += "## Topic Progress\n"
        table += "| Topic 📖 | Labs 🔬 | Progress ✅ | Status ⭕️ | Last Updated 🗓️ |\n"
        table += "|---|---|---|:---:|---|\n"  # Center-align the Status column
        
        sections = [
            ('Server-side topics 🟧', '#server-side-topics'),
            ('Client-side topics 🟧', '#client-side-topics'),
            ('Advanced topics 🟧', '#advanced-topics')
        ]
        
        for section_name, section_id in sections:
            section = soup.find('h2', {'id': section_id[1:]})
            if section:
                table += f"| **{section_name}** | | | | |\n"
                topics_data = self.process_section_topics(section, soup, all_labs_soup)
                table += ''.join(topics_data)
        
        # Save updated progress and markdown table
        self.save_progress()
        with open(self.output_file, 'w') as f:
            f.write(table)
        
        return table

    def determine_lab_level(self, topic_url, lab_count):
        """Determine the difficulty level of labs for a topic"""
        # This is a simplified version - you might want to actually fetch and parse
        # the topic page to get accurate level information
        if not topic_url:
            return "Unknown"
        try:
            response = self.session.get(topic_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            # Add logic to parse lab levels from the topic page
            # This would depend on the HTML structure of the topic pages
            return "Mixed"  # Placeholder
        except:
            return "Unknown"

    def fetch_topics(self):
        """Fetch current topics and lab counts from PortSwigger"""
        try:
            response = self.session.get(self.topics_url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching topics: {e}")
            if os.path.exists('topics_backup.html'):
                with open('topics_backup.html', 'r') as f:
                    return f.read()
            raise

    def set_session_cookies(self, cookies):
        """Set session cookies for authenticated requests"""
        self.session.cookies.update(cookies)

    def save_progress(self):
        """Save progress to JSON file"""
        self.progress['last_updated'] = datetime.now().strftime("%x")
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, f, indent=2)

def schedule_updates():
    """Schedule weekly updates"""
    tracker = PortSwiggerTracker()
    if not tracker.init_session():
        print("Could not initialize session for scheduled updates.")
        return
    
    def job():
        print(f"Running scheduled update at {datetime.now()}")
        # Re-initialize session before each update in case cookies expire
        if tracker.init_session():
            tracker.update_progress_table()
        else:
            print("Failed to update progress: invalid session")
    
    schedule.every().monday.at("09:00").do(job)
    
    while True:
        schedule.run_pending()
        time.sleep(3600)

def main():
    parser = argparse.ArgumentParser(description='Web Security Progress Tracker')
    parser.add_argument('--update', action='store_true', help='Update progress table')
    parser.add_argument('--schedule', action='store_true', help='Start scheduled updates')
    
    args = parser.parse_args()
    tracker = PortSwiggerTracker()
    
    # Initialize session with cookies
    if not tracker.init_session():
        exit(1)
    
    if args.update:
        tracker.update_progress_table()
    elif args.schedule:
        schedule_updates()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

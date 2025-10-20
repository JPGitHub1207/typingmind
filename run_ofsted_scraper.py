#!/usr/bin/env python3
"""
Simple runner script for Ofsted scraper
Handles setup and execution with error handling
"""

import sys
import os
import subprocess
import importlib.util

def check_and_install_requirements():
    """Check if required packages are installed and install if needed"""
    required_packages = [
        'requests',
        'beautifulsoup4', 
        'lxml'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'beautifulsoup4':
                import bs4
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing required packages: {', '.join(missing_packages)}")
        print("Installing missing packages...")
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install"
            ] + missing_packages)
            print("Successfully installed missing packages!")
        except subprocess.CalledProcessError as e:
            print(f"Error installing packages: {e}")
            print("Please install manually using: pip install -r requirements.txt")
            return False
    
    return True

def main():
    """Main runner function"""
    print("=== Ofsted Website Scraper Runner ===")
    print()
    
    # Check and install requirements
    if not check_and_install_requirements():
        print("Failed to install required packages. Exiting.")
        sys.exit(1)
    
    # Check which scraper to use
    enhanced_scraper_exists = os.path.exists('ofsted_enhanced_scraper.py')
    basic_scraper_exists = os.path.exists('ofsted_scraper.py')
    
    if enhanced_scraper_exists:
        print("Using enhanced scraper with BeautifulSoup...")
        try:
            from ofsted_enhanced_scraper import main as run_enhanced_scraper
            run_enhanced_scraper()
        except Exception as e:
            print(f"Error running enhanced scraper: {e}")
            if basic_scraper_exists:
                print("Falling back to basic scraper...")
                from ofsted_scraper import main as run_basic_scraper
                run_basic_scraper()
            else:
                print("No working scraper found!")
                sys.exit(1)
    
    elif basic_scraper_exists:
        print("Using basic scraper...")
        try:
            from ofsted_scraper import main as run_basic_scraper
            run_basic_scraper()
        except Exception as e:
            print(f"Error running basic scraper: {e}")
            sys.exit(1)
    
    else:
        print("No scraper scripts found!")
        print("Please ensure ofsted_scraper.py or ofsted_enhanced_scraper.py exists.")
        sys.exit(1)

if __name__ == "__main__":
    main()
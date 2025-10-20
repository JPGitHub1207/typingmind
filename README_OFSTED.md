# Ofsted Website Scraper

This tool automates the collection of Ofsted inspection data for educational providers and companies.

## Features

- **Automated Search**: Searches Ofsted website for providers by company name
- **Detailed Data Extraction**: Collects inspection ratings, contact info, and compliance data
- **Multiple Output Formats**: Saves results in both CSV and JSON formats
- **Error Handling**: Robust error handling with detailed logging
- **Rate Limiting**: Respectful scraping with configurable delays
- **Duplicate Prevention**: Avoids processing the same provider multiple times

## Files Included

- `ofsted_scraper.py` - Basic scraper with regex-based parsing
- `ofsted_enhanced_scraper.py` - Advanced scraper with BeautifulSoup HTML parsing
- `run_ofsted_scraper.py` - Simple runner script with automatic dependency installation
- `companies.txt` - List of companies to process (one per line)
- `requirements.txt` - Python dependencies

## Quick Start

### Option 1: Use the Runner Script (Recommended)
```bash
python run_ofsted_scraper.py
```

The runner script will automatically:
- Check for required dependencies
- Install missing packages if needed
- Run the appropriate scraper
- Handle errors gracefully

### Option 2: Manual Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run the enhanced scraper
python ofsted_enhanced_scraper.py

# Or run the basic scraper
python ofsted_scraper.py
```

## Configuration

### Company List
Edit `companies.txt` to specify which companies to process:
```
# One company name per line
# Lines starting with # are ignored

ABC Learning Centre
XYZ Training Academy
Education Plus Ltd
```

### Scraper Settings
You can modify the scraper behavior by editing the Python files:

- **Delay between requests**: Change the `delay` parameter (default: 2 seconds)
- **Search parameters**: Modify search filters and criteria
- **Output format**: Customize CSV/JSON field selection

## Output Files

The scraper generates timestamped output files:

- `ofsted_enhanced_results_YYYYMMDD_HHMMSS.csv` - CSV format results
- `ofsted_enhanced_results_YYYYMMDD_HHMMSS.json` - JSON format results
- `ofsted_enhanced_scraper.log` - Detailed execution log

## Data Collected

For each provider found, the scraper attempts to collect:

### Basic Information
- Provider name and URN (Unique Reference Number)
- Provider type (school, nursery, training provider, etc.)
- Status (active, closed, etc.)
- Registration date
- Age range served

### Contact Details
- Full address
- Phone number
- Website URL
- Email address

### Inspection Data
- Last inspection date
- Report published date
- Next inspection due date
- Overall effectiveness rating
- Quality of education rating
- Behaviour and attitudes rating
- Personal development rating
- Leadership and management rating
- Safeguarding effectiveness

## Usage Examples

### Processing Specific Companies
```python
from ofsted_enhanced_scraper import EnhancedOfstedScraper

scraper = EnhancedOfstedScraper(delay=1.5)
companies = ["My Training Company", "ABC Learning Centre"]
results = scraper.process_companies(companies)
scraper.save_results_csv("my_results.csv")
```

### Searching with Filters
```python
# Search for specific provider types
providers = scraper.search_providers(
    "Learning Centre", 
    location="London",
    provider_types=["childcare", "school"]
)
```

## Error Handling

The scraper includes comprehensive error handling:

- **Network errors**: Retries and graceful degradation
- **Parsing errors**: Continues processing other providers
- **Rate limiting**: Respects website rate limits
- **Logging**: Detailed logs for debugging

## Compliance Notes

This tool is designed for legitimate research and compliance purposes:

- Respects robots.txt guidelines
- Implements reasonable rate limiting
- Only accesses publicly available data
- Includes proper error handling to avoid overloading servers

## Troubleshooting

### Common Issues

1. **"No providers found"**
   - Check company names in companies.txt for typos
   - Try variations of company names
   - Some providers may not be registered with Ofsted

2. **"Network timeout errors"**
   - Increase the delay between requests
   - Check internet connection
   - Ofsted website may be temporarily unavailable

3. **"Missing dependencies"**
   - Run: `pip install -r requirements.txt`
   - Use the runner script for automatic installation

4. **"Empty results"**
   - Check the log file for detailed error messages
   - Verify company names exist on Ofsted website
   - Try the basic scraper if enhanced version fails

### Getting Help

Check the log files for detailed error messages:
- `ofsted_enhanced_scraper.log` - Enhanced scraper log
- `ofsted_scraper.log` - Basic scraper log

## Legal Disclaimer

This tool is for educational and research purposes. Users are responsible for:
- Complying with Ofsted website terms of use
- Respecting rate limits and not overloading servers
- Using collected data responsibly and in accordance with data protection laws
- Ensuring they have the right to collect and use the data

## Updates and Maintenance

The Ofsted website structure may change over time. If the scraper stops working:
1. Check the log files for specific errors
2. Update the CSS selectors in the parsing functions
3. Verify the search URL and parameters are still correct
4. Consider using the basic scraper as a fallback
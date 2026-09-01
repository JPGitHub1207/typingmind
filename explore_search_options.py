#!/usr/bin/env python3
"""
Explore different search options on Ofsted website to find more providers
"""

import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

class OfstedSearchExplorer:
    def __init__(self):
        self.base_url = "https://reports.ofsted.gov.uk"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def explore_search_variations(self):
        """Try different search parameters to find more providers"""
        
        search_variations = [
            # Original search
            "https://reports.ofsted.gov.uk/search?q=&location=&lat=&lon=&radius=&level_1_types=1&level_2_types%5B%5D=3",
            
            # Try different level_2_types
            "https://reports.ofsted.gov.uk/search?q=&location=&lat=&lon=&radius=&level_1_types=1&level_2_types%5B%5D=1",
            "https://reports.ofsted.gov.uk/search?q=&location=&lat=&lon=&radius=&level_1_types=1&level_2_types%5B%5D=2",
            "https://reports.ofsted.gov.uk/search?q=&location=&lat=&lon=&radius=&level_1_types=1&level_2_types%5B%5D=4",
            "https://reports.ofsted.gov.uk/search?q=&location=&lat=&lon=&radius=&level_1_types=1&level_2_types%5B%5D=5",
            
            # Try all level_1_types=1 without level_2_types filter
            "https://reports.ofsted.gov.uk/search?q=&location=&lat=&lon=&radius=&level_1_types=1",
            
            # Try searching for "training" in the query
            "https://reports.ofsted.gov.uk/search?q=training&location=&lat=&lon=&radius=&level_1_types=1",
            
            # Try searching for "apprenticeship"
            "https://reports.ofsted.gov.uk/search?q=apprenticeship&location=&lat=&lon=&radius=&level_1_types=1",
            
            # Try different level_1_types
            "https://reports.ofsted.gov.uk/search?q=&location=&lat=&lon=&radius=&level_1_types=2",
            "https://reports.ofsted.gov.uk/search?q=&location=&lat=&lon=&radius=&level_1_types=3",
            
            # Try no filters at all with training keywords
            "https://reports.ofsted.gov.uk/search?q=training+provider",
            "https://reports.ofsted.gov.uk/search?q=independent+learning+provider",
        ]
        
        results = {}
        
        for i, url in enumerate(search_variations):
            print(f"\n{i+1}. Testing search variation:")
            print(f"   URL: {url}")
            
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Count provider links
                provider_links = []
                all_links = soup.find_all('a', href=True)
                for link in all_links:
                    href = link['href']
                    if '/provider/' in href:
                        full_url = urljoin(self.base_url, href)
                        if full_url not in provider_links:
                            provider_links.append(full_url)
                
                # Look for result count indicators
                result_text = soup.get_text()
                
                # Look for pagination
                page_links = soup.find_all('a', href=re.compile(r'page=\d+'))
                max_page = 1
                for link in page_links:
                    href = link.get('href', '')
                    page_match = re.search(r'page=(\d+)', href)
                    if page_match:
                        page_num = int(page_match.group(1))
                        max_page = max(max_page, page_num)
                
                # Look for "showing X of Y results" type text
                result_count_patterns = [
                    r'(\d+)\s+results?',
                    r'showing\s+\d+\s+of\s+(\d+)',
                    r'(\d+)\s+providers?\s+found',
                ]
                
                total_results = None
                for pattern in result_count_patterns:
                    match = re.search(pattern, result_text, re.IGNORECASE)
                    if match:
                        total_results = int(match.group(1))
                        break
                
                results[url] = {
                    'providers_on_page': len(provider_links),
                    'max_page_found': max_page,
                    'estimated_total': total_results,
                    'provider_links': provider_links[:5]  # Store first 5 for inspection
                }
                
                print(f"   Providers found on page 1: {len(provider_links)}")
                print(f"   Max page number found: {max_page}")
                if total_results:
                    print(f"   Estimated total results: {total_results}")
                
                if provider_links:
                    print(f"   Sample provider URLs:")
                    for j, link in enumerate(provider_links[:3]):
                        print(f"     {j+1}. {link}")
                
            except Exception as e:
                print(f"   Error: {e}")
                results[url] = {'error': str(e)}
        
        return results
    
    def analyze_results(self, results):
        """Analyze the search results to find the best approach"""
        print(f"\n" + "="*80)
        print("SEARCH ANALYSIS SUMMARY")
        print("="*80)
        
        best_searches = []
        
        for url, data in results.items():
            if 'error' in data:
                continue
            
            providers = data.get('providers_on_page', 0)
            max_page = data.get('max_page_found', 1)
            estimated_total = data.get('estimated_total')
            
            estimated_providers = providers * max_page if max_page > 1 else providers
            
            if providers > 0:
                best_searches.append({
                    'url': url,
                    'providers_per_page': providers,
                    'max_pages': max_page,
                    'estimated_total': estimated_total or estimated_providers,
                    'sample_links': data.get('provider_links', [])
                })
        
        # Sort by estimated total
        best_searches.sort(key=lambda x: x['estimated_total'], reverse=True)
        
        print(f"\nBest search options (by estimated total providers):")
        for i, search in enumerate(best_searches[:5]):
            print(f"\n{i+1}. {search['estimated_total']} estimated providers")
            print(f"   URL: {search['url']}")
            print(f"   Providers per page: {search['providers_per_page']}")
            print(f"   Max pages: {search['max_pages']}")
        
        return best_searches

def main():
    explorer = OfstedSearchExplorer()
    
    print("Exploring different search options on Ofsted website...")
    results = explorer.explore_search_variations()
    
    best_options = explorer.analyze_results(results)
    
    if best_options:
        print(f"\nRecommendation: Use the search with {best_options[0]['estimated_total']} providers")
        print(f"URL: {best_options[0]['url']}")
    else:
        print("\nNo viable search options found with more providers")

if __name__ == "__main__":
    main()
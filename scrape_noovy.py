#!/usr/bin/env python3
"""
Scraper for Noovy Knowledge Base
Extracts articles and content for the hotel AI support system
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urljoin

def scrape_noovy_knowledge_base():
    """Scrape the Noovy knowledge base and extract Q&A content"""
    
    base_url = "https://help.noovy.com"
    knowledge_url = f"{base_url}/knowledge"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    knowledge_data = []
    
    # Main categories from the knowledge base
    categories = {
        "Bookings & Rooms": "bookings-rooms",
        "Rates & Distribution": "rates-distribution", 
        "Finance & Payments": "finance-payments",
        "Profiles & Tasks": "profiles-tasks",
        "Hardware": "hardware",
        "Getting Started": "getting-started"
    }
    
    print("🔍 Starting Noovy Knowledge Base scraping...")
    
    for category_name, category_slug in categories.items():
        category_url = f"{base_url}/knowledge/{category_slug}"
        print(f"\n📂 Category: {category_name}")
        print(f"   URL: {category_url}")
        
        try:
            response = requests.get(category_url, headers=headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try to find article links
            articles = soup.find_all('a', href=lambda x: x and '/knowledge/' in x and category_slug in x)
            
            print(f"   Found {len(articles)} potential articles")
            
            for article_link in articles[:5]:  # Limit to first 5 per category
                article_url = urljoin(base_url, article_link.get('href', ''))
                article_title = article_link.get_text(strip=True)
                
                if not article_title or len(article_title) < 10:
                    continue
                    
                print(f"   📄 {article_title[:60]}...")
                
                try:
                    article_response = requests.get(article_url, headers=headers, timeout=15)
                    article_soup = BeautifulSoup(article_response.text, 'html.parser')
                    
                    # Extract content
                    content = ""
                    article_body = article_soup.find('article') or article_soup.find('main')
                    if article_body:
                        # Get all paragraphs
                        paragraphs = article_body.find_all(['p', 'li', 'h2', 'h3'])
                        content = '\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
                    
                    if content:
                        knowledge_data.append({
                            'category': category_name,
                            'title': article_title,
                            'content': content[:1500],  # Limit content size
                            'url': article_url,
                            'source': 'Noovy Knowledge Base'
                        })
                    
                    time.sleep(1)  # Be respectful with requests
                    
                except Exception as e:
                    print(f"      ⚠️ Error fetching article: {e}")
                    continue
                    
        except Exception as e:
            print(f"   ❌ Error fetching category: {e}")
            continue
    
    print(f"\n✅ Scraping complete! Collected {len(knowledge_data)} articles")
    return knowledge_data


if __name__ == "__main__":
    # Scrape the knowledge base
    data = scrape_noovy_knowledge_base()
    
    # Save to JSON file
    output_file = 'backend/data/noovy_knowledge.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Data saved to: {output_file}")
    print(f"   Total entries: {len(data)}")
    
    # Print sample
    if data:
        print(f"\n📋 Sample entry:")
        print(json.dumps(data[0], ensure_ascii=False, indent=2))

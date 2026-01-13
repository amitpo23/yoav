"""
URL Knowledge Scraper - גריפת אתרים והוספה למאגר הידע
"""

import os
import re
import hashlib
import asyncio
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from urllib.parse import urlparse, urljoin
import httpx


@dataclass
class ScrapedPage:
    """דף שנסרק"""
    url: str
    title: str
    content: str
    links: List[str]
    scraped_at: str
    content_hash: str
    word_count: int
    language: str


class URLKnowledgeScraper:
    """
    שירות לגריפת אתרים והוספה למאגר הידע
    תומך ב:
    - גריפת דף בודד
    - גריפת אתר מלא (crawling)
    - עדכון אוטומטי
    - זיהוי שפה
    """
    
    def __init__(self, knowledge_service=None):
        self.knowledge_service = knowledge_service
        self.scraped_urls: Dict[str, ScrapedPage] = {}
        self.url_queue: List[str] = []
        self.visited_urls: set = set()
        self.storage_path = "./data/scraped"
        os.makedirs(self.storage_path, exist_ok=True)
        
        # Load existing scraped data
        self._load_scraped_data()
    
    def _load_scraped_data(self):
        """טעינת נתוני גריפה קיימים"""
        import json
        try:
            data_file = os.path.join(self.storage_path, "scraped_urls.json")
            if os.path.exists(data_file):
                with open(data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for url, page_data in data.items():
                        self.scraped_urls[url] = ScrapedPage(**page_data)
        except Exception as e:
            print(f"Error loading scraped data: {e}")
    
    def _save_scraped_data(self):
        """שמירת נתוני גריפה"""
        import json
        try:
            data_file = os.path.join(self.storage_path, "scraped_urls.json")
            data = {}
            for url, page in self.scraped_urls.items():
                data[url] = {
                    "url": page.url,
                    "title": page.title,
                    "content": page.content[:10000],  # Limit content size
                    "links": page.links[:50],  # Limit links
                    "scraped_at": page.scraped_at,
                    "content_hash": page.content_hash,
                    "word_count": page.word_count,
                    "language": page.language
                }
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving scraped data: {e}")
    
    def _extract_text_from_html(self, html: str) -> str:
        """חילוץ טקסט מ-HTML"""
        # Remove script and style elements
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<head[^>]*>.*?</head>', '', html, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove HTML comments
        html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', html)
        
        # Decode HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
    
    def _extract_title(self, html: str) -> str:
        """חילוץ כותרת מ-HTML"""
        match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # Try h1
        match = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.IGNORECASE | re.DOTALL)
        if match:
            return re.sub(r'<[^>]+>', '', match.group(1)).strip()
        
        return "ללא כותרת"
    
    def _extract_links(self, html: str, base_url: str) -> List[str]:
        """חילוץ קישורים מ-HTML"""
        links = []
        pattern = r'<a[^>]+href=["\']([^"\']+)["\']'
        
        for match in re.finditer(pattern, html, re.IGNORECASE):
            href = match.group(1)
            
            # Skip anchors, javascript, mailto
            if href.startswith('#') or href.startswith('javascript:') or href.startswith('mailto:'):
                continue
            
            # Convert relative URLs to absolute
            full_url = urljoin(base_url, href)
            
            # Only include same domain
            base_domain = urlparse(base_url).netloc
            link_domain = urlparse(full_url).netloc
            
            if link_domain == base_domain:
                links.append(full_url)
        
        return list(set(links))
    
    def _detect_language(self, text: str) -> str:
        """זיהוי שפה פשוט"""
        hebrew_chars = len(re.findall(r'[\u0590-\u05FF]', text))
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        
        if hebrew_chars > english_chars:
            return "he"
        return "en"
    
    def _calculate_hash(self, content: str) -> str:
        """חישוב hash של תוכן"""
        return hashlib.md5(content.encode()).hexdigest()
    
    async def scrape_url(
        self,
        url: str,
        add_to_knowledge: bool = True,
        category: str = "scraped"
    ) -> Optional[ScrapedPage]:
        """
        גריפת URL בודד
        """
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(url, headers={
                    "User-Agent": "Mozilla/5.0 (compatible; HotelAIBot/1.0)"
                })
                response.raise_for_status()
                
                html = response.text
                
                # Extract content
                title = self._extract_title(html)
                content = self._extract_text_from_html(html)
                links = self._extract_links(html, url)
                language = self._detect_language(content)
                content_hash = self._calculate_hash(content)
                
                # Check if content changed
                if url in self.scraped_urls:
                    if self.scraped_urls[url].content_hash == content_hash:
                        return self.scraped_urls[url]  # No change
                
                page = ScrapedPage(
                    url=url,
                    title=title,
                    content=content,
                    links=links,
                    scraped_at=datetime.now().isoformat(),
                    content_hash=content_hash,
                    word_count=len(content.split()),
                    language=language
                )
                
                self.scraped_urls[url] = page
                self.visited_urls.add(url)
                self._save_scraped_data()
                
                # Add to knowledge base
                if add_to_knowledge and self.knowledge_service:
                    await self._add_to_knowledge_base(page, category)
                
                return page
                
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None
    
    async def crawl_website(
        self,
        start_url: str,
        max_pages: int = 20,
        category: str = "scraped",
        depth: int = 2
    ) -> List[ScrapedPage]:
        """
        סריקת אתר מלא
        """
        pages = []
        self.url_queue = [start_url]
        self.visited_urls = set()
        current_depth = 0
        
        while self.url_queue and len(pages) < max_pages and current_depth < depth:
            current_batch = self.url_queue[:10]
            self.url_queue = self.url_queue[10:]
            
            for url in current_batch:
                if url in self.visited_urls:
                    continue
                
                page = await self.scrape_url(url, add_to_knowledge=True, category=category)
                
                if page:
                    pages.append(page)
                    
                    # Add new links to queue
                    for link in page.links:
                        if link not in self.visited_urls and link not in self.url_queue:
                            self.url_queue.append(link)
                
                # Small delay to be polite
                await asyncio.sleep(0.5)
            
            current_depth += 1
        
        return pages
    
    async def _add_to_knowledge_base(self, page: ScrapedPage, category: str):
        """הוספת דף למאגר הידע"""
        if not self.knowledge_service:
            return
        
        # Split content into chunks if too long
        content = page.content
        max_chunk_size = 2000
        
        if len(content) > max_chunk_size:
            chunks = self._split_into_chunks(content, max_chunk_size)
            for i, chunk in enumerate(chunks):
                await self.knowledge_service.add_item(
                    title=f"{page.title} (חלק {i+1})",
                    content=chunk,
                    category=category,
                    tags=["scraped", page.language, urlparse(page.url).netloc]
                )
        else:
            await self.knowledge_service.add_item(
                title=page.title,
                content=content,
                category=category,
                tags=["scraped", page.language, urlparse(page.url).netloc]
            )
    
    def _split_into_chunks(self, text: str, chunk_size: int) -> List[str]:
        """חלוקת טקסט לחתיכות"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_size = 0
        
        for word in words:
            if current_size + len(word) > chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                current_size = 0
            
            current_chunk.append(word)
            current_size += len(word) + 1
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    async def refresh_url(self, url: str) -> Optional[ScrapedPage]:
        """רענון URL קיים"""
        return await self.scrape_url(url, add_to_knowledge=True)
    
    async def refresh_all(self) -> Dict[str, Any]:
        """רענון כל ה-URLs"""
        results = {
            "updated": 0,
            "failed": 0,
            "unchanged": 0
        }
        
        for url in list(self.scraped_urls.keys()):
            old_hash = self.scraped_urls[url].content_hash
            page = await self.scrape_url(url, add_to_knowledge=False)
            
            if page:
                if page.content_hash != old_hash:
                    results["updated"] += 1
                    # Update in knowledge base
                    if self.knowledge_service:
                        await self._add_to_knowledge_base(page, "scraped")
                else:
                    results["unchanged"] += 1
            else:
                results["failed"] += 1
            
            await asyncio.sleep(0.5)
        
        return results
    
    def get_scraped_urls(self) -> List[Dict[str, Any]]:
        """קבלת רשימת URLs שנסרקו"""
        return [
            {
                "url": page.url,
                "title": page.title,
                "word_count": page.word_count,
                "language": page.language,
                "scraped_at": page.scraped_at
            }
            for page in self.scraped_urls.values()
        ]
    
    def delete_url(self, url: str) -> bool:
        """מחיקת URL מהזיכרון"""
        if url in self.scraped_urls:
            del self.scraped_urls[url]
            self._save_scraped_data()
            return True
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """קבלת סטטיסטיקות"""
        total_words = sum(p.word_count for p in self.scraped_urls.values())
        languages = {}
        for page in self.scraped_urls.values():
            languages[page.language] = languages.get(page.language, 0) + 1
        
        return {
            "total_urls": len(self.scraped_urls),
            "total_words": total_words,
            "languages": languages,
            "average_words_per_page": total_words // max(len(self.scraped_urls), 1)
        }


# Singleton instance
url_scraper = URLKnowledgeScraper()

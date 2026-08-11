from typing import List, Dict, Any
import fitz
import re
from urllib.parse import urlparse, urlunparse
import os
from pdf2image import convert_from_path
import pytesseract

class Extractor:
    def __init__(self, use_ocr_fallback: bool = True):
        self.use_ocr_fallback = use_ocr_fallback

    def extract_urls(self, pdf_path: str) -> Dict[str, Any]:
        """Main pipeline to extract structured URLs from a PDF."""
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
        doc = fitz.open(pdf_path)
        all_urls = set()
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            page_urls = set()
            
            # 1. Embedded hyperlink extraction
            page_urls.update(self._extract_embedded_links(page))
            
            # 2. Text URL extraction
            page_text = self.extract_all_text(page)
            page_urls.update(self.extract_hyperlinks(page_text))
                
            # 3. OCR fallback if necessary
            if not page_urls and self.use_ocr_fallback:
                page_urls.update(self._extract_via_ocr(pdf_path, page_num))
            
            all_urls.update(page_urls)
            
        doc.close()
        
        # 4. Normalize
        normalized_urls = {self._normalize_url(url) for url in all_urls if url}
        
        # 5. Deduplicate (Already handled by set, but we format it as a list)
        unique_urls = list(normalized_urls)
        
        # 6. Classify
        classified = self._classify_urls(unique_urls)
        
        # 7. Return structured URLs
        return {
            'total_unique_urls': len(unique_urls),
            'classified_urls': classified,
            'urls_list': unique_urls
        }

    def _extract_embedded_links(self, page: fitz.Page) -> List[str]:
        """Extract embedded hyperlinks from a PDF page."""
        links = []
        for link in page.get_links():
            if link.get('kind') == fitz.LINK_URI:
                uri = link.get('uri')
                if uri:
                    links.append(uri)
        return links

    def extract_hyperlinks(self, text: str) -> List[str]:
        """Extract URLs typed as plain text using regex."""
        url_pattern = re.compile(
            r'(?:https?://)?'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)', re.IGNORECASE)
        return url_pattern.findall(text)

    def extract_all_text(self, page: fitz.Page) -> str:
        """Extract all raw text from a PDF page."""
        return page.get_text()

    def _extract_via_ocr(self, pdf_path: str, page_num: int) -> List[str]:
        """Convert a page to image and run OCR to extract URLs."""
        urls = []
        try:
            images = convert_from_path(pdf_path, first_page=page_num+1, last_page=page_num+1)
            for img in images:
                ocr_text = pytesseract.image_to_string(img)
                urls.extend(self.extract_hyperlinks(ocr_text))
        except Exception as e:
            print(f"OCR failed on page {page_num}: {e}")
        return urls

    def _normalize_url(self, url: str) -> str:
        """Normalize URL: add scheme, strip trailing slashes and fragments."""
        url = url.strip()
        if not url.startswith('http://') and not url.startswith('https://'):
            url = 'https://' + url
        try:
            parsed = urlparse(url)
            path = parsed.path.rstrip('/')
            return urlunparse((parsed.scheme, parsed.netloc, path, parsed.params, parsed.query, ''))
        except Exception:
            return url

    def _classify_urls(self, urls: List[str]) -> Dict[str, List[str]]:
        """Classify URLs into basic categories."""
        classified = {
            'social_media': [],
            'documents': [],
            'general': []
        }
        for url in urls:
            lower_url = url.lower()
            if any(domain in lower_url for domain in ['twitter.com', 'linkedin.com', 'facebook.com', 'github.com']):
                classified['social_media'].append(url)
            elif any(ext in lower_url for ext in ['.pdf', '.doc', '.docx']):
                classified['documents'].append(url)
            else:
                classified['general'].append(url)
        return classified
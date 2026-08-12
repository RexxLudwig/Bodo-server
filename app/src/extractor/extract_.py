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
        """Main pipeline to extract structured URLs and their text from a PDF."""
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
        doc = fitz.open(pdf_path)
        all_urls_map = {}
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            page_items = []
            
            # 1. Embedded hyperlink extraction
            page_items.extend(self._extract_embedded_links(page))
            
            # 2. Text URL extraction
            page_text = self.extract_all_text(page)
            page_items.extend(self.extract_hyperlinks(page_text))
                
            # 3. OCR fallback if necessary (if very little text was extracted, it's likely an image/scan)
            if len(page_text.strip()) < 50 and self.use_ocr_fallback:
                page_items.extend(self._extract_via_ocr(pdf_path, page_num))
            
            for item in page_items:
                url = item['url']
                text = item['text']
                # Keep the longest extracted text for a given URL
                if url not in all_urls_map or len(text) > len(all_urls_map.get(url, "")):
                    all_urls_map[url] = text
            
        doc.close()
        
        # 4. Normalize
        normalized_urls = {}
        for url, text in all_urls_map.items():
            if not url: continue
            norm = self._normalize_url(url)
            if norm not in normalized_urls or len(text) > len(normalized_urls.get(norm, "")):
                normalized_urls[norm] = text
        
        # 5. Format as list of dictionaries
        unique_urls = [{'url': k, 'text': v} for k, v in normalized_urls.items()]
        
        # 6. Classify
        classified = self._classify_urls(unique_urls)
        
        # 7. Return structured URLs
        return {
            'total_unique_urls': len(unique_urls),
            'classified_urls': classified,
            'urls_list': unique_urls
        }

    def _extract_embedded_links(self, page: fitz.Page) -> List[Dict[str, str]]:
        """Extract embedded hyperlinks and their text from a PDF page."""
        links = []
        for link in page.get_links():
            if link.get('kind') == fitz.LINK_URI:
                uri = link.get('uri')
                if uri:
                    rect = link.get('from')
                    link_text = page.get_textbox(rect).replace('\n', ' ').strip() if rect else uri
                    if not link_text:
                        link_text = uri
                    links.append({"url": uri, "text": link_text})
        return links

    def extract_hyperlinks(self, text: str) -> List[Dict[str, str]]:
        """Extract URLs typed as plain text using regex."""
        # A more robust regex that catches URLs with or without http://, including paths
        url_pattern = re.compile(
            r'(?:https?://)?(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)', 
            re.IGNORECASE)
        return [{"url": match, "text": match} for match in url_pattern.findall(text)]

    def extract_all_text(self, page: fitz.Page) -> str:
        """Extract all raw text from a PDF page."""
        return page.get_text()

    def _extract_via_ocr(self, pdf_path: str, page_num: int) -> List[Dict[str, str]]:
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

    def _classify_urls(self, urls: List[Dict[str, str]]) -> Dict[str, List[Dict[str, str]]]:
        """Classify URLs into basic categories."""
        classified = {
            'github': [],
            'portfolio': [],
            'social_media': [],
            'documents': [],
            'general': []
        }
        for item in urls:
            lower_url = item['url'].lower()
            if 'github.com' in lower_url:
                classified['github'].append(item)
            elif any(domain in lower_url for domain in ['quora.com', 'linkedin.com', 'leetcode.com', 'twitter.com']):
                classified['social_media'].append(item)
            elif 'portfolio' in lower_url:
                classified['portfolio'].append(item)
            elif any(ext in lower_url for ext in ['.pdf', '.doc', '.docx']):
                classified['documents'].append(item)
            else:
                classified['general'].append(item)
        return classified
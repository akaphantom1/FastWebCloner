"""
Motor de crawling pentru scanarea domeniilor web
"""

import re
import time
import logging
from collections import deque
from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup

from config import DEFAULT_USER_AGENT, DEFAULT_TIMEOUT, EXCLUDED_EXTENSIONS
import config

logger = logging.getLogger(__name__)


class DomainCrawler:
    """
    Clasa avansata pentru crawling de domenii web
    """
    
    def __init__(self, base_url, max_depth=3, max_pages=1000, 
                 same_domain_only=True, include_subdomains=False, 
                 exclude_patterns=None):
        """
        Initializeaza crawler-ul
        
        Args:
            base_url: URL-ul de pornire
            max_depth: Adancimea maxima de scanare
            max_pages: Numarul maxim de pagini de scanat
            same_domain_only: Daca sa scaneze doar acelasi domeniu
            include_subdomains: Daca sa includa subdomenii
            exclude_patterns: Liste de pattern-uri de exclus
        """
        self.base_url = self._normalize_url(base_url)
        self.base_domain = urlparse(self.base_url).netloc
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.same_domain_only = same_domain_only
        self.include_subdomains = include_subdomains
        self.exclude_patterns = exclude_patterns or []
        
        # Stare interna
        self.visited_urls = set()
        self.url_queue = deque([(self.base_url, 0)])
        self.page_content = {}
        self.resources = set()
        self.errors = []
        
        # Statistici
        self.pages_found = 0
        self.pages_processed = 0
        self.start_time = time.time()
        
        # Headers pentru request-uri
        self.headers = {
            'User-Agent': DEFAULT_USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ro-RO,ro;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
    def _normalize_url(self, url):
        """Normalizeaza URL-ul pentru consistenta"""
        if not url:
            return url
            
        # Adauga protocol daca lipseste
        if not url.startswith(('http://', 'https://')):
            # Încearca mai intai HTTPS
            test_url = f"https://{url}"
            try:
                response = requests.head(test_url, timeout=5, allow_redirects=True)
                if response.status_code < 400:
                    return response.url
            except:
                pass
            # Daca HTTPS nu functioneaza, foloseste HTTP
            return f"http://{url}"
            
        return url
        
    def should_crawl_url(self, url, depth):
        """Determina daca un URL ar trebui scanat"""
        # Verifica adancimea
        if depth > self.max_depth:
            return False
            
        # Verifica numarul de pagini
        if self.pages_processed >= self.max_pages:
            return False
            
        parsed = urlparse(url)
        
        # Verifica restrictiile de domeniu
        if self.same_domain_only:
            url_domain = parsed.netloc
            if self.include_subdomains:
                # Permite subdomenii ale domeniului de baza
                if not (url_domain == self.base_domain or 
                        url_domain.endswith(f'.{self.base_domain}')):
                    return False
            else:
                # Doar potrivire exacta de domeniu
                if url_domain != self.base_domain:
                    return False
                    
        # Verifica pattern-urile de excludere
        url_path = parsed.path
        for pattern in self.exclude_patterns:
            if '*' in pattern:
                # Potrivire simpla cu wildcard
                regex_pattern = pattern.replace('*', '.*')
                if re.match(regex_pattern, url_path):
                    return False
            elif pattern in url_path:
                return False
                
        # Nu scana anumite tipuri de fisiere
        if any(url_path.lower().endswith(ext) for ext in EXCLUDED_EXTENSIONS):
            return False
            
        return True
        
    def extract_links(self, html, base_url):
        """Extrage toate link-urile din HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        links = set()
        
        # Gaseste link-uri in diverse tag-uri
        for tag in soup.find_all(['a', 'link', 'area']):
            href = tag.get('href')
            if href and not href.startswith(('#', 'mailto:', 'tel:', 'javascript:')):
                absolute_url = urljoin(base_url, href)
                # Elimina fragmentul
                absolute_url = absolute_url.split('#')[0]
                if absolute_url:
                    links.add(absolute_url)
                    
        return links
        
    def extract_resources(self, html, base_url):
        """Extrage toate resursele (imagini, CSS, JS, etc.) din HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        resources = set()
        
        # Imagini
        for tag in soup.find_all(['img', 'source', 'picture']):
            src = tag.get('src') or tag.get('srcset') or tag.get('data-src')
            if src:
                # Gestioneaza srcset cu URL-uri multiple
                if ',' in src:
                    for part in src.split(','):
                        url = part.strip().split()[0]
                        if url:
                            resources.add(urljoin(base_url, url))
                else:
                    resources.add(urljoin(base_url, src))
                    
        # Fisiere CSS
        for tag in soup.find_all('link'):
            if 'stylesheet' in tag.get('rel', []):
                href = tag.get('href')
                if href:
                    resources.add(urljoin(base_url, href))
                
        # Fisiere JavaScript
        for tag in soup.find_all('script'):
            src = tag.get('src')
            if src:
                resources.add(urljoin(base_url, src))
                
        # Video si audio
        for tag in soup.find_all(['video', 'audio', 'source']):
            src = tag.get('src')
            if src:
                resources.add(urljoin(base_url, src))
                
        # Fonturi si alte resurse in stiluri inline
        for tag in soup.find_all(style=True):
            css_resources = self._extract_css_urls(tag['style'], base_url)
            resources.update(css_resources)
            
        # Resurse din tag-uri <style>
        for style in soup.find_all('style'):
            if style.string:
                css_resources = self._extract_css_urls(style.string, base_url)
                resources.update(css_resources)
                
        # Favicon si alte meta resurse
        for tag in soup.find_all('link'):
            if tag.get('rel') and any(rel in ['icon', 'apple-touch-icon', 'manifest'] 
                                     for rel in tag.get('rel')):
                href = tag.get('href')
                if href:
                    resources.add(urljoin(base_url, href))
                
        return resources
        
    def _extract_css_urls(self, css_content, base_url):
        """Extrage URL-uri din continut CSS"""
        urls = set()
        
        # Pattern-uri pentru diverse formate de URL in CSS
        patterns = [
            r'url\s*\(\s*["\']?([^"\'()]+)["\']?\s*\)',
            r'@import\s+["\']([^"\']+)["\']',
            r'@import\s+url\s*\(\s*["\']?([^"\'()]+)["\']?\s*\)'
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, css_content, re.IGNORECASE):
                url = match.group(1).strip()
                if url and not url.startswith(('data:', 'javascript:', '#')):
                    urls.add(urljoin(base_url, url))
                    
        return urls
        
    def crawl(self, progress_callback=None):
        """
        Metoda principala de crawling care descopera si descarca toate paginile
        
        Args:
            progress_callback: Functie callback pentru actualizarea progresului
            
        Returns:
            tuple: (dictionar cu continutul paginilor, set cu resursele gasite)
        """
        logger.info(f"Incepe scanarea pentru: {self.base_url}")
        
        while self.url_queue and not config.CANCELLED:
            # Gestioneaza pauza
            while config.PAUSED and not config.CANCELLED:
                time.sleep(0.5)
                
            if config.CANCELLED:
                logger.info("Scanare anulata de utilizator")
                break
                
            current_url, depth = self.url_queue.popleft()
            
            # Sari peste URL-urile deja vizitate
            if current_url in self.visited_urls:
                continue
                
            # Verifica daca ar trebui sa scanam acest URL
            if not self.should_crawl_url(current_url, depth):
                continue
                
            self.visited_urls.add(current_url)
            
            try:
                # Actualizeaza progresul
                if progress_callback:
                    from utils.constants import TEXTS
                    progress_callback(
                        -1, 
                        f"{TEXTS['status_crawling']} {TEXTS['pages_processed'].format(self.pages_processed, self.pages_found)}",
                        current_url
                    )
                
                # Descarca pagina
                response = requests.get(
                    current_url, 
                    headers=self.headers, 
                    timeout=DEFAULT_TIMEOUT,
                    allow_redirects=True
                )
                response.raise_for_status()
                
                # Verifica tipul de continut
                content_type = response.headers.get('content-type', '').lower()
                if 'text/html' not in content_type:
                    continue
                
                # Stocheaza continutul
                self.page_content[current_url] = response.text
                self.pages_processed += 1
                logger.info(f"Pagina scanata: {current_url}")
                
                # Extrage link-uri pentru scanare ulterioara
                if depth < self.max_depth:
                    links = self.extract_links(response.text, current_url)
                    for link in links:
                        if link not in self.visited_urls:
                            self.url_queue.append((link, depth + 1))
                            self.pages_found += 1
                            
                # Extrage resurse
                resources = self.extract_resources(response.text, current_url)
                self.resources.update(resources)
                
            except requests.exceptions.RequestException as e:
                error_msg = f"Eroare la accesarea {current_url}: {str(e)}"
                logger.error(error_msg)
                self.errors.append((current_url, str(e)))
            except Exception as e:
                error_msg = f"Eroare neasteptata pentru {current_url}: {str(e)}"
                logger.error(error_msg)
                self.errors.append((current_url, str(e)))
                
        logger.info(f"Scanare completa. Pagini: {self.pages_processed}, Resurse: {len(self.resources)}")
        return self.page_content, self.resources
        
    def get_statistics(self):
        """Returneaza statisticile crawling-ului"""
        elapsed_time = time.time() - self.start_time
        return {
            'pages_found': self.pages_found,
            'pages_processed': self.pages_processed,
            'resources_found': len(self.resources),
            'errors': len(self.errors),
            'elapsed_time': elapsed_time,
            'pages_per_second': self.pages_processed / elapsed_time if elapsed_time > 0 else 0
        }
import re
from urllib.parse import urlparse
import os

from config import EXCLUDED_EXTENSIONS, MAX_FILE_SIZE, RESOURCE_TYPES


def validate_url(url):
    """
    Valideaza un URL
    
    Args:
        url: URL-ul de validat
        
    Returns:
        tuple: (valid: bool, error_message: str sau None)
    """
    if not url:
        return False, "URL-ul nu poate fi gol"
    
    # Verifica lungimea
    if len(url) > 2048:
        return False, "URL-ul este prea lung (maxim 2048 caractere)"
    
    # Adauga protocol daca lipseste pentru validare
    test_url = url
    if not test_url.startswith(('http://', 'https://')):
        test_url = f"https://{url}"
    
    try:
        result = urlparse(test_url)
        
        # Verifica componentele obligatorii
        if not result.scheme:
            return False, "URL-ul nu are protocol valid"
        
        if result.scheme not in ['http', 'https']:
            return False, "Doar protocoalele HTTP si HTTPS sunt suportate"
        
        if not result.netloc:
            return False, "URL-ul nu are domeniu valid"
        
        # Verifica domeniul
        domain_pattern = re.compile(
            r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*'
            r'[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$'
        )
        
        if not domain_pattern.match(result.netloc.split(':')[0]):
            return False, "Domeniul contine caractere invalide"
        
        return True, None
        
    except Exception as e:
        return False, f"URL invalid: {str(e)}"


def validate_folder_name(folder_name):
    """
    Valideaza numele unui dosar
    
    Args:
        folder_name: Numele dosarului de validat
        
    Returns:
        tuple: (valid: bool, error_message: str sau None)
    """
    if not folder_name:
        return False, "Numele dosarului nu poate fi gol"
    
    # Verifica lungimea
    if len(folder_name) > 255:
        return False, "Numele dosarului este prea lung (maxim 255 caractere)"
    
    # Verifica caractere invalide
    invalid_chars = '<>:"|?*\0'
    for char in invalid_chars:
        if char in folder_name:
            return False, f"Numele dosarului contine caractere invalide: {char}"
    
    # Verifica nume rezervate pe Windows
    reserved_names = [
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    ]
    
    base_name = folder_name.split('.')[0].upper()
    if base_name in reserved_names:
        return False, f"'{folder_name}' este un nume rezervat de sistem"
    
    # Verifica daca incepe sau se termina cu spatiu sau punct
    if folder_name.startswith(' ') or folder_name.endswith(' '):
        return False, "Numele dosarului nu poate incepe sau termina cu spatiu"
    
    if folder_name.endswith('.'):
        return False, "Numele dosarului nu poate termina cu punct"
    
    return True, None


def validate_depth(depth):
    """
    Valideaza adancimea de crawling
    
    Args:
        depth: Adancimea de validat
        
    Returns:
        tuple: (valid: bool, error_message: str sau None)
    """
    try:
        depth_int = int(depth)
        
        if depth_int < 0:
            return False, "Adancimea nu poate fi negativa"
        
        if depth_int > 20:
            return False, "Adancimea maxima permisa este 20"
        
        return True, None
        
    except ValueError:
        return False, "Adancimea trebuie sa fie un numar intreg"


def validate_max_pages(max_pages):
    """
    Valideaza numarul maxim de pagini
    
    Args:
        max_pages: Numarul de validat
        
    Returns:
        tuple: (valid: bool, error_message: str sau None)
    """
    try:
        pages_int = int(max_pages)
        
        if pages_int < 1:
            return False, "Numarul de pagini trebuie sa fie cel putin 1"
        
        if pages_int > 10000:
            return False, "Numarul maxim de pagini permis este 10000"
        
        return True, None
        
    except ValueError:
        return False, "Numarul de pagini trebuie sa fie un numar intreg"


def validate_exclude_patterns(patterns_text):
    """
    Valideaza pattern-urile de excludere
    
    Args:
        patterns_text: Textul cu pattern-uri (unul pe linie)
        
    Returns:
        tuple: (valid: bool, patterns: list, error_message: str sau None)
    """
    if not patterns_text:
        return True, [], None
    
    patterns = []
    lines = patterns_text.strip().split('\n')
    
    for i, line in enumerate(lines, 1):
        pattern = line.strip()
        if not pattern:
            continue
        
        # Verifica lungimea
        if len(pattern) > 200:
            return False, [], f"Pattern-ul de pe linia {i} este prea lung (maxim 200 caractere)"
        
        # Verifica caractere invalide
        invalid_chars = '<>"|'
        for char in invalid_chars:
            if char in pattern:
                return False, [], f"Pattern-ul de pe linia {i} contine caractere invalide: {char}"
        
        patterns.append(pattern)
    
    # Verifica numarul total de pattern-uri
    if len(patterns) > 100:
        return False, [], "Numarul maxim de pattern-uri permis este 100"
    
    return True, patterns, None


def validate_file_size(size_bytes):
    """
    Valideaza dimensiunea unui fisier
    
    Args:
        size_bytes: Dimensiunea in bytes
        
    Returns:
        tuple: (valid: bool, error_message: str sau None)
    """
    if size_bytes <= 0:
        return False, "Dimensiunea fisierului este invalida"
    
    if size_bytes > MAX_FILE_SIZE:
        from utils.helpers import format_size
        return False, f"Fisierul este prea mare (maxim {format_size(MAX_FILE_SIZE)})"
    
    return True, None


def validate_content_type(content_type, allowed_types):
    """
    Valideaza tipul de continut
    
    Args:
        content_type: Header-ul Content-Type
        allowed_types: Lista de tipuri permise
        
    Returns:
        bool: True daca tipul este permis
    """
    if not content_type:
        return True  # Permitem daca nu stim tipul
    
    content_type = content_type.lower().split(';')[0].strip()
    
    for allowed in allowed_types:
        if allowed in content_type:
            return True
    
    return False


def validate_domain_match(url, base_domain, allow_subdomains=False):
    """
    Valideaza daca un URL apartine unui domeniu
    
    Args:
        url: URL-ul de verificat
        base_domain: Domeniul de baza
        allow_subdomains: Daca sunt permise subdomenii
        
    Returns:
        bool: True daca URL-ul apartine domeniului
    """
    try:
        parsed = urlparse(url)
        url_domain = parsed.netloc.lower()
        base_domain = base_domain.lower()
        
        # Elimina www. pentru comparatie
        if url_domain.startswith('www.'):
            url_domain = url_domain[4:]
        if base_domain.startswith('www.'):
            base_domain = base_domain[4:]
        
        if url_domain == base_domain:
            return True
        
        if allow_subdomains:
            return url_domain.endswith(f'.{base_domain}')
        
        return False
        
    except Exception:
        return False


def validate_resource_extension(url, resource_type):
    """
    Valideaza extensia unei resurse
    
    Args:
        url: URL-ul resursei
        resource_type: Tipul de resursa ('images', 'css', etc.)
        
    Returns:
        bool: True daca extensia este valida pentru tipul dat
    """
    if resource_type not in RESOURCE_TYPES:
        return False
    
    # Extrage extensia
    path = urlparse(url).path
    ext = os.path.splitext(path)[1].lower()
    
    # Verifica daca extensia este in lista pentru tipul dat
    return ext in RESOURCE_TYPES[resource_type]


def validate_crawl_settings(max_depth, max_pages, same_domain_only, patterns):
    """
    Valideaza toate setarile de crawling
    
    Args:
        max_depth: Adancimea maxima
        max_pages: Numarul maxim de pagini
        same_domain_only: Daca sa ramana pe acelasi domeniu
        patterns: Pattern-urile de excludere
        
    Returns:
        tuple: (valid: bool, errors: list)
    """
    errors = []
    
    # Valideaza adancimea
    valid, error = validate_depth(max_depth)
    if not valid:
        errors.append(f"Adancime: {error}")
    
    # Valideaza numarul de pagini
    valid, error = validate_max_pages(max_pages)
    if not valid:
        errors.append(f"Pagini: {error}")
    
    # Valideaza pattern-urile
    if patterns:
        patterns_text = '\n'.join(patterns)
        valid, _, error = validate_exclude_patterns(patterns_text)
        if not valid:
            errors.append(f"Pattern-uri: {error}")
    
    return len(errors) == 0, errors
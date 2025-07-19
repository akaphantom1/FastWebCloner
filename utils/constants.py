from __future__ import annotations
# utils/constants.py
# -*- coding: utf-8 -*-
"""
Constante ai texte pentru interfata
"""
# utils/constants.py
"""
Toate constantele centralizate pentru FastWebCloner.
ASCII only – fara diacritice in fiaier.
"""


# -------------------------- Retea -----------------------------------
DEFAULT_USER_AGENT = "FastWebCloner/0.1 (+https://example.local)"
DEFAULT_TIMEOUT = 10  # secunde

# -------------------- Filtrare fiaiere -------------------------------
# extensii pe care NU le tratam ca pagini HTML
EXCLUDED_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp",
    ".ico", ".css", ".js", ".pdf", ".zip", ".rar", ".7z",
    ".mp3", ".mp4", ".avi", ".mov", ".wmv", ".mkv",
    ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
}

# dimensiune maxima pentru o resursa (bytes)
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB

# clasificare resurse (extensie -> subfolder)
RESOURCE_TYPES = {
    "images": {".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp", ".ico"},
    "styles": {".css"},
    "scripts": {".js"},
    "docs":    {".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx"},
    "archives": {".zip", ".rar", ".7z"},
}

# -------------- Path‑guesses (crawl domeniu) -------------------------
COMMON_PATH_GUESSES = [
    "/", "/index", "/index.html", "/home", "/default", "/main",
    "/about", "/contact", "/profile", "/login", "/admin", "/files",
    "/downloads", "/sitemap", "/robots.txt",
]

# ------------------------- UI stub -----------------------------------



APP_NAME = "FastWebCloner"

COLORS = {
    "bg": "#F8FAFC",
    "secondary_bg": "#F1F5F9",
    "card_bg": "#FFFFFF",
    "text": "#1E293B",
    "button": "#3B82F6",
    "button_text": "#FFFFFF",
    "progress": "#10B981",
    "accent": "#8B5CF6",
    "hover": "#2563EB",
    "border": "#E2E8F0",
    "entry_bg": "#FFFFFF",
    "success": "#10B981",
    "warning": "#F59E0B",
    "error": "#EF4444",
    "highlight": "#DBEAFE",
    "shadow": "#0000001A",  # fost rgba(...)
}

TEXTS = {
    'title': 'FastWebCloner v1.0.0',
    'window_title': 'FastWebCloner - Instrument Avansat pentru Clonarea Site-urilor',

    # Etichete campuri
    'url_label': 'Domeniu/URL pentru clonare:',
    'url_placeholder': 'Introduceti domeniul sau URL-ul (ex: example.com)',
    'base_url_label': 'URL de baza nou (optional):',
    'base_url_placeholder': 'Introduceti noul URL de baza',
    'output_folder_label': 'Numele dosarului de ieaire:',
    'output_folder_placeholder': 'Introduceti numele dosarului',

    # Setari crawl
    'crawl_settings': 'Setari de Scanare',
    'max_depth': 'Adancime maxima de scanare:',
    'max_pages': 'Numar maxim de pagini:',
    'same_domain_only': 'Doar acelaai domeniu',
    'include_subdomains': 'Include subdomenii',

    # Setari resurse
    'resource_settings': 'Setari pentru Resurse',
    'include_images': 'Include imagini',
    'include_css': 'Include fiaiere CSS',
    'include_js': 'Include fiaiere JavaScript',
    'include_fonts': 'Include fonturi',
    'include_videos': 'Include videoclipuri',

    # Setari ieaire
    'output_settings': 'Setari de Salvare',
    'create_zip': 'Creeaza arhiva ZIP',
    'keep_folder': 'Pastreaza dosarul necomprimat',

    # Tipuri clonare
    'clone_type': 'Tip de clonare:',
    'single_page': 'Pagina unica',
    'entire_domain': 'Domeniu intreg',

    # Statusuri
    'status_idle': 'Pregatit pentru clonare',
    'status_crawling': 'Se scaneaza paginile...',
    'status_downloading': 'Se descarca resursele...',
    'status_processing': 'Se proceseaza fiaierele...',
    'status_compressing': 'Se creeaza arhiva...',
    'status_completed': 'Clonare finalizata!',

    # Progres / statistici
    'pages_found': 'Pagini gasite: {0}',
    'pages_processed': 'Pagini procesate: {0}/{1}',
    'resources_downloaded': 'Resurse: {0}/{1}',
    'stats_title': 'Statistici de Clonare',
    'time_elapsed': 'Timp scurs: {0}',
    'current_url': 'Curent: {0}',
    'errors_found': 'Erori: {0}',
    'download_speed': 'Viteza: {0}/s',
    'remaining_time': 'Timp ramas: {0}',

    # Butoane
    'clone_button': 'Începe Clonarea',
    'pause': 'Pauza',
    'resume': 'Continua',
    'cancel': 'Anuleaza',
    'settings': 'Setari',
    'about': 'Despre',
    'browse': 'Rasfoire...',

    # Excluderi
    'exclude_patterns': 'Modele de excludere (unul pe linie):',
    'exclude_placeholder': '/admin/\\n*.pdf\\n/private/*',

    # Eroare / confirmare
    'confirm': 'Confirmare',
    'cancel_confirm': 'Sunteti sigur ca doriti sa anulati procesul de clonare?',
    'error': 'Eroare',
    'success': 'Succes',
    'domain_required': 'Va rugam sa introduceti un domeniu sau URL valid.',
    'output_option_required': 'Selectati cel putin o optiune de salvare.',
    'invalid_input': 'Date de intrare invalide',

    # Despre
    'about_title': 'Despre WebCloner Pro',
    'about_message': (
        "FastWebCloner v1.0.0\n\n"
        "Instrument profesional pentru clonarea completa a site-urilor web.\n\n"
        "Dezvoltat de echipa WebCloner Pro\n\n"
        "Caracteristici principale:\n"
        "• Scanare completa a domeniilor\n"
        "• Gestionare avansata a resurselor\n"
        "• Filtrare personalizata\n"
        "• Interfata moderna ai intuitiva\n"
        "• Suport pentru site-uri complexe"
    ),

    # Stari runtime
    'default_folder': 'site_clonat',
    'process_paused': 'Proces intrerupt',
    'process_cancelled': 'Proces anulat',
    'cleanup_cancelled': 'Se curata fiaierele...',

    # Finalizare
    'both_created': 'Clonare completa!\n\n Fiaiere salvate in:\n• ZIP: {0}\n• Dosar: {1}',
    'zip_created': 'Domeniu clonat ai arhivat:\n{0}',
    'folder_kept': 'Domeniu clonat in dosarul:\n{0}',

    # Diverse
    'loading': 'Se incarca...',
    'please_wait': 'Va rugam aateptati...',
    'operation_in_progress': 'Operatiune in curs...',
    'select_folder': 'Selectati dosarul de salvare',
}

LOG_MESSAGES = {
    'start_crawl': 'Începe scanarea pentru: {0}',
    'page_crawled': 'Pagina scanata: {0}',
    'resource_downloaded': 'Resursa descarcata: {0}',
    'error_download': 'Eroare la descarcarea: {0} - {1}',
    'crawl_complete': 'Scanare completa. Pagini: {0}, Resurse: {1}',
    'save_complete': 'Salvare completa in: {0}',
    'validation_error': 'Validare eauata: {0}',
    'config_loaded': 'Configuratie incarcata',
    'app_started': 'Aplicatia a fost pornita',
}

DEFAULT_SETTINGS = {
    'max_depth': 3,
    'max_pages': 100,
    'same_domain': True,
    'include_subdomains': True,
    'include_images': True,
    'include_css': True,
    'include_js': True,
    'include_fonts': True,
    'include_videos': False,
    'create_zip': True,
    'keep_folder': False,
    'clone_type': 'entire_domain',
    'output_folder': 'site_clonat',
    'exclude_patterns': ['/admin/', '*.pdf', '/private/*'],
}
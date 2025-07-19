
import os

# Informatii despre aplicatie
APP_VERSION = "3.0.0"
APP_NAME = "FastWebClonez"
APP_AUTHOR = "FastWebClonez Development Team"

# Limite implicite pentru crawling - pot fi modificate din interfata
DEFAULT_MAX_DEPTH = 3        # cat de adanc sa intre in site
DEFAULT_MAX_PAGES = 100      # cate pagini maxim sa scaneze
DEFAULT_TIMEOUT = 10         # timeout pentru fiecare request HTTP in secunde
DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Dimensiuni fereastra principala
WINDOW_WIDTH = 950          # latime initiala
WINDOW_HEIGHT = 820         # inaltime initiala  
MIN_WINDOW_WIDTH = 800      # latime minima permisa
MIN_WINDOW_HEIGHT = 700     # inaltime minima permisa

# Cai si directoare folosite de aplicatie
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESOURCES_DIR = os.path.join(BASE_DIR, 'resources')

# Extensii de fisiere pe care le excludem automat din descarcare
# Acestea sunt fisiere mari care nu sunt necesare pentru vizualizare offline
EXCLUDED_EXTENSIONS = {
    '.pdf', '.zip', '.rar', '.tar', '.gz', '.7z',
    '.exe', '.dmg', '.iso', '.mp4', '.avi', '.mov',
    '.mp3', '.wav', '.flac', '.doc', '.docx', '.xls',
    '.xlsx', '.ppt', '.pptx', '.msi', '.deb', '.rpm'
}

# Categorii de resurse web si extensiile asociate
# Folosit pentru a grupa fisierele descarcate si pentru filtrare
RESOURCE_TYPES = {
    'images': ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.ico', '.bmp'],
    'css': ['.css'],
    'js': ['.js'],
    'fonts': ['.woff', '.woff2', '.ttf', '.otf', '.eot'],
    'videos': ['.mp4', '.webm', '.ogg', '.avi', '.mov']
}

# Limite pentru protectie impotriva site-urilor foarte mari
MAX_FILE_SIZE = 100 * 1024 * 1024    # 100 MB per fisier
MAX_TOTAL_SIZE = 1024 * 1024 * 1024  # 1 GB total pentru tot site-ul

# Spatiere si dimensiuni pentru elementele din interfata
UI_PADDING = 20        # spatiu intre sectiuni
CARD_PADDING = 15      # spatiu in interiorul cardurilor
BUTTON_HEIGHT = 45     # inaltime butoane
ENTRY_HEIGHT = 40      # inaltime campuri text

# Variabile globale pentru controlul procesului de clonare
# Acestea permit pauza si anularea din interfata
PAUSED = False      # True cand utilizatorul apasa pauza
CANCELLED = False   # True cand utilizatorul anuleaza procesul
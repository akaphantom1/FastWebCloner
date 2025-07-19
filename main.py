#!/usr/bin/env python3
import sys
import logging
from ui.main_window import WebClonerApp

# Configurare logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Functia principala care porneste aplicatia"""
    try:
        app = WebClonerApp()
        app.run()
    except Exception as e:
        logging.error(f"Eroare la pornirea aplicatiei: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
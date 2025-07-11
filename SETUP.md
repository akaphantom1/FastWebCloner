FastWebCloner/
│
├── main.py # Punctul principal de intrare
├── config.py # Configurari globale
├── requirements.txt # Lista dependentelor Python
├── README.md # Documentatia proiectului
├── SETUP.md # Acest fisier
├── .gitignore # Fisiere ignorate de Git
├── run.bat # Script pornire Windows
├── run.sh # Script pornire Linux/macOS
│
├── core/ # Pachet pentru logica de baza
│ ├── **init**.py
│ ├── crawler.py # Motor de crawling
│ ├── downloader.py # Descarcator de resurse
│ └── processor.py # Procesor HTML/CSS
│
├── ui/ # Pachet pentru interfata grafica
│ ├── **init**.py
│ ├── main_window.py # Fereastra principala
│ ├── components.py # Componente UI reutilizabile
│ └── dialogs.py # Ferestre de dialog
│
└── utils/ # Pachet pentru utilitati
├── **init**.py
├── constants.py # Constante si traduceri
├── helpers.py # Functii ajutatoare
└── validators.py # Functii de validare

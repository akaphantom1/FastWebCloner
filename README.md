# FastWebCloner
FastWebCloner este o aplicație de tip web scraper + offline site cloner care permite salvarea completă a unei pagini web sau a unui întreg domeniu, exact așa cum arăta în momentul realizării snapshot-ului. Toate resursele (HTML, CSS, JavaScript, imagini, fișiere etc.) sunt descărcate și restructurate local, astfel încât site-ul să poată fi vizualizat complet offline, fără conexiune la internet.


Acest lucru implică:

-> Snapshot pentru o singură pagină web: salvarea paginii și a tuturor resurselor de pe pagina respectivă (documente, imagini etc) și înlocuirea link-urilor cu link-uri locale

-> Snapshot pentru un domeniu: același lucru ca la o singură pagină, dar pentru toate paginile accesibile pe domeniul respectiv. Pentru identificarea acestora se vor prelua recursiv linkurile de pe pagină și apoi se vor descărca și paginile respective, iar suplimentar aplicația va avea și un dicționar de pagini pe care sa le “încerce” (ex: /index, /files, /profile, etc.)

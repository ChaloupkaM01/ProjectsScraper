# ProjectsScraper

Zadání 1:
- Extrakce dat z prostředí VaV souvisejících s projekty. (Kategorie projektů, typy projektů, projekty, doby řešení, řešitelské kolektivy)

Společné podmínky:
- Datové struktury jako JSON file, alternativně přímý zápis do postgreSQL
- Normalizované datové struktury podle DBDefinitions v příslušných kontejnerech
- ID generovat podle uuid1
- Mapping generované id (uuid) a originální id 

Podmínky ke spuštění:
- Nainstalovat knihovny z requirements.txt
- Vytvořit soubor .env se záznamy UNAME="", PASSWD="", které je třeba naplnit přihlašovacími údaji na unob.cz

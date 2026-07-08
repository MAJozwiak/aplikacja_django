## Opis projektu

Aplikacja webowa zbudowana w frameworku Django, służąca do zarządzania 
hierarchiczną bazą pytań sprawozdawczych oraz automatycznego generowania ankiet 
jakościowych dla podmiotów sprawozdających.

Aplikacja umożliwia:
- zarządzanie hierarchiczną strukturą pytań sprawozdawczych (obszary → bloki → 
  podbloki → pytania → podzapytania)
- wersjonowanie pytań w oparciu o okresy sprawozdawcze z zachowaniem pełnej 
  historii zmian
- zarządzanie podmiotami sprawozdającymi oraz grupami podmiotów
- budowanie ankiet poprzez przypisywanie pytań do nagłówków ankiet
- automatyczne generowanie formularzy ankietowych w formacie Excel dla 
  wybranych grup podmiotów

Projekt powstał jako element systemu sprawozdawczości opartego na taksonomii 
w ramach pracy magisterskiej na Politechnice Poznańskiej, Wydział Informatyki 
i Telekomunikacji.

## Technologie

- **Python 3.x**
- **Django 5.2.9**
- **SQLite** (domyślna baza danych)
- **openpyxl** (generowanie plików Excel)

## Instrukcja uruchomieniowa


### Zainstalowanie zależności
```
pip install -r .\requirements.txt
```

### Przeprowadzenie migracji
```
python manage.py makemigrations
python manage.py migrate
```

### uruchomienie serwera programistycznego
```
python manage.py runserver
```

### Stworzenie superuser-a
```
python manage.py createsuperuser

```

### Stworzenie pierwszego roku w bazie (tylko za pierwszym uruchomieniem)
```
Pod adresem http://127.0.0.1:8000/admin/ dodać pierwszy rok sprawozdawczy w modelu "Okres sprawozdawczy".
```

### Kolejne uruchomienie
```
python manage.py runserver
```

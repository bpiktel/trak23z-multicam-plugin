# Blender Multicamera Rendering Plugin

TRAK 23Z project

### Setup

- Python 3.7.9 (doesn't work with higher python versions)
- create venv with requirements file
- add plugin to blender: Edit -> Preferences -> Add-ons -> Install




## Task details (PL)

### Wielokamerowy rendering w programie Blender
#### Prowadzący: dr inz. Łukasz Dąbała

##### W ramach projektu należy stworzyć wtyczkę do programu Blender, która będzie umożliwiać tworzenie zestawu kamer do różnych potrzeb.
##### Wtyczka powinna umożliwiać:

1. tworzenie kamery stereo w różnych trybach
   1. tryb równoległy — kamery mają równoległe osie widoku
   2. tryb zbieżny — osie widoku kamer przetną się. Miejsce przecięcia powinno byc możliwe do ustawienia
2. tworzenie kamery typu light-field
   1. wiele kamer ustawionych w macierz z różnym oddaleniem od siebie (zarówno w osi pionowej, jak i poziomej)
   2. kamera plenoptyczna - obrazy sa od siebie oddalone o 1-2 piksele
3. tworzenie sieci kamer wokół zadanego obiektu i sceny
   1. ułożenie równomierne według zadanego pasa wokół obiektu
   2. ułożenie równomierne na kuli wokół obiektu
   3. ułożenie optymalne wokół obiektu — staramy się minimalizować liczbę kamer tzn. każda kolejna kamera powinna dostarczać jakaś informacje na temat obiektu
4. ustawienie renderingu
   1. każda kamera ma swój folder na obrazy
   2. aplikacja zadanych właściwości z kamer do wszystkich kamer utworzonych z wykorzystaniem wtyczki
5. rendering ze wszystkich kamer — rozpoczęcie renderingu powinno renderować według zadanego trybu tzn. kamera po kamerze lub klatka po klatce
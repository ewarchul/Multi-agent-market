# Opis Projektu 
Projekt polega na utworzeniu symulatora rynku dóbr. Ma on na celu zbadanie różnych mechanizmów występujących na rynku. Agenci mają możliwość przeprowadzania transakcji kupna i sprzedaży oraz magazynowania dóbr. Każdy z agentów musi zaspokajać swoje potrzeby konsumpcyjne, niektórzy agenci mogą także produkować dobra. Agenci dysponują walutą, za którą mogą nabywać dobra. Celem agenta jest zaspokojenie potrzeb konsumpcyjnych ???(i zdobycie jak najwięcej waluty lub poniesienie jak najmniejszego kosztu)???

# Model rynku 

## Sesja 
* rynek działa ciągle i po czasie $t$ jego stan jest archiwizowany 
* agenci ciągle mogą ze sobą wchodzić w interkacje i nie są poinformowani o czasie $t$ 

## Struktura połączeń
* struktura połączeń jest generowana przez wybrany graf losowy (Barabasi-Albert, dowolony inny lub zadany przez użytkownika)

# Model Agenta

## Zasoby
* agent $A_i$ w chwili $t$ posiada $Z^{A_i}(t)$ zasobu i ma możliwość wygenerować większą jego ilość, która będzie go kosztowała  $g(z)$, gdzie $z$ jest przyrostem zasobu
* agent może przechowywać zasób lub go sprzedać, wchodząc w negocjacje handlowe z pozostałymi agentami na rynku, z którymi agent jest połączony (patrz struktura połączeń)
* produkcja agenta jest ograniczona przez $P^{A_i}_{max}(t, \delta t)$
* każdy agent posiada maksymalny stan magazynowy zasobu $Z$, którego nie może przekroczyć, i wynosi on $M^{A_i}$
* jeśli agent przekroczy maksymalny stan posiadania $M^{A_i}$, to zobligowany jest do zapłacenia kosztu utylizacji nadmiarowej ilości zasobu $Z$
* agenci dysponują potrzebami konsumpcyjnymi $C^{A_i}(t, \delta t)$, które chcą zaspokoić
* jeśli agent nie zaspokoi swoich potrzeb konsumpcyjnych po czasie $T$ od ich wygenerowania, to zobligowany jest do zapłacenia kosztu 
* agenci posiadają na starcie określoną ilość środka wymiany $K^{A_i}$, który jest im przydzialny w sposób losowy lub zdeterminowany przy inicjalizacji systemu
* agent otrzymuje środek wymiany zgodnie z funkcją $f^{A_i}(\dot)$ 

## Polityka decyzyjna 
* todo

## Protokół komunikacyjny 
* todo, bo skomplikowany -- trzeba ogarnąć papery 
* warto uwzględnić uwagę dr. hab. inż. Pawła Wawrzyńskiego odnośnie tego, że agenty w czasie NEGOCJACJI mogą je zerwać! 

# Technologia
* implementacja w języku `Python` z wykorzystaniem bibliotek: ...
* analizy danych wykonywane będą w języku `R` 

# Eksperymenty (przykładowe)
* nadmiar podaży, a niedomiar popytu
* niedomiar podaży, nadmiar popytu
* generacja monopoli
* symulacja zdrowego rynku (stan równowagi)
* określenie realnej wartości zasobu $Z$ na podstawie cen proponowanych przez agenty w trakcie negocjacji handlowych
* co się dzieje na rynku, gdy pojawiają się podmioty wyłącznie magazynujące towar (chomiki lub logistyka)
* sezonowość produkcji lub konsumpcji 
* trajektoria cen w funkcji polityki decyzyjnej agentów
* odporność na błędy polityki decyzyjnej lub parametrów początkowych

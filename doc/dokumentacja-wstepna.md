# Opis Projektu 
Projekt polega na utworzeniu symulatora rynku dóbr. Ma on na celu zbadanie różnych mechanizmów występujących na rynku. Agenci mają możliwość przeprowadzania transakcji kupna i sprzedaży oraz magazynowania dóbr. Każdy z agentów musi zaspokajać swoje potrzeby konsumpcyjne, niektórzy agenty mogą także produkować dobra. Agenci dysponują środekiem wymiany, za którą mogą nabywać dobra. 
Cele agenta są różne i zależne od jego polityki decyzyjnej, która z kolei zależy od konfiguracji.

# Model rynku 

## Sesja 
* rynek działa ciągle i po czasie $t$ jego stan jest archiwizowany 
* agenty ciągle mogą ze sobą wchodzić w interkacje i nie są poinformowani o czasie $t$ 

## Struktura połączeń
* struktura połączeń jest generowana przez wybrany graf losowy (Barabasi-Albert, dowolony inny lub zadany przez użytkownika) i determinuje ona strukturę rynku, na którym operują agenty


# Model Agenta

## Zasoby
* agent $A_i$ w chwili $t$ posiada $Z^{A_i}(t)$ zasobu i ma możliwość wygenerować większą jego ilość, która będzie go kosztowała  $g(z)$, gdzie $z$ jest przyrostem zasobu
* agent może przechowywać zasób lub go sprzedać, wchodząc w negocjacje handlowe z pozostałymi agentami na rynku, z którymi agent jest połączony (patrz struktura połączeń)
* produkcja agenta jest ograniczona przez $P^{A_i}_{max}(t, \delta t)$
* każdy agent posiada maksymalny stan magazynowy zasobu $Z$, którego nie może przekroczyć, i wynosi on $M^{A_i}$
* jeśli agent przekroczy maksymalny stan posiadania $M^{A_i}$, to zobligowany jest do zapłacenia kosztu utylizacji nadmiarowej ilości zasobu $Z$
* agenty mają potrzeby konsumpcyjne $C^{A_i}(t, \delta t)$, które chcą zaspokoić
* jeśli agent nie zaspokoi swoich potrzeb konsumpcyjnych po czasie $T$ od ich wygenerowania, to zobligowany jest do zapłacenia kosztu 
* agenty posiadają na starcie określoną ilość środka wymiany $K^{A_i}$, który jest im przydzialny w sposób losowy lub zdeterminowany przy inicjalizacji systemu
* agent otrzymuje środek wymiany zgodnie z funkcją $f^{A_i}(\dot)$ 

## Polityka decyzyjna 

Polityka decyzyjna określa zachowanie agentów na rynku.


Przyjmuje się, że polityka decyzyjna agenta sparametryzowana jest następującymi wielkościami: 
* obecne zapotrzebowanie agenta $R \geq 0$ 
* czas, w którym agent musi zaspokoić swoje zapotrzebowanie $T_s$ liczony od czasu startu sesji
* obecny stan agenta $S$, który jest liczbą posiadanych jednostek zasobu $Z$ przez agenta
* obecny budżet agenta $B$, który jest liczbą posiadanych jednostek wymiany $K$ przez agenta
* funkcją kosztu produkcji $g(z)$
* funkcją limitu produkcji $P(t, \delta t)$
* kosztem utylizacji dóbr nadmiarowych $M_c$
* kosztem niezaspokojenia potrzeb konsumpcyjnych $C$
* limitem posiadanych jednostek zasobu $M$


Agent w oknie czasowym $T_w$, wyznaczającym czas trwania negocjacji, generuje oferty sprzedaży (obiekt `Os`) oraz kupna (obiekt `Ob`), na które nałożone są limity:
* `Ob.value` $\leq B$ $\land$ `Ob.n` $\leq M - S$, które kolejno oznaczają: cena zakupionej ilości towaru nie może przekraczać budżetu agenta oraz ilość zakupionego towaru nie może być większa od dostępnej jeszcze liczby jednostek zasobu, które agent może przechowywać.  
* `Os.n` $\leq S$, tj. ilość sprzedanego towaru nie może być większa pod stan posiadania agenta.

Na podstawie powyższych ustaleń proponowana polityka decyzyjna agenta może być wyglądać następująco:
* `O's`, `O'b` są aktualnymi ofertami kupna i sprzedaży 
* `Ns` jest kontrahentem


```
  buyer initializes
    initial buy offer = (rand(R - S, M - S), 0 if Ob empty else min(Ob).value * rand(0, 1))
   
    seller counter offer:
        n = min{S, O'b(Ns).number}
        value = random with boundaries:
            value >= max(g(S), O'b(Ns).value)
            if O's not empty:
                value < min{O's(n) where n is not self}

    buyer counter offer:
        n = keep previous w.r.t. limits
        if n = 0 then withdraw
        value = random with distribution depending on Ts and boundaries:
            value <= min{O's} & value >= previous
```

Pełna specyfikacja obiektów, które występują w powyższym pseudokodzie zostana umieszczona w dokumentacji opisującej część implementacyjną.



## Protokół komunikacyjny 
* szczegółowa specyfikacja protokołu komunikacyjnego powstanie w trakcie realizacji i będzie dostosowana do planowanych eksperymentów 
* zakłada się, że protokół będzie umożliwiał komunikacje $1-m$ oraz $1-1$

# Technologia
* implementacja w języku `Python` z wykorzystaniem bibliotek: `networkx`, `spade`, `PyGraphViz`
* analizy danych wykonywane będą w języku `R` z wykorzystaniem ekosystemu `tidyverse`

# Propozycje eksperymentów
* nadmiar podaży, a niedomiar popytu
* niedomiar podaży, nadmiar popytu
* generacja monopoli (sytuacja na rynku, w której niewielka liczba agentów -- dwóch lub trzech -- posiada większość dostepnych zasobów)
* symulacja zdrowego rynku (stan równowagi)
* określenie realnej wartości zasobu $Z$ na podstawie cen proponowanych przez agenty w trakcie negocjacji handlowych
* co się dzieje na rynku, gdy pojawiają się podmioty wyłącznie magazynujące towar (chomiki lub logistyka)
* sezonowość produkcji lub konsumpcji 
* trajektoria cen w funkcji polityki decyzyjnej agentów
* odporność na błędy polityki decyzyjnej lub parametrów początkowych

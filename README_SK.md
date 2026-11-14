# Kysucká moderná chata — vizualizačný projekt

Michal, toto je samostatný pracovný začiatok vizualizácie podľa obrázka.
Model je pripravený na otvorenie a postupné zlepšovanie; hotová vizualizácia
ani architektonické preverenie sa zatiaľ netvrdia.

## Začni tu

1. Pracuj v Git repozitári https://github.com/cisarik/kysucka_moderna_chata.
   Pri novom klone použi --recurse-submodules; po bežnom klone inicializuj
   prijatý submodul príkazom git submodule update --init --recursive.
2. Prečítaj AGENTS.md a docs/VISUAL_BRIEF.md. Aktuálny celok koordinuje jeho
   Orchestrator; Master koordinuje vývojový beh. Starý prompt sa z histórie
   nevykonáva ako nové povolenie.
3. Vizuálny cieľ je reference/kysucka_chata_moderna.png. Zachovaný počiatočný
   model je blender/kysucka_chata_seed.blend; referencia je v ňom zabalená.
   Python auto-run ani add-on nie sú potrebné.
4. Michal doručuje aktuálne úplné prompty manuálne do určenej relácie.
   Režim a súradnice určuje grant. Súhlas s plánom ani tlačidlo Build
   neposkytujú realizačné povolenie.
5. Prompty a správy patria do externého cisarik/meta podľa AGENTS.md.
   Worker uloží vlastnú správu len s povolením a dostupnou schopnosťou;
   pri obmedzení klienta vráti úplný výstup a uvedie chýbajúce uloženie.
6. Inicializačný celok zavádza AP/Meta bez úpravy vizualizácie. Prácu na
   kanonickom renderi, kamere alebo siluete musí vybrať a povoliť ďalší celok.

## Obsah

| Súbor / priečinok | Na čo slúži |
|---|---|
| docs/Kysucka_chata_pracovna_studia_S00.pdf | 21 listov A3: referencia, kóty, pôdorysy, strecha, pohľady, rezy, otvory, detaily a postup |
| cad/Kysucka_chata_S00_all_views.dxf | všetkých 13 vektorových schém v jednom CAD súbore, v mm |
| cad/*.dxf a cad/svg/ | samostatné editovateľné schémy; mm v DXF, tlačové mierky v SVG |
| blender/kysucka_chata_seed.blend | reálny počiatočný model; Blender 4.3.2, metre |
| previews/camera_a_material.png | skutočný počiatočný farebný render z .blend |
| previews/camera_a_clay.png | skutočný sivý kontrolný render rovnakej kamery |
| model/parameters.json | spoločné hlavné rozmery, otvory, miestnosti, materiálové ciele a kamera |
| model/reference_landmarks.json | ručne orientačne označené body referencie, s neistotou |
| scripts/ | znovuvytvorenie CAD/PDF a scény; iba s aktuálnym povolením úprav |
| docs/OPERATIONS.md | lokálna cesta ovládania Blenderu; CLI bez MCP |
| .ap/, .gitmodules | prijatý nemenný AP submodul; presný commit určuje gitlink |
| AGENTS.md | aktuálne projektové pravidlá a vlastníci zdrojov |
| reference/kysucka_chata_moderna.png | zachovaný vizuálny cieľ |
| manifest/ | historické inventáre pôvodného S00 balíka, nie aktuálne Git brány |
| externý cisarik/meta | historické prompty, správy, poznámky a odovzdanie celku |

## Čo je isté a čo je odhad

Istý je dodaný referenčný obrázok a prítomnosť viditeľných motívov.
Zvolená stopa **14,4 × 8,4 m**, otvorená časť 2,4 m, sklon 45°,
dispozícia, skryté fasády a všetky výšky sú pracovné hypotézy.
Obal uzavretej časti má geometricky 100,8 m²; nejde o normovú úžitkovú plochu.
Obytné podkrovie sa v S00 nepridáva. Rozhodnutia môžeš neskôr zmeniť.

PDF je pracovná vizualizačná štúdia. Detaily sú detaily tvaru a výrazu,
nie skladby, kotvenie ani výrobná dokumentácia. Architektovi zatiaľ nič
netreba odovzdávať; najprv chceš dosiahnuť veľmi dobrú vizualizáciu.

## Čo bude treba z internetu

Na otvorenie a prvý render nič. Všetky súčasné materiály sú procedurálne;
obrázok je zabalený. Až po prijatí tvaru a kamery môže Worker dostať presný
grant na konkrétne PBR drevo, kameň, kvalitné rastliny alebo HDRI.
Poly Haven a ambientCG poskytujú CC0 aktíva; konkrétne súbory sa ešte nevybrali.
Každý budúci import má mať zaznamenaný pôvod, licenciu a kontrolný súčet.
Neznáme modely s automatickými skriptmi a balíky platených doplnkov sa
nemajú inštalovať len preto, že je otvorený Blender.

## Dôležité pre ďalšiu prácu

- Pôvodný seed si zachovaj. Budúce verzie nech vznikajú ako pomenované kópie.
- Worker používa deklarovanú cestu blender-local-v1 v docs/OPERATIONS.md; iná cesta vyžaduje konkrétny grant.
- Nepracuj súčasne ručne aj Workerom na tom istom súbore. GUI po externom
  uložení potrebuje bezpečné opätovné načítanie.
- Ručná úprava .blend nemení JSON a generátor; pred regeneráciou sa musí
  zosúladiť, ktorá verzia je prijatá.
- Stromy, kvety a nábytok sú zámerné náhrady. Prvé prijatie má sledovať
  kameru a siluetu, nie kvalitu botanických detailov.
- Projekt je Git repozitár s kanonickým originom uvedeným vyššie. Lokálny commit, verejné publikovanie a prijatie sú samostatné tvrdenia, ktoré sa overujú pri konkrétnej úlohe.

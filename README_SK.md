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
3. Vizuálny cieľ je reference/kysucka_chata_moderna.png. Aktuálnu pracovnú kópiu
   otvor cez File → Open → blender/kysucka_chata_mcp_v02.blend. Má kameru
   s ohniskom 35 mm, shift_y = 0.105 a kamerový pohľad Cycles so svetlami
   a svetom scény. Zachované sú blender/kysucka_chata_mcp_v01.blend aj
   počiatočný model blender/kysucka_chata_seed.blend;
   referencia je zabalená vo všetkých troch súboroch. Na otvorenie netreba auto-run ani MCP.
4. Michal doručuje aktuálne úplné prompty manuálne do určenej relácie.
   Režim a súradnice určuje grant. Súhlas s plánom ani tlačidlo Build
   neposkytujú realizačné povolenie.
5. Prompty a správy patria do externého cisarik/meta podľa AGENTS.md.
   Worker uloží vlastnú správu len s povolením a dostupnou schopnosťou;
   pri obmedzení klienta vráti úplný výstup a uvedie chýbajúce uloženie.
6. Inicializačný celok zaviedol AP/Meta. V01 upravuje zvislé rámovanie;
   aktuálna v02 vyberá perspektívu z troch kamier. Vizuálne prijatie zostáva
   na tebe. Ďalšie úpravy musí
   pomenovať a povoliť aktuálny úplný grant.

## Obsah

| Súbor / priečinok | Na čo slúži |
|---|---|
| docs/Kysucka_chata_pracovna_studia_S00.pdf | 21 listov A3: referencia, kóty, pôdorysy, strecha, pohľady, rezy, otvory, detaily a postup |
| cad/Kysucka_chata_S00_all_views.dxf | všetkých 13 vektorových schém v jednom CAD súbore, v mm |
| cad/*.dxf a cad/svg/ | samostatné editovateľné schémy; mm v DXF, tlačové mierky v SVG |
| blender/kysucka_chata_seed.blend | reálny počiatočný model; Blender 4.3.2, metre |
| blender/kysucka_chata_mcp_v01.blend | zachovaná prvá pracovná kópia cez MCP; 50 mm, posun kamery 0.075 |
| blender/kysucka_chata_mcp_v02.blend | aktuálna pracovná kópia cez MCP; Blender 5.2.3 LTS, 35 mm, posun kamery 0.105, kamerový pohľad Cycles |
| previews/camera_a_material.png | skutočný počiatočný farebný render z .blend |
| previews/camera_a_clay.png | skutočný sivý kontrolný render rovnakej kamery |
| model/parameters.json | spoločné hlavné rozmery, otvory, miestnosti, materiálové ciele a kamera |
| model/reference_landmarks.json | ručne orientačne označené body referencie, s neistotou |
| scripts/ | znovuvytvorenie CAD/PDF a scény; iba s aktuálnym povolením úprav |
| docs/OPERATIONS.md | lokálna kontrola Blenderu a grantom aktivovaná cesta živého MCP |
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
- Worker používa cestu pomenovanú aktuálnym grantom: blender-local-v1 na lokálnu kontrolu, v tomto celku blender-mcp-live-v1 na živé ovládanie. Obe opisuje docs/OPERATIONS.md; ďalšie úpravy vyžadujú konkrétny grant.
- Nepracuj súčasne ručne aj Workerom na tom istom súbore. GUI po externom
  uložení potrebuje bezpečné opätovné načítanie.
- Ručná úprava .blend nemení JSON a generátor; pred regeneráciou sa musí
  zosúladiť, ktorá verzia je prijatá.
- V02 zlepšuje obrys strechy a pomer fasád pri nezmenenom modeli. Poloha
  krbu za rohom a rozsah plota zostávajú kompromismi; porovnanie troch
  kamier a merania sú v externom Meta celku 00/02-reference-camera-perspective/.
- Stromy, kvety a nábytok sú zámerné náhrady. Prvé prijatie má sledovať
  kameru a siluetu, nie kvalitu botanických detailov.
- Projekt je Git repozitár s kanonickým originom uvedeným vyššie. Lokálny commit, verejné publikovanie a prijatie sú samostatné tvrdenia, ktoré sa overujú pri konkrétnej úlohe.

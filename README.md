# Kysucká moderná chata — vizualizačný projekt

## Render

![01](github/02.png)

## Začni tu

1. Pracuj v Git repozitári https://github.com/cisarik/kysucka_moderna_chata.
   Pri novom klone použi --recurse-submodules; po bežnom klone inicializuj
   prijatý submodul príkazom git submodule update --init --recursive.
2. Prečítaj AGENTS.md a docs/VISUAL_BRIEF.md. Aktuálny celok koordinuje jeho
   Orchestrator; Master koordinuje vývojový beh. Starý prompt sa z histórie
   nevykonáva ako nové povolenie.
3. Vizuálny cieľ je reference/kysucka_chata_moderna.png. Aktuálnu pracovnú kópiu
   otvor cez File → Open → blender/kysucka_chata_mcp_v05.blend. Má kameru
   s ohniskom 35 mm, shift_y = 0.105 a kamerový pohľad Cycles so svetlami
   a svetom scény. Zachované sú v04, v03, v02, v01 aj počiatočný seed;
   v05 obsahuje zabalenú referenciu, drevo a použité textúry rastlín a trávy. Na otvorenie netreba auto-run ani MCP.
4. Michal doručuje aktuálne úplné prompty manuálne do určenej relácie.
   Režim a súradnice určuje grant. Súhlas s plánom ani tlačidlo Build
   neposkytujú realizačné povolenie.
5. Prompty a správy patria do externého cisarik/meta podľa AGENTS.md.
   Worker uloží vlastnú správu len s povolením a dostupnou schopnosťou;
   pri obmedzení klienta vráti úplný výstup a uvedie chýbajúce uloženie.
6. Inicializačný celok zaviedol AP/Meta. V01 upravuje zvislé rámovanie;
   v02 vyberá perspektívu z troch kamier a v03 pridáva PBR drevo a plot v popredí. Vizuálne prijatie zostáva
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
| blender/kysucka_chata_mcp_v02.blend | zachovaná perspektívna pracovná kópia; 35 mm, posun kamery 0.105 |
| blender/kysucka_chata_mcp_v03.blend | zachovaná pracovná kópia; PBR drevo, rustikálny plot, rovnaká kamera a Cycles CPU s OIDN |
| blender/kysucka_chata_mcp_v04.blend | zachovaná predchádzajúca kópia; kopce, hustý les, jabloň s ovocím a prirodzená výsadba |
| scripts/landscape_v04.py | spoločná deterministická úprava prostredia a rastlín |
| assets/ASSET_MANIFEST.md | drevo a rastlinné modely, autori, licencie, úpravy a kontrolné súčty |
| scripts/timber_fence_v03.py | spoločná explicitná úprava materiálov, metrických UV a plota |
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

Na otvorenie v04 netreba internet: referencia, drevo a použité rastlinné textúry sú zabalené.
Exteriér používa `coated_pine_02`, plot `rough_wood` od Poly Haven pod CC0;
presný pôvod a SHA-256 uvádza `assets/ASSET_MANIFEST.md`. Ďalšie modely a HDRI
možno dopĺňať až pod ďalším konkrétnym grantom.
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
- V03 ponecháva kameru v02, zlepšuje drevo a vedie plot cez celé popredie.
  Zdrojové parametre a generátor sú zosúladené; porovnanie pred/po a výrezy
  sú v externom Meta celku 00/03-realistic-timber-and-foreground-fence/.
  Vegetácia, obloha, viditeľnosť krbu/komín a vnútorné priečky zostávajú témami ďalšej práce.
- Stromy a kvety vo v04 pochádzajú z evidovaných modelov; nábytok zostáva
  pôvodným vizualizačným zástupným modelom. Vizuálne prijatie je stále otvorené.
- Projekt je Git repozitár s kanonickým originom uvedeným vyššie. Lokálny commit, verejné publikovanie a prijatie sú samostatné tvrdenia, ktoré sa overujú pri konkrétnej úlohe.

## Prostredie v04 a autori

V04 pridáva 1 200 zdieľaných lesných stromov, štyri mladé smreky, jabloň s 28 plodmi, tri skupiny prednej výsadby a trsy pri plote. Zachováva dom, kameru, drevo a plot v03, pôvodný svet a svetlá. Počty a rozmiestnenie riadi `landscape_v04` v JSON; offline zdrojové zostavenie používa normalizované knižnice v `assets/models/`. Má 429 202 unikátnych zdrojových trojuholníkov; súbor scény má približne 56 MiB.

| Model | Autor | Licencia |
|---|---|---|
| [Realistic HD Norway spruce (3/43)](https://sketchfab.com/3d-models/realistic-hd-norway-spruce-343-bf500546e2874f9ea086ba6abb11357e) | PlantCatalog | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |
| [Realistic HD Black spruce (19/38)](https://sketchfab.com/3d-models/realistic-hd-black-spruce-1938-3232c3022f2947b7999de0941ede5653) | PlantCatalog | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |
| [Blossoming apple tree](https://sketchfab.com/3d-models/blossoming-apple-tree-7df0631398f443379fa4541e9efc2343) | Lassi Kaukonen (thesidekick) | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |
| [Food Apple 01](https://polyhaven.com/a/food_apple_01) | Oliver Harries | [CC0](https://polyhaven.com/license) |
| [Grass Medium 01](https://polyhaven.com/a/grass_medium_01) | Rob Tuytel, Rico Cilliers | [CC0](https://polyhaven.com/license) |
| [Shrub 01](https://polyhaven.com/a/shrub_01) | Rico Cilliers | [CC0](https://polyhaven.com/license) |
| [Periwinkle Plant](https://polyhaven.com/a/periwinkle_plant) | Amal Kumar | [CC0](https://polyhaven.com/license) |

Úpravy zahŕňajú normalizáciu mierky, statické LOD, vyčistenie zemného lemu jablone, 1K/2K mapy a úpravu shaderov. Presný rozsah a SHA-256 uvádza `assets/ASSET_MANIFEST.md`; pri šírení prilož tieto kredity aj k renderom. Čierny smrek `Picea mariana` je výslovne vybrané vizuálne aktívum, nie tvrdenie o pôvodnom druhu na Kysuciach.

Celkový vzhľad, charakter korún a ovocie posúď na finálnom rendri a výrezoch. Sivá obloha, osvetlenie a ďalšie skôr evidované témy zostávajú mimo tejto úpravy. Subjektívne prijatie vizualizácie patrí tebe.

## Priestorový pozemok v05

Zachovanú predchádzajúcu kópiu otvor v `blender/kysucka_chata_mcp_v05.blend`. Okolie tvorí
súvislý horský terén s otvoreným údolím smerom z preskleného štítu. Záhradu
s plochou 810,910 m² uzatvára pokračovanie pôvodného dreveného plota a bránka
pri predĺženom vstupnom chodníku. Približne 528 m² otvoreného trávnika zostáva
pre budúce ovocné stromy; ďalšie stromy sa teraz nepridávali.

V záhrade sú krátke 4–10 cm listy nad PBR podkladom Grass005; za plotom
a pri lesných okrajoch sú vysoké 25–65 cm lúčne skupiny. Na nerovnom podklade
sa ich časti usádzajú samostatne. Svet, svetlá, sklo, dom, vnútorné zariadenie,
drevo a pôvodný úsek plota zostali zachované. Pôvodné sklo preto naďalej
opticky rozmazáva vzdialený pohľad.

Parametre vlastní `site_v05` v JSON a spoločný generátor `scripts/site_v05.py`.
Zdrojové zostavenie aj druhé aplikovanie sa overili. Scéna má zabalené mapy
a nepotrebuje internet ani automatické spúšťanie skriptov. Seed až v04 sú
zachované. Vzhľad celej vizualizácie a navrhnutý pozemok ešte čakajú na tvoje
prijatie; nejde o zameraný pozemok ani stavebný návrh. Presné licencie a autori
zostávajú v `assets/ASSET_MANIFEST.md`.

## Pracovná stanica CachyOS a ďalšia vizuálna kvalita

Projekt sa ďalej vyvíja výhradne na počítači s CachyOS Linuxom. Michal udáva
32 GiB RAM, z ktorej ostáva približne 20 GiB voľných aj počas bežnej práce
s vývojovými nástrojmi, Blenderom a prehliadačom. Kontrola cez `nvidia-smi`
potvrdila NVIDIA GeForce RTX 3080 s 10 240 MiB VRAM; existujúci Blender 5.3.0
má povolené zariadenia Cycles CUDA aj OPTIX. Skutočné použitie GPU a spotrebu
VRAM/RAM treba pri ďalších renderoch merať, nielen odhadovať z nastavení.

Cieľ 3 GiB z plánovania v05 už nie je hardvérovou požiadavkou tohto počítača.
Viedol k výberu 1K máp Grass005, polovičnej hustote vzdialenej lúky a 32 m
lúčnym oblastiam; nebol sám osebe dôkazom kvality. Ďalšie kandidáty majú voliť
kvalitu podľa natívnych A/B renderov a skutočne nameraných zdrojov, pričom
porovnávacie snímky pred/po zostanú na rovnakom CPU/OIDN profile.

Technické uzavretie v05 nie je tvrdením o prijatí finálnej fotorealistickej
vizualizácie. V `01_closure.md` externého Meta celku je podrobný zoznam
nedostatkov pre Master Chat Orchestratora: hustejší a prirodzenejší les na
zatiaľ holých a riedkych hrebeňoch, súvislejšia lúčna pokrývka bez efektu
oddelených tmavých trsov, prirodzenejšie prehnuté listy trávnika s podkladovým
suchým stelom, ostrejšie sklo a lepší dôkaz výhľadu do diaľky, presunutie NW/SZ
review kamery mimo lesa, uzavretie malého odstupu chodníka pred bránkou,
pozorovaný odraz krbu v skle, a samostatná ďalšia práca na osvetlení, architektúre
a interiéri. Tieto zapísané potreby nie sú samy osebe novým realizačným grantom.

## V06 pred opravou lúky – zachovaný historický stav

Kandidát pred opravou lúky bol uložený ako `blender/kysucka_chata_mcp_v06.blend`. Podľa tvojho
výslovného rozhodnutia je vonkajšia krajina aj jej stromy zmenšená na polovicu.
Chata, oplotená záhrada, chodník a kamery zostali zachované; terén sa pri záhrade
pripája plynule. Pôvodná v05 aj všetky skoršie scény zostávajú zachované.

Les má súvislejší porast a nižší vzdialený hrebeň. Trávnik má hustejšie prehnuté
steblá a suchú vrstvu, lúka viac spodného aj stredného pokryvu. Výsledok je
**PARTIAL**: na lúke zostávajú pásy a stupňovité holé miesta, krátke steblá
pôsobia príliš rovnomerne, niektoré koruny sú stále riedke a stred vzdialeného hrebeňa zostáva bez lesa. Vzhľad čaká na tvoje
prijatie. Pôvodné sklo ďalej rozmazáva výhľad zvnútra; ostrá vonkajšia snímka
slúži na kontrolu krajiny spoza skla.

Uložený súbor, opakované aplikovanie a samostatné zostavenie zo zdrojov sú
overované. Zabalené aktíva a relatívne cesty fungujú bez internetu. Porovnania
pred/po používajú rovnaký CPU/OIDN režim s 96 vzorkami. Plný GPU render síce
skončil, ale nemal požadovanú rezervu VRAM; kvalita sa kvôli tomu neznižovala.
Po reštarte sa rendery a ťažké kontroly vykonávali postupne.

Natívne porovnania, štyri pohľady okolo chaty, prehľad pozemku a oba výhľady
sú v externom Meta celku `00/06-dense-forest-and-continuous-meadow/`.
Parametre vlastní `vegetation_v06` v JSON, geometriu `scripts/vegetation_v06.py`.
Nové aktíva sa nepridávali; licencie a autori zostávajú v pôvodnom manifeste.
Git sa nepublikoval a nejde o prijatý architektonický či zameraný návrh.

## V06 po oprave lúky – stav pred doplnením strmých svahov

Otvor `blender/kysucka_chata_mcp_v06.blend`. Veľké hranaté lúčne otvory sa
zacelili a nízky pohľad má prehnuté spodné listy so strednou a vyššou vrstvou.
Chata, záhrada, les, krátky trávnik, kamery aj mierka okolia 0,5 sú zachované.
Výsledok tejto opravy: **PARTIAL**. Veľké hranaté otvory sa zacelili a nízky pohľad je súvislejší. Zostávajú jemné pásy a trsovitá textúra aj veľký holý strmý svah; krátky trávnik a stred hrebeňa zostali mimo opravy.

Uloženie, zostavenie zo zdrojov, oba spôsoby opakovaného aplikovania, usadenie
rastlín a kontrolný render po otvorení z disku sú overené. Porovnania používajú
CPU/OIDN s 96 vzorkami. Pôvodný v05 záber pred úpravami zostal nezmenený;
priame porovnanie pôvodnej a opravenej v06 je v
`work/v06/final/meadow/current_after_details.png`. Správa a obrázky sú v Meta
`00/06-dense-forest-and-continuous-meadow/`. Prijatie vzhľadu zostáva tebe.

## Aktuálna v06 – nízky porast strmých svahov

Otvor `blender/kysucka_chata_mcp_v06.blend`. Holé plochy so sklonom približne
63,11° a 64,21° dostali nízky porast s kratšími stonkami; podklad rastlín aj
celé obrysy sa overujú na skutočných trojuholníkoch terénu. Pôvodná lúka,
les, krátky trávnik, chata, záhrada, kamery aj mierka okolia zostali zachované.
Výsledok tejto ohraničenej opravy: **PASS**. Oba pôvodne holé strmé svahy majú viditeľný nízky porast. Jemné pásy a trsovitá textúra lúky, uniformný krátky trávnik, nezalesnený stred hrebeňa a optické či architektonické limity zostávajú neprijaté.
Priame natívne výrezy pred/po sú v
`work/v06/final/meadow/steep_slope/native/compare_*`; úplná správa je
Meta `01_report_04.md`. Prijatie celkového vzhľadu zostáva tebe.


## Kandidát v07 – vek lesa a súvislý štrkový chodník

Aktuálny uložený kandidát je
[`blender/kysucka_chata_mcp_v07.blend`](blender/kysucka_chata_mcp_v07.blend).
Má 12 977 lesných stromov vrátane 144 doplnení hrebeňa; presne 649 náhrad má
polovičnú geometrickú mierku. Staršia trieda 378 mladých stromov sa druhýkrát
nezmenšuje. Súvislý štrkový chodník vedie od bránky až po skutočnú severnú
hranicu terénu. Krátky prechod z dlažby má strmý skosený úsek, nie bezbariérovú
podestu. Poloha chaty, bránky, pôvodnej dlažby a kamera C1 zostávajú zachované.

Parametre vlastní nová sekcia `forest_trail_v07`; geometriu a lokálne porasty
spoločný modul [`scripts/forest_trail_v07.py`](scripts/forest_trail_v07.py),
volaný builderom po v06. Zdrojový replay, opakovaná aplikácia v07 a studené
otvorenie skutočného produktu prešli. Všetkých 85 súborových obrázkov je
zabalených a má platné externé relatívne cesty. S00 až v06 a referenčný obrázok
ostávajú zachované. Dočasné dôkazy sú vo `work/v07/`; externá stopa patrí do
Meta `00/07-forest-age-variation-and-gravel-trail/`.

Vizuálne prijatie zostáva na Michalovi a orchestrátorke. Nízke vetvy v pohľade
chodca, okraje konečného terénu v celkovom zábere, pôvodný charakter lúky a
trávnika aj optické a architektonické obmedzenia zostávajú otvorené. Skoršie
sekcie v05/v06 sú historické záznamy. Tento záznam nepovoľuje ďalšiu regeneráciu.

Záverečný audit označil implementáciu v07 ako PARTIAL: cieľová šírka krajníc
0,45–0,75 m je v parametroch, ale kód ju samostatne nevynucuje. Súčasný test
pásu pôdneho shaderu používa 0,85 m a lokálna obnova porastu 1,15 m plus
hraničné náhrady. Tento bod potrebuje rozhodnutie orchestrátorky a nový grant;
overenie geometrie, opory, replayu a prenosnosti tým nie je odvolané.


### V08 – ľahšie ovládanie prírody

Aktuálny kandidát je `blender/kysucka_chata_mcp_v08.blend`; V07 zostáva zachovaná.
Les má 9 733 stromov s výškami 1,00–8,32 m a hornou hranicou 9 m.
Pracovné Solid zobrazenie používa jednoduché predlohy; úplný oblet dosahuje
42.9 FPS pri 2840 × 1208. Finálny render má približne polovičnú geometrickú
náročnosť vegetácie. Chata a jej detaily ostali zachované.
Výsledky, porovnania, diagnostika po HW resete a otvorené limity sú v
[prehľade V08](docs/V08_VEGETATION.md). Vizuálne prijatie zostáva otvorené.

Voliteľný `blender/kysucka_chata_mcp_v08_view.blend` nahrádza iba hrubé pracovné
koruny vernejšími odvodenými vetvami a ihličím; pôvodná V08 a jej render zostávajú.
Má zmeraných 41,8 FPS v Solid a 16,7 FPS v krátkom Material Preview teste.
[Hotový render chaty](previews/v08/after_C1.png) môžeš otvoriť priamo;
postup F12/F11 a rozdiel oproti pracovnej vetve sú v tom istom prehľade.

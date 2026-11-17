# Lokálna práca s Blenderom

Projektová prevádzková projekcia. Aktuálne povolenie poskytuje iba konkrétny
prompt. Nasledujúce príkazy sú možnosti nástroja, nie trvalé povolenie úprav.

## Read-only local inspection

Identita schopnostnej cesty: blender-local-v1. Aktuálny grant ju aktivuje ako kanonickú cestu lokálneho pozorovania; nevyžaduje MCP.

1. Over fyzický Git koreň pomocou git rev-parse --show-toplevel, kanonický
   origin https://github.com/cisarik/kysucka_moderna_chata, presný commit
   uvedený aktuálnym grantom a povolený stav indexu/pracovného stromu.
   Inicializačný baseline je bc510eb063f96d7cedad49aaaca6f58b54a51fd2;
   ďalšie granty musia pomenovať svoj aktuálny presný baseline.
2. Pred otvorením scény over presnú vstupnú cestu a príslušné zdrojové
   SHA-256 z AGENTS.md alebo aktuálneho grantu. Historické inventáre
   manifest/*.sha256 nie sú aktuálnou identitnou bránou.
3. Nájsť Blender bez inštalácie: pozorovaný program `blender` v PATH alebo
   existujúci macOS program `/Applications/Blender.app/Contents/MacOS/Blender`.
4. Zavolať jeho `--version`. Potom sa dá iba čítať scéna takto, so skutočnými
   absolútnymi cestami dosadenými zo zisteného koreňa:

```text
<observed-blender> --background --disable-autoexec <ROOT>/blender/kysucka_chata_seed.blend --python-exit-code 2 --python <ROOT>/scripts/inspect_scene.py
```

Skript vypisuje pozorovania do stdout, neukladá a nerenderuje. Overiť metre,
kameru, rozlíšenie, zabalený obrázok a počty objektov. Ak Blender nie je
dostupný, Planner uvedie presnú prekážku a plán; neinštaluje ho.
Lokálne GUI otvorenie môže potvrdiť Michal. Fotografia otvoreného okna sama
nepotvrdzuje dostupnosť CLI alebo MCP nástroja Workera.

Inštalovaný Blender môže mať vlastný vstavaný handler. Pri skúške 4.3.2 bol
rovnaký handler `pose_library.gui._on_blendfile_load_post` prítomný aj v čistej
factory scéne. Samotný počet 1 preto nie je projektový auto-run. S00 má nulové
automatické textové moduly a nulové objektové drivery; zdroj sa porovnal s čistým
spustením. Pri inom lokálnom náleze treba pôvod overiť, nie ho ignorovať.

Pozorovanie 14. 11. 2026: deklarovaná read-only kontrola seedu úspešne
dobehla v /Applications/Blender.app/Contents/MacOS/Blender, verzia 5.2.3 LTS.
Pôvod seedu ostáva Blender 4.3.2. Proces pri štarte vypísal registráciu
existujúceho BlenderMCP add-onu; load_post=3, save_pre=0, render_pre=0.
Pôvod handlerov tento skript neurčuje. Historický počet 1 sa nepovažuje
za aktuálne overenie. Doplnky sa neinštalovali ani neupravovali.
Engine, zariadenie a nový render neboli touto kontrolou overené.

## Živé ovládanie cez MCP — v01, v02 a aktuálna v03

Cesta `blender-mcp-live-v1` je konkrétnym grantom aktivovaná výnimka pre celok
`kysucka-moderna-chata-blender-mcp-first-reference-render`. Používa existujúce
MCP spojenie s otvoreným Blenderom 5.2.3 LTS. `blender-local-v1` zostáva cestou
lokálnej kontroly vrátane čítania uloženej pracovnej kópie v samostatnom procese.
Opis cesty sám neposkytuje povolenie ďalších úprav ani inštalácie doplnkov.

1. Pred zmenou over Git koreň, origin, baseline, povolený stav a príslušné hashe;
   cez MCP prečítaj presnú otvorenú cestu, neuložený stav, aktívny objekt a režim.
2. Pred opustením Edit režimu ulož skutočný živý stav pomocou
   `save_as_mainfile(copy=True, compress=True)` do grantom pomenovaného checkpointu.
   V01 používa `work/mcp-v01-owner-checkpoint.blend`; over uloženie a hash seedu.
3. Prejdi do Object režimu, over zachovanie rozpracovanej geometrie a ulož aktívnu
   kópiu `blender/kysucka_chata_mcp_v01.blend`. Pred korekciou bol samostatne
   uložený `work/mcp-v01-before.blend`. Existujúce checkpointy neprepisuj.
4. Porovnanie pred/po používa Cycles CPU, 640 × 480 a 32 vzoriek. Jediná zmena
   obrazu je `CAM_A_REFERENCE.data.shift_y`: `0.17 → 0.075`; hodnotu potvrdilo
   samostatné MCP čítanie. Snímky a presné príkazy sú v externom Meta celku
   `projects/kysucka_moderna_chata/00/01-blender-mcp-first-reference-render/`.
5. Uložená pracovná kópia má kanonických 1448 × 1086, 96 vzoriek a výstup
   `//../work/camera_a.png`. GUI je v kamerovom režime Cycles so svetlami a svetom
   scény; interaktívny náhľad má 16 vzoriek. Pri kontrole z disku nič neukladaj.

Zdroj `model/parameters.json` obsahuje rovnaký posun kamery. Generátor ho už
číta; živá scéna sa týmto krokom neprestavuje. Pred neskoršou regeneráciou treba
zosúladiť prijatú verziu scény a zdrojov. V01 je pracovný kandidát na vizuálne prijatie.

Pre celok `kysucka-moderna-chata-reference-camera-perspective` konkrétny
realizačný grant znovu aktivoval `blender-mcp-live-v1`. Z nezmenenej v01
sa porovnali tri kamery pri Cycles CPU, 640 × 480 a 32 vzorkách.
Výsledná pracovná scéna bola `blender/kysucka_chata_mcp_v02.blend`: kamera
`CAM_A_REFERENCE` má polohu `[21.5, -10.0, 1.25]`, cieľ `[8.5, 2.5, 1.25]`,
ohnisko 35 mm, snímač 36 mm, shift_x = 0 a shift_y = 0.105. JSON obsahuje
rovnaké hodnoty; orientáciu už počíta existujúci generátor. Geometria,
materiály, sklo, svet, svetlá aj krajina zostali zachované, rovnako seed a v01.
Kontrolný bod pred zmenou kamery je `work/mcp-v02-before.blend` s malým
porovnávacím rozlíšením. V02 má obnovených 1448 × 1086, 96 vzoriek a výstup
`//../work/camera_a.png`; živý pohľad Layout je CAMERA + RENDERED so svetlami
a svetom scény a 16 vzorkami náhľadu. Samostatné otvorenie bez okna používa
Solid; kameru a uložené renderovacie nastavenia overuje bez renderovania.
Rendery a merania sú v externom Meta celku `00/02-reference-camera-perspective/`.
Vizuálne prijatie zostáva otvorené. Tento opis neudeľuje ďalšie oprávnenie úprav.

## V03 — PBR drevo a plot v popredí

Konkrétny grant celku `kysucka-moderna-chata-realistic-timber-and-foreground-fence`
aktivoval `blender-mcp-live-v1` pre úpravu dreva a plota. Aktuálny súbor je
`blender/kysucka_chata_mcp_v03.blend`; kamera zostáva totožná s v02.

- `MAT_TIMBER_EXTERIOR` používa `coated_pine_02` na 89 exteriérových objektoch;
  `MAT_TIMBER_FENCE` používa `rough_wood` na 26 stĺpikoch a dvoch priečkach.
  Pôvodné materiály zostali zachované na nábytku, stromoch a dekorácii.
- Šesť CC0 JPG má 2K rozlíšenie; pôvod, smer vlákien, mierku a kontrolné súčty
  uvádza `assets/ASSET_MANIFEST.md`. V03 obsahuje zabalené mapy aj referenciu,
  pričom zachováva cesty `//../assets/textures/wood/...`.
- `model/parameters.json` obsahuje `exterior_timber`, `fence_timber` a
  `foreground_fence`. Funkcia `apply_v03` v `scripts/timber_fence_v03.py` vykoná
  rovnakú úpravu cez MCP aj zo zdrojového generátora a nemení globálny RNG.
  Pôvodných 26 náhodných ťahov starého plota zostáva pred tvorbou stromov.
- Plot vedie z `(16.60,-8.62)` do `(18.25,1.00)`; nohy sú zapustené do terénu.
  Zvolený prvý variant pretína celý spodný okraj záberu bez zmeny terénu či kamery.
- Porovnanie pred/po používa 1448 × 1086, 100 %, Cycles CPU, 96 vzoriek,
  OpenImageDenoise zapnuté, snímku/seed 0, AgX/None, expozíciu 0 a gamma 1.
  Rovnaké nastavenie v03 zostáva uložené; výstup je `//../work/camera_a.png`.
  Layout má CAMERA + RENDERED, svetlá/svet scény a 16 vzoriek náhľadu.
- Kontrolný bod je `work/mcp-v03-before.blend`; overenie zdrojov vytvára iba
  `work/v03_source_replay.blend` v oddelenom CLI procese. Pri budúcom opakovaní
  treba nové konkrétne povolenie aj kontrolu kolízií výstupov.

`configure_comparison_render` v rovnakom module nastavuje profil v03.
Starší `scripts/render_scene.py` ponecháva odšumovanie vypnuté, a preto neslúži
na toto porovnanie. Príkaz na cold kontrolu používa existujúci Blender s
`--background --disable-autoexec` a `scripts/inspect_scene.py`; nič neukladá.
Zdrojové zostavenie používa `scripts/build_scene.py -- --output <nový-pracovný-súbor>`.
Rendery, výrezy a technické overenia patria do externého Meta celku `00/03-realistic-timber-and-foreground-fence/`.

## Zostavenie a render - iba s budúcim povolením

Zdrojové skripty nevyžadujú add-on. `bpy` dodáva Blender; netreba `pip install bpy`.
Príkazy musia bežať v samostatnom procese, aby sa vyhla strata neuloženej GUI scény.

```text
<observed-blender> --background --factory-startup --python-exit-code 2 --python <ROOT>/scripts/build_scene.py -- --output <ROOT>/work/rebuild.blend
<observed-blender> --background --disable-autoexec <ROOT>/work/rebuild.blend --python-exit-code 2 --python <ROOT>/scripts/render_scene.py -- --output <ROOT>/work/camera_a_preview.png --width 960 --samples 64
```

Fish spúšťače v tools/ používajú rovnakú cestu, odmietnu existujúci výstup
a nič neinštalujú. Nemajú oprávnenie samy od seba meniť seed.

## Bežné otvorenie bez terminálu

V Blenderi: File → Open → `blender/kysucka_chata_mcp_v04.blend`. Zachované sú
v02, v01 a seed `blender/kysucka_chata_seed.blend`.
V03 má nastavený kamerový pohľad Cycles
so svetlami a svetom scény. Na notebooku možno použiť View → Cameras → Active Camera.
F12 spustí render; pri dodanom rozlíšení môže na CPU trvať výrazne dlhšie
než malý náhľad. Režim Solid je vhodný na rýchlu geometriu, Material Preview
na materiály. Referencia je zabalená v dátach obrázkov ako
REF_kysucka_chata_moderna; nie je súčasťou vyrenderovaného obrazu.

Blender GUI nenačíta automaticky zmeny uložené externým Workerom. Pred novým
načítaním treba zachovať neuložené ručné zmeny. Nepracovať súčasne ručne aj
Workerom na tom istom .blend. Každý prijatý výsledok má konkrétny súbor a hash.

## Výkon a prenosnosť

Seed vznikol v Blenderi 4.3.2; jeho historický testovací build nemal OpenImageDenoise.
Aktuálna v03 používa Blender 5.2.3 LTS a zapnuté OpenImageDenoise na CPU.
Oficiálny lokálny Blender môže ponúkať Metal alebo CUDA/OptiX; musí sa to
overiť v Preferences → System. Nezamieňať nastavenie s reálne použitým zariadením.
V03 má porovnávací profil CPU, 1448 × 1086 a 96 vzoriek; celkové vizuálne prijatie zostáva otvorené.

## PDF / CAD regenerácia

`scripts/build_documents.py` používa reportlab, ezdxf, Pillow a DejaVu Sans.
Zapisuje PDF, DXF, SVG a computed_metrics.json; nie je to read-only kontrola.
Závislosti uvádza requirements-docs.txt. Prvý Planner ich neinštaluje.
DXF je R2013 v milimetroch; Blender je v metroch. SVG a PDF majú spoločnú
2D geometriu. Kóty v DXF sú neasociatívny text a čiary, nie výrobná dokumentácia.

## V04 — kopce, les a prirodzená záhrada

Aktuálny kandidát je `blender/kysucka_chata_mcp_v04.blend`. Zachované sú seed,
v01, v02 aj kanonická v03. Grant 01/03 osobitne povolil zachovať Michalovo
uloženie pohľadu v kontrolnom bode `work/mcp-v04-before.blend` a obnoviť v03
na jej prijaté bajty. Ďalšie uloženia scény smerovali iba do v04.

`scripts/landscape_v04.py` nemá účinky pri importe ani sieťové požiadavky.
`apply_v04(scene, P, ROOT)` používa lokálny RNG 13704, normalizované knižnice
zo `landscape_v04.assets` a zdieľané siete. Zo zdrojového generátora sa volá
hneď po `apply_v03`; v živej v03 sa opakuje iba v04. Druhé volanie nevytvára
ďalšie objekty, materiály ani textúry. Zdrojové master kolekcie mimo scény a
pôvodné materiály trávy/zeminy majú fake user, aby sa zachovali po uložení.

V04 obsahuje 79 zabalených súborových obrázkov vrátane referencie a dreva.
Rastlinné mapy majú relatívne cesty `//../assets/models/.../textures/...`.
Knižnice a ich kontrolné súčty vlastní `assets/ASSET_MANIFEST.md`. Zostavenie
nepotrebuje pôvodné archívy ani internet. Nepovoľuje auto-run alebo inštaláciu.

Cold kontrola používa existujúci Blender s `--background --disable-autoexec`.
Overenie zdrojov používa `--background --factory-startup --disable-autoexec`
a `scripts/build_scene.py -- --output <nový-grantom-povolený-súbor>`.
Tento beh vytvoril iba dočasnú `work/v04_source_replay.blend`; pred opakovaním
treba nový grant a preverenie kolízií. Porovnávajú sa objekty, transformácie,
siete, UV, priradenia materiálov, inštancie a zabalené obrázky; nie UI cache
ani úplný zoznam predvolených RNA hodnôt medzi verziami Blenderu.

Výstupný profil zostáva 1448 × 1086, Cycles CPU, 8 vlákien, 96 vzoriek,
OpenImageDenoise, snímka/seed 0, AgX/None, expozícia 0 a gamma 1.
Pred/po, výrezy bez zmeny mierky a technické dôkazy patria do externého
Meta celku `00/04-kysuce-forest-and-natural-garden/`. Jeho `render_metadata.json`
vyžaduje explicitné vynútené zaradenie Cooperatorom podľa Meta ignore pravidiel.
Celkové vizuálne prijatie zostáva otvorené; tento opis neudeľuje ďalšiu autoritu.

## V05 — súvislý pozemok, údolie, plot a tráva

Aktuálna pracovná kópia je `blender/kysucka_chata_mcp_v05.blend`. Tento celok
použil existujúci Linux Blender 5.3.0 na `/home/agile/Applications/Blender/blender`
a výslovne obnovenú cestu `blender-mcp-live-v1`. Historické macOS pozorovania
vyššie sa nemenia. Tento opis neposkytuje ďalší realizačný grant.

Kontrolný bod `work/mcp-v05-before.blend` zachováva pôvodný živý stav v04.
V04 sa neprepisovala. Funkcia `apply_v05(scene, P, ROOT)` sa v zdrojovom
generátore volá po v03/v04; v živej v04 sa použila iba v05. Import nemá
vedľajšie účinky a funkcia nemení globálny RNG. Druhé aplikovanie má nulový
sémantický posun. Vlastnené V05 dáta a off-scene masters sa opakovane používajú.

Terén používa jednu triangulovanú výškovú funkciu, presne vloženú hranicu
záhrady a zhodné normály švu. Zachováva 126 pôvodných vrcholov chránenej
terasy. Trávnik používa 8 × 8 m oblasti a lúka 32 × 32 m oblasti pre nižšiu réžiu; pri odchýlke podkladu
nad 10 mm sa lúčne skupiny rozložia na zdieľané časti a usadia samostatne.
Kontrola vyhodnocuje skutočné pätky a premietnuté obrysy, nielen stredy skupín.
Hustota vzdialenej lúky je z rozpočtových dôvodov znížená na polovicu; blízka zostáva zachovaná.

Oddelené procesy overili otvorenie z disku a zostavenie:

```text
/home/agile/Applications/Blender/blender --background --factory-startup --disable-autoexec <ROOT>/blender/kysucka_chata_mcp_v05.blend --python-exit-code 2 --python <ROOT>/work/v05_cold_verify.py -- cold
/home/agile/Applications/Blender/blender --background --factory-startup --disable-autoexec --python-exit-code 2 --python <ROOT>/scripts/build_scene.py -- --output <ROOT>/work/v05_source_replay.blend
```

Dočasné overovacie skripty a replay patria do `work/`; budúce opakovanie potrebuje
nový grant a kontrolu kolízií. Porovnanie nahrádza lokalizované názvy uzlov ich
indexmi v grafe. `Subsurface Scale` sa sémanticky neporovnáva len pri
neprepojenej nulovej váhe podpovrchového rozptylu; jeho rozdiel 0,05/0,005
pochádza zo staršieho uloženého defaultu. Aktívne shaderové hodnoty sa porovnávajú
s toleranciou 1e-6. U skrytých zachovaných trsov sa overujú uložené lokálne
transformácie, pretože runtime svetová matica sa po načítaní nemusí aktualizovať.
Žiadny pôvodný materiál sa kvôli porovnaniu neupravuje.

C1 má nezmenené ohnisko, transformáciu, posuny a clip_end 500 m. Finálny súbor
obnovuje C1, 1448 × 1086, Cycles CPU, 8 vlákien, 96 vzoriek, OIDN, snímku/seed 0
a AgX/None. Pomocné kamery a natívne výrezy dokladajú záhradu, údolie, orbit
a obidva typy trávy. Súbory sú v externom Meta celku
`00/05-spatial-site-valley-and-grass/`. Jeho `renders/render_metadata.json`
vyžaduje pri Michalovom archivovaní explicitné vynútené zaradenie; Meta Git
sa v tomto grante nemenil.

Overené SHA-256 tejto verzie:

| Súbor | SHA-256 |
|---|---|
| `model/parameters.json` | `66ed4d7246ca211a55d3067a4b14f50e8af706efc669c4dd4911c7c0c1d2d664` |
| `scripts/build_scene.py` | `9c7863c125c74f2894529ad247f8d5eb8f9b756f3f1af26dd8be094ebd7a8c6b` |
| `scripts/site_v05.py` | `f6f122dbacb293bb8a90f748583555516c8d57344112c47a62eba172afb821aa` |
| `blender/kysucka_chata_mcp_v05.blend` | `c3bd3d5e847c52d33a60f3f89cf4392da85a24df96fe7774a25a37bd39d8fafe` |

## CachyOS hardvér a odstránenie nesprávneho 3 GiB stropu pre ďalšiu prácu

Projekt sa vyvíja výhradne na CachyOS Linuxe. Michal hlási 32 GiB RAM, z ktorej
zostáva približne 20 GiB dostupných aj s bežiacimi vývojovými nástrojmi,
Blenderom a prehliadačom. Priama kontrola `nvidia-smi` (16. 11. 2026) potvrdila
`NVIDIA GeForce RTX 3080`, `10240 MiB` VRAM, ovládač `620.70.06` a práve
približne 4.43 GiB obsadenej VRAM desktopom a ďalšími procesmi. V tom istom
čase dlhodobo otvorený Blender proces používal približne 2.99 GiB VRAM.
V Blenderi 5.3.0 sú cez MCP priamo overené zariadenia `NVIDIA GeForce RTX 3080`
typu `OPTIX` aj `CUDA` s `use = True`, CPU v zozname s `use = False`. To potvrdzuje
dostupnosť/UI preferencie zariadení, nie automaticky získanie vyššej kvality
alebo skutočné použitie GPU v každom budúcom renderi.

Pôvodný cieľ `< 3 GiB` RSS uviazaný na predchádzajúci 8 GiB M1 nie je aktuálnou
technickou požiadavkou tohto PC. Pri v05 viedol k dobrovoľne zvolenej 1K verzii
Grass005, polovičnej vzdialenej hustote lúky a zväčšeniu lúčnych sektorov na
32 m. Zachovaná v05 zostáva nezmenená; ďalší grant má prehodnotiť tieto
kompromisy podľa skutočných meraní, nie automaticky prepínať na 2K alebo
vyššiu hustotu. Porovnávací zdroj v05 zostáva nezmenený a používa Cycles CPU s OIDN.

Pre ďalšie kandidáty sa má merať samostatne:
- svieži CLI proces verzus teplé GUI s alokačnou históriou,
- systémová RAM a VRAM počas skutočného renderu,
- CPU/OPTIX/CUDA časy, nastavenie a skutočné použitie,
- natívna 1 : 1 vizuálna kvalita krátkeho trávnika, hustota lúky a hustota lesa.

Práca v `01_closure.md` externého Meta celku `00/05-spatial-site-valley-and-grass`
obsahuje aj úplný registrovaný vizuálny nedostatkový prehľad. Zvlášť treba preveriť
viac a vrstvenejšie stromy na zatiaľ holom hrebeni za údolím a riedkom lesnom
okolí, súvislejšiu lúku, prirodzenejšie prehnutie/morfologické 3D listy trávnika,
ostrejšie sklo, novú SZ pozíciu review kamery mimo lesa, pristávacia betónová
plocha pred bránkou (medzery asi 18–22 cm sa tento grant dotýkať nemal) a ostatné
architektonické, materiálové a interiérové odchýlky od referencie. Uzavretie
technického v05 celku teda nevyhlasuje hotovú profesionálnu vizualizáciu ani
neoslovuje ďalšie úpravy bez nového grantu.

## V06 pred opravou lúky – historické overenie

Kandidát pred opravou lúky: `blender/kysucka_chata_mcp_v06.blend`, Blender 5.3.0.
Zdrojom je `vegetation_v06` v parametroch a `scripts/vegetation_v06.py`, volaný
po zachovaných v03/v04/v05 krokoch. Michal výslovne schválil mierku 0,5 pre
vonkajšiu krajinu a stromy so zachovaním chaty, záhrady, chodníka a kamier.
Pevné jadro je `[-15,5;19,2] × [-10;16,5] m`; výška sa pripája počas 8 m.
Pôvodné siete terénu ostávajú skryté a zachované, aktívne siete sú kópie v06.
Lúka sa vzorkuje nanovo s prirodzenými veľkosťami stebiel. Pôvodný vonkajší
mladý smrek 03 ostáva zachovaný skrytý a má zdieľanú polovičnú náhradu.

Plný výsledok: 12 833 stromových umiestnení, 6 793 trávnikových a 1 134 737
lúčnych záplat. Kontrola skutočných kotiev a celých premietnutých obrysov
prešla; všetky korene predlôh sú obsiahnuté v overovaných transformovaných
obálkach oproti každej pretínanej trojuholníkovej ploche terénu. Kontrolu
dopĺňajú priame koreňové lúče na dvoch umiestneniach každej použitej predlohy.
Odmietnutých je 2 973 drobných buniek s plochou 11,6133 m². Dve plné aplikácie,
opätovné otvorenie a zdrojové zostavenie sa sémanticky zhodujú v toleranciách
0,1 mm pre polohu a 1e-6 pre ostatné čísla. Staršie parametre/moduly, pôvodné
terénne údaje, architektúra a materiály mimo povolených zásahov ostali zachované.

Profil je P0: Cycles CPU, 8 vlákien, 96 vzoriek, CPU OIDN Accurate/High,
adaptívny prah 0,01/minimum 0, snímka/seed 0, AgX/None, expozícia 0/gama 1.
C1 je aktívna, 1448 × 1086/100 %, s nezmenenou optikou. Plný OPTIX render
skončil úspešne, ale minimum voľnej VRAM bolo 159 MiB, pod rezervou približne
1 GiB. Preto oficiálne páry používajú nový v05 CPU základ aj v06 CPU výsledok.
Po oznámenom páde a reštarte sa GPU pokus neopakoval; SOLID viewport a postupné
vykonávanie renderov a ťažkých kontrol obmedzili súbeh. Príčina pádu nie je
preukázaná. Preferencie sa na disk neukladali; pri nahradení vlastnej pracovnej
kópie bol počet záložných verzií dočasne nastavený na nulu a ihneď vrátený.

Existujúca trasa `blender-mcp-live-v1` slúžila na živé úpravy a uloženie;
oddelené procesy `/home/agile/Applications/Blender/blender` s factory-startup/
disable-autoexec overili zdrojové zostavenie a studený render C1. Podklady sú
v `work/v06/final/`; `work/v06_source_replay.blend` je dočasný dôkaz. Toto
zdokumentovanie neudeľuje ďalší grant na spúšťanie ani prepis výstupov.

Natívne PNG a logy zostávajú v `work/v06/final/native/`, úplná proveniencia,
teplé/studené merania a SHA-256 v Meta `00/06-dense-forest-and-continuous-meadow/`.
Hárky nepoužívajú prevzorkovanie ani opravu obrazu. Pohľad zvnútra zachováva
pôvodné rozmazávajúce sklo; vonkajší diagnostický záber je spoza neho.
Výsledok zostáva vizuálne PARTIAL pre pásy/holé miesta lúky, uniformitu krátkych
stebiel, časť riedkych korún a nezalesnený stred vzdialeného hrebeňa. Nedokladá prijatie finálneho vzhľadu ani stavby.
Meta JSON musí Michal pri archivovaní zaradiť výslovne napriek ignorovaniu.
Git sa v tomto grante nemenil a nič sa nepublikovalo.

Overené SHA-256 v06 (skoršie tabuľky zostávajú historické):

| Súbor | SHA-256 |
|---|---|
| `model/parameters.json` | `58a6886c917e59d233d2cd5abcf711f334f73a9ef3f340f4a5c8bde7983d507a` |
| `scripts/build_scene.py` | `2abb505c6665eb7e215557a1681f6fc7bc72e4d2949493c275cd16c261473f6a` |
| `scripts/vegetation_v06.py` | `4bfce5ea56de33fdc737e31c1cfafe8cb82cc460d998c98711d234c7860e3ea9` |
| `blender/kysucka_chata_mcp_v06.blend` | `fff6f16e373aa94c20902f9cd9880f62a2569981ce5b68d2396222258626cc63` |

## Oprava lúky v06 – historický stav pred strmými svahmi

Parametre vlastní `vegetation_v06.meadow`; spoločný
`scripts/vegetation_v06.py::apply_meadow_v06` používa aj normálny `apply_v06`.
Kamera, svetlá, les, trávnik, terén a spoločné materiály sú s predchádzajúcou
v06 sémanticky zhodné. Generátor pri prvom uložení prevádza cesty obrázkov podľa
skutočného výstupného adresára; hlboký replay má preto platné relatívne cesty.

Uložený súbor má 158,453,381 bajtov (151.11 MiB). Staršia
hranica 90 MiB sa nevynucovala stenčením porastu ani realizovaním inštancií.
Zostavenie a oba testy opakovania používajú samostatný Blender 5.3.0 s výrobným nastavením a vypnutým automatickým spúšťaním skriptov; ťažké procesy a P0 CPU/OIDN/96 rendery bežia postupne.
Po prerušení procesu sa dokončená geometria obnovila z presných polí; všetkých
42 700 156 porovnávaných hodnôt bolo zhodných. Obrazový editor nahradil aktívny
3D viewport, scéna sa neskryla a preferencie sa nemenili. Pred uložením novej
kanonickej verzie sa pôvodné bajty odložili do povolenej pracovnej cesty, takže
nevznikla vedľajšia .blend1 a netrebalo meniť počet záloh v preferenciách.

Stav je **PARTIAL**: Veľké hranaté otvory sa zacelili a nízky pohľad je súvislejší. Zostávajú jemné pásy a trsovitá textúra aj veľký holý strmý svah; krátky trávnik a stred hrebeňa zostali mimo opravy.
Pôvodná v06 a jej obrázky/metadáta sú v `work/v06/final/pre-meadow/` a bajtovom
`pre_meadow_correction.blend`; nové dôkazy v `work/v06/final/meadow/`.
Predlohy, všetky skutočné korene/kotvy a premietnuté obrysy sú overené, s limitmi
1 mm vyčnievania a 20 mm zanorenia. Pri archivácii musí Michal výslovne pridať
ignorovaný Meta JSON. História ani index Git sa nemenili; nič sa nepublikovalo.

## Aktuálna v06 – podpora porastu na strmých svahoch

Jediná zmena je `vegetation_v06.meadow.steep_slope` a jej spoločné spracovanie
v `apply_meadow_v06`. Namerané sklony 64,214° a 63,107° boli nad starým
limitom 60°. Nová trieda siaha do 68° a celú premietnutú plochu overuje na
pretínaných trojuholníkoch. Dvanásť doplnkových predlôh má výšku 0,4 pôvodnej;
3,869,907 starých umiestnení aj ich predlohy sú presne zachované.
Nových skupín je 15,194; celá lúka má 3,885,101.
Kanonický súbor má 159,992,657 bajtov (152.58 MiB).
Pracovný súbor sa uložil hneď po mutácii pred ťažkými kontrolami; pôvodný stav
je bajtovo v `work/v06/final/meadow/pre_steep_slope_correction.blend`.
Nové skripty, replay, natívne snímky, merania a zachované podklady patria do
`work/v06/final/meadow/steep_slope/`. Ťažké procesy boli postupné, P0 CPU/OIDN/96.
Stav: **PASS**. Oba pôvodne holé strmé svahy majú viditeľný nízky porast. Jemné pásy a trsovitá textúra lúky, uniformný krátky trávnik, nezalesnený stred hrebeňa a optické či architektonické limity zostávajú neprijaté.
Správa `01_report_04.md` uvádza skutočné výstupné kódy a teplé/studené merania.
Spravovaný AP blok aj celá sekcia Closure and Git gates zostali bez zmeny.
Pri archivovaní musí Michal výslovne zaradiť ignorovaný Meta JSON; staging ani
publikovanie sa nevykonali. Tento opis neudeľuje ďalší grant.


## V07 – vek lesa a štrkový chodník

Aktuálny kandidát: `blender/kysucka_chata_mcp_v07.blend`, existujúci Linux
Blender 5.3.0 v `/home/agile/Applications/Blender/blender`. Grant
FOREST-TRAIL-V07-IMPL obnovil `blender-mcp-live-v1` pre vlastné vrstvy v07,
checkpointy a uloženie produktu. `blender-local-v1` v oddelených procesoch
overil replay a studené otvorenie; žiadne preferencie, ovládače ani doplnky sa
nemenili. Tento záznam nie je oprávnením na budúce spustenie alebo publikovanie.

Builder volá `apply_v07(scene, P, ROOT, *, components=None)` po nezmenených
v03/v04/v05/v06. Sekcia `forest_trail_v07` je jediná nová sekcia parametrov;
modul používa izolovaný seed 13707 a nemenné záznamy v06. Natívny register
`V07_FOREST_REGISTRY.json` uchováva všetky pôvodné a výsledné transformácie.
Pôvodné vrstvy terénu a lesa zostávajú skryté a nezmenené. Vlastné normály
terénu používajú natívne vektorové dáta CORNER, aby sa mimo koridoru zachovali
presne. Štrk je uzavretý, jeho spodok je 2 mm v teréne a horná plocha 15 mm nad
ním; prechod pod zatvorenou bránkou necháva približne 5 mm svetlosti. Skosenie
má 27,55–35,13° a nepredstavuje bezbariérovú podestu.

`work/v07/checks/source_replay.py` spustil jediný normálny builder do
`work/v07/replay/source.blend`; v tom istom procese potom vynútil všetkých päť
častí v07 bez druhej aplikácie v06. Opakované použitie nemení transformácie,
geometriu, masky ani globálny RNG. Studené porovnanie uložených súborov je
presné. Rozdiely poradia uzlov šiestich svetiel boli porovnané podľa úplných
uzlov, spojení a fyzických parametrov; svetlá sa neupravovali. Nepoužitá lawn
skupina bez používateľov sa v uložených súboroch prirodzene neuchováva.

P0 zostáva CPU / 8 vlákien / 96 vzoriek / OIDN Accurate High, AgX/None,
frame/seed 0, expozícia 0 a gamma 1. C1 má 1448 × 1086. Ťažké procesy sú
postupné, každý začína pri aspoň 12 GiB dostupnej RAM a má guard pod 3 GiB počas
troch sekundových vzoriek. Záznamy v `work/v07/checks/` obsahujú skutočné návratové
kódy, časy, RSS, dostupnú RAM a spoločnú obsadenosť VRAM. Žiadny GPU/P1 pokus
neprebehol. `work/` a replay sú dočasná evidencia; neskoršie opakovanie potrebuje
nový grant a novú výstupnú cestu. Manuálne úpravy `.blend` sa do zdrojov nevracajú.

Otvorený implementačný bod z posledného auditu: `route.shoulder_width_m`
[0,45;0,75] m zatiaľ nemá vlastné vynútenie. Shaderový pás testuje vzdialenosť
0,85 m a lokálna obnova porastu siaha do 1,15 m plus náhrady hraničných trsov.
Tieto obnovné zóny nemožno bez samostatného dôkazu označiť za splnenie cieľovej
šírky krajnice. Stav je PARTIAL; ďalšia oprava vyžaduje nový grant, pretože
povolená jedna sústredená oprava už bola využitá.


### V08 – pracovné a renderové zobrazenie

Nový kandidát `blender/kysucka_chata_mcp_v08.blend` sa otvára v Solid režime.
Uzol Is Viewport automaticky vyberá ľahkú vetvu pri práci; finálny render používa
odvodené podrobnejšie predlohy. Zdrojom je `vegetation_v08` v JSON a
`scripts/vegetation_v08.py::apply_v08`, po V07 kroku buildera.
Staršie generátory sa pri bežnej práci s kandidátom nespúšťajú.
Po HW resete je pôvodný plný Material Preview považovaný za neúspešný test;
overovanie nového náhľadu používa výlučne ľahkú vetvu, oddelene od CPU renderov.
Samostatné procesy používajú `/home/agile/Applications/Blender/blender`,
`--background --disable-autoexec`, CPU/8 vlákien a externé meranie dostupnej RAM.
Žiadne ovládače ani uložené preferencie sa nemenili.
Podrobnosti: [V08](V08_VEGETATION.md); checkpointy/logy `work/v08/` sú dočasné dôkazy.

Samostatný pracovný variant je `blender/kysucka_chata_mcp_v08_view.blend`.
`vegetation_v08.forest.viewport_model = source_branches` zmení iba päť
pracovných predlôh; podrobná renderová vetva zostáva zhodná s V08.
Material Preview tiež vyhodnocuje pracovnú vetvu. Skutočný render spúšťa F12;
F11 zobrazí dostupný posledný výsledok. Hotové PNG sú v `previews/v08/`.
Pri poslednom obnovení bol ponechaný Image Editor s C1; kontrolný obrázok
nebol uložený ako nová scéna ani pridaný do pôvodných 85 zabalených máp.

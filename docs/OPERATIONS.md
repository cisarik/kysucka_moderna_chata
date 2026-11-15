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

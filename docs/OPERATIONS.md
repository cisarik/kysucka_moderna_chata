# Lokálna práca s Blenderom

Projektová prevádzková projekcia. Aktuálne povolenie poskytuje iba konkrétny
prompt. Nasledujúce príkazy sú možnosti nástroja, nie trvalé povolenie úprav.

## Read-only local inspection

Identita schopnostnej cesty: **blender-local-v1**. Prvý Planner ju musí použiť
ako kanonickú cestu lokálneho pozorovania, ak je dostupná. Nevyžaduje MCP.

1. Pracovný koreň je priečinok otvorený v Cursori, ktorý obsahuje AGENTS.md,
   model/parameters.json a manifest/seed_files.sha256. Overiť fyzickú cestu.
2. Overiť manifest iba čítaním štandardnou knižnicou Python; nevytvárať cache.
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

V Blenderi: File → Open → `blender/kysucka_chata_seed.blend`. Kamera je nastavená
ako aktívna. Na notebooku možno použiť View → Cameras → Active Camera.
F12 spustí render; pri dodanom rozlíšení môže na CPU trvať výrazne dlhšie
než malý náhľad. Režim Solid je vhodný na rýchlu geometriu, Material Preview
na materiály. Referencia je zabalená v dátach obrázkov ako
REF_kysucka_chata_moderna; nie je súčasťou vyrenderovaného obrazu.

Blender GUI nenačíta automaticky zmeny uložené externým Workerom. Pred novým
načítaním treba zachovať neuložené ručné zmeny. Nepracovať súčasne ručne aj
Workerom na tom istom .blend. Každý prijatý výsledok má konkrétny súbor a hash.

## Výkon a prenosnosť

Seed vznikol v Blenderi 4.3.2. Testovací build nemá OpenImageDenoise, preto je
odšumovanie vypnuté a náhľad môže byť zrnitý. Toto nie je vlastnosť modelu.
Oficiálny lokálny Blender môže ponúkať Metal alebo CUDA/OptiX; musí sa to
overiť v Preferences → System. Nezamieňať nastavenie s reálne použitým zariadením.
Na úvod stačí CPU, 960 × 720 a 32-64 vzoriek. Finálne nastavenie nie je vybrané.

## PDF / CAD regenerácia

`scripts/build_documents.py` používa reportlab, ezdxf, Pillow a DejaVu Sans.
Zapisuje PDF, DXF, SVG a computed_metrics.json; nie je to read-only kontrola.
Závislosti uvádza requirements-docs.txt. Prvý Planner ich neinštaluje.
DXF je R2013 v milimetroch; Blender je v metroch. SVG a PDF majú spoločnú
2D geometriu. Kóty v DXF sú neasociatívny text a čiary, nie výrobná dokumentácia.

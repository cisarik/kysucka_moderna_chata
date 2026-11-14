# Kysucká chata - štartovací balík S00

Michal, toto je samostatný pracovný začiatok vizualizácie podľa obrázka.
Model je pripravený na otvorenie a postupné zlepšovanie; hotová vizualizácia
ani architektonické preverenie sa zatiaľ netvrdia.

## Začni tu

1. Rozbaľ celý ZIP do nového vlastného priečinka. Zachovaj vnútornú štruktúru.
2. V Blenderi otvor **blender/kysucka_chata_seed.blend**. Referenčný obrázok je
   zabalený aj v súbore. Python auto-run ani add-on netreba povoľovať.
3. V Cursori otvor ako projekt tento rozbalený priečinok, nie samotný .blend.
4. Vytvor nový Worker chat a zapni skutočný **Plan Mode**. Model vyber v Cursori;
   pre prvú plánovaciu úlohu odporúčam Medium, bez maximum/enhanced režimu.
5. Celý obsah **handoff/kysucka-chata-workstation-bootstrap-and-camera-baseline/01_planning.md**
   vlož do tohto nového chatu. Je to iba plánovací prompt, nie povolenie model meniť.
6. Pošli Chat Orchestratorovi kompletný `01_report.md` (alebo kompletný výstup,
   ak ho klient nevie uložiť). Potom vznikne osobitný realizačný prompt.
   Tlačidlo Build ani súhlas s plánom samo osebe ďalšiu prácu nepovoľuje.

Pred prvým doručením súradnice promptu ešte nie sú spotrebované. Ten istý prompt
nevkladaj do viacerých chatov. Ak sa niečo zastaví, vráť správu Orchestratorovi;
nové číslo relácie nevymýšľaj sám.

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
| protocol/ | presný overený AP snapshot; nie inicializovaný .ap gitlink |
| AGENTS.md | projektové pravidlá pre Cursor Workera |
| handoff/.../01_planning.md | prvý kompletný plánovací prompt v angličtine |
| prompts/RESTORE_CHAT_ORCHESTRATOR.md | obnova read-only Chat Orchestratora pri pokračovaní |
| manifest/ | kontrolné súčty seed podkladov a celého dodania |

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
- Workeri môžu použiť lokálny Blender cez príkazový riadok; MCP je voliteľný.
- Nepracuj súčasne ručne aj Workerom na tom istom súbore. GUI po externom
  uložení potrebuje bezpečné opätovné načítanie.
- Ručná úprava .blend nemení JSON a generátor; pred regeneráciou sa musí
  zosúladiť, ktorá verzia je prijatá.
- Stromy, kvety a nábytok sú zámerné náhrady. Prvé prijatie má sledovať
  kameru a siluetu, nie kvalitu botanických detailov.
- Toto ešte nie je Git repository ani AP offline bundle. Repo URL a publikovanie
  nie sú vybrané; žiadna Git mutácia nie je prvým promptom povolená.

🟡 **Pripravené na manuálne doručenie**

Príjemca: Planner · nový Worker chat · Cursor. Odporúčanie: Medium a približne
250k kontext, ak je dostupný; nejde o tvrdenie o skutočnej kapacite klienta.
Native Plan Mode: **ON**. Prompt: `handoff/kysucka-chata-workstation-bootstrap-and-camera-baseline/01_planning.md`.
Správa: rovnaký priečinok, `01_report.md`. Archivácia: čakať na skutočnú správu.
Model volíš ty; Worker rozlíši žiadaný a skutočne pozorovateľný model.

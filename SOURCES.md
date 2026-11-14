# Pôvod a zdroje S00

## Referencia

`reference/kysucka_chata_moderna.png` je pôvodný používateľom dodaný súbor,
nezmenený. Má 1448 × 1086 pixelov. Je obrazovou inšpiráciou, nie zameraním
ani geometrickým dôkazom reálneho domu. Balík nepridáva nové tvrdenie o jeho licencii.

## Analytic Programming

- Používateľom určený kanonický zdroj: https://github.com/cisarik/ap
- Overený commit: https://github.com/cisarik/ap/commit/d7023cf037f6d17885c3ede5c04812c61640da50
- Pozorovanie 13. 11. 2026: oficiálne GitHub API commits/main; následne
  súbory z nemenného raw SHA. Každý priložený Git blob bol porovnaný
  so SHA v stromovom objekte. Záznam: protocol/SOURCE.json.
- AP.md je sémantický vlastník. AP_ORCHESTRATOR.md a AP_WORKER.md sú
  prevádzkové projekcie; PROMPT_CONTRACTS.md určuje presný tvar metadát.
- Čítaná bola chrbtica Orchestratora, pravidlá plánovania, mutačné osi,
  doručenie správ, zdroje dôkazov, životný cyklus a prvý Planner.
- Snapshot nie je `.ap` submodul, Git transport ani stav Michalovho pracoviska.
  Obsah AP sa v balíku neupravuje. Internetové vyhľadávanie našlo aj starý
  repozitár analytic_programming; ten nebol použitý ako aktuálny protokol.

## Blender

- Použitý a priamo overený lokálny nástroj: Blender 4.3.2.
- Oficiálna dokumentácia príkazového riadku:
  https://docs.blender.org/manual/en/latest/advanced/command_line/arguments.html
- Vlastná procedurálna geometria a materiály, žiadne stiahnuté objekty,
  HDRI, fototextúry alebo add-ony. Referenčný obrázok je zabalený iba ako pomôcka.
- Testovací build nepodporoval OpenImageDenoise; po pravdivom zlyhaní renderu
  sa odšumovanie vyplo. Finálne renderované súbory vznikli úspešne bez neho.

## Možné budúce aktíva - zatiaľ nepoužité

- Poly Haven, overené licenčné pravidlá 13. 11. 2026:
  https://polyhaven.com/license - zverejnené aktíva HDRI/textúry/modely CC0.
- ambientCG, overené vyhlásenie na domovskej stránke 13. 11. 2026:
  https://ambientcg.com/ - dostupné PBR aktíva pod CC0.

Licencia aktíva sa nezamieňa s licenciou webovej stránky, loga alebo ukážkového
renderu. Konkrétne súbory nie sú vybrané, stiahnuté ani obsiahnuté v S00.
Budúci import musí uviesť presnú stránku aktíva, súbor, autora/licenciu,
dátum, veľkosť, hash, úpravy a účel v scéne.

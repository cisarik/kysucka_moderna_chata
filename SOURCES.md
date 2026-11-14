# Pôvod a zdroje S00

## Referencia

`reference/kysucka_chata_moderna.png` je pôvodný používateľom dodaný súbor,
nezmenený. Má 1448 × 1086 pixelov. Je obrazovou inšpiráciou, nie zameraním
ani geometrickým dôkazom reálneho domu. Balík nepridáva nové tvrdenie o jeho licencii.

## Analytic Programming

- Kanonický zdroj: https://github.com/cisarik/ap
- Distribúcia projektu: Git submodul .ap s URL https://github.com/cisarik/ap.git.
- Prijatý nemenný commit:
  https://github.com/cisarik/ap/commit/d7023cf037f6d17885c3ede5c04812c61640da50
- Presnú prijatú verziu určuje gitlink .ap; checkout musí zodpovedať gitlinku.
- .ap/AP.md vlastní sémantiku. .ap/AP_ORCHESTRATOR.md a .ap/AP_WORKER.md
  sú prevádzkové projekcie; .ap/PROMPT_CONTRACTS.md určuje presné metadáta.
- Projektové pravidlá sú mimo spravovaného bloku v AGENTS.md.
  .ap sa pri bežnej práci nemení; aktualizácia vyžaduje osobitný grant.

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

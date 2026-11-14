# Životný cyklus podkladov

Projektová prevádzková projekcia pravidla AP RF-14. Tento súbor nevytvára
nové univerzálne pravidlo AP. Každý riadok uvádza triedu, význam, spotrebiteľa,
vstupný odkaz, uchovanie a vlastníka upratania.

| Cesta | Trieda / autorita | Spotrebiteľ / vstup | Uchovanie a vlastník |
|---|---|---|---|
| AGENTS.md, docs/VISUAL_BRIEF.md | normatívny projektový zámer; nie stavebná autorita | Orchestrator a Worker / README | do výslovného nahradenia; Orchestrator navrhne, poverený Worker zmení |
| model/parameters.json | spoločné hlavné čísla, kamera a materiálové ciele; hypotézy | generátory / AGENTS.md | trvalý zdroj; poverený Worker |
| scripts/design.py | 2D geometria a spoločné geometrické pomocné funkcie | generátory / AGENTS.md | trvalý zdroj; poverený Worker |
| scripts/build_scene.py | podrobná procedurálna stavba scény | Blender / AGENTS.md | trvalý zdroj; poverený Worker |
| reference/ | zachovaný používateľský zdroj; obrazová referencia | všetky vizuálne iterácie / README | do ukončenia projektu alebo pokynu Michala; Michal |
| .ap/, .gitmodules | nemenná AP distribúcia cez Git submodul; pin d7023cf037f6d17885c3ede5c04812c61640da50 | roly AP / AGENTS.md | zachovať; zmena iba osobitným AP update grantom |
| blender/kysucka_chata_seed.blend | odvodený počiatočný checkpoint, bez vizuálneho prijatia | Blender a Workeri / README | zachovať aspoň do prijatia reprodukovateľného nástupcu; Michal |
| docs/*.pdf, cad/ | odvodené pracovné podklady S00 | Michal, neskôr architekt / README | zachovať po dobu používania S00; poverený Worker |
| previews/ | zachovaný dôkaz konkrétneho renderu, bez subjektívneho prijatia | Orchestrator / PDF A19 | do prijatia nástupcu a rozhodnutia o uprataní; Michal |
| externý cisarik/meta: projects/kysucka_moderna_chata/00/00-init/ | historické prompty, správy, poznámky a uzavretie; nie autorita úlohy | Orchestrator a Master / AGENTS.md | prompty a poznámky autoruje Orchestrator, správy Worker; Meta Git publikuje COOPERATOR; poznámky sa pri uzavretí zmrazia |
| manifest/ | historické inventáre pôvodného ne-Git S00 balíka; nie aktuálne brány | čitateľ histórie / manifest/README.md | zachovať bez prepisu hashov; odstránenie iba osobitným grantom |
| work/ | budúce dočasné výstupy; nikdy aktuálna autorita | poverený Worker / OPERATIONS | iba presne vlastnené súbory po prijatí výsledku; poverený Worker |

Spúšťač upratania nie je povolenie vymazať súbor. Aktuálnu identitu určuje presný Git commit, strom a príslušné zdrojové hashe. Publikovanie sa dokazuje priamym verejným readbackom. Ručné zmeny .blend sa automaticky nevracajú do JSON ani generátorov; PDF/CAD a staré rendery nevlastnia aktuálne 3D správanie.

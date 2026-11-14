# Životný cyklus podkladov

Projektová prevádzková projekcia pravidla AP RF-14. Tento súbor nevytvára
nové univerzálne pravidlo AP. Každý riadok uvádza triedu, význam, spotrebiteľa,
vstupný odkaz, uchovanie a vlastníka upratania.

| Cesta | Trieda / autorita | Spotrebiteľ / vstup | Uchovanie a vlastník |
|---|---|---|---|
| AGENTS.md, docs/VISUAL_BRIEF.md | normatívny projektový zámer; nie stavebná autorita | Orchestrator a Worker / README | do výslovného nahradenia; Orchestrator navrhne, poverený Worker zmení |
| model/, scripts/ | trvalé číselné a prevádzkové zdroje vizualizácie | generátory / README, OPERATIONS | po celý projekt; poverený Worker |
| reference/ | zachovaný používateľský zdroj; obrazová referencia | všetky vizuálne iterácie / README | do ukončenia projektu alebo pokynu Michala; Michal |
| protocol/ap/, protocol/SOURCE.json | nemenná referencia presného AP pinu; nie inicializovaný gitlink | roly AP / AGENTS | do autorizovaného prijatia riadnej distribúcie; poverený Worker |
| blender/kysucka_chata_seed.blend | odvodený počiatočný checkpoint, bez vizuálneho prijatia | Blender a Workeri / README | zachovať aspoň do prijatia reprodukovateľného nástupcu; Michal |
| docs/*.pdf, cad/ | odvodené pracovné podklady S00 | Michal, neskôr architekt / README | zachovať po dobu používania S00; poverený Worker |
| previews/ | zachovaný dôkaz konkrétneho renderu, bez subjektívneho prijatia | Orchestrator / PDF A19 | do prijatia nástupcu a rozhodnutia o uprataní; Michal |
| handoff/.../01_planning.md | presný pripravený prompt; autorita až pri riadnom doručení | prvý Planner / README | po doručení historický dôkaz; nevymieňať potichu; Orchestrator |
| handoff/.../01_report.md | budúca štandardná správa Workera; v seede neexistuje | ChatOrchestrator / prompt | vytvorí poverený Worker; potom zachovať dôvodový pár |
| manifest/ | zachovaný dôkaz integrity necommitovaného seed balíka | Planner / README | do prijatia Git baseline; poverený Worker |
| work/ | budúce dočasné výstupy; nikdy aktuálna autorita | poverený Worker / OPERATIONS | iba presne vlastnené súbory po prijatí výsledku; poverený Worker |

Spúšťač upratania nie je povolenie vymazať súbor. Git zatiaľ nie je
inicializovaný. Žiadne zmeny nie sú commitnuté, publikované alebo nasadené.
Balík S00 preto nemožno opisovať ako Git bundle ani aktuálny verejný projekt.

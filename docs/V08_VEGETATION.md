# V08 – ovládateľná chata a úsporná vegetácia

V08 je samostatný technicky overený kandidát. Hlavnou témou zostáva chata.
Scéna sa otvára v ľahkom Solid zobrazení; finálny CPU render používa podrobnejšiu
odvodenú vegetáciu. Celkové vizuálne prijatie patrí Michalovi.

## Výsledok

| Položka | Výsledok |
|---|---:|
| Les | 9 733 stromov; odstránených 3 244, približne 25 % |
| Stromy pod 3 m / 3–5 m / nad 5 m | 1 053 / 3 214 / 5 466 |
| Výška modelov stromov | 1,00–8,32 m |
| Nastavená horná hranica | 9,00 m; vizualizačný parameter zmenšenej krajiny |
| Náročnosť finálnej vegetácie podľa vážených trojuholníkov | 51.73 % V07 |
| Trávne plôšky vo finálnom renderi | 4,110,353 |
| Trávne plôšky v pracovnom náhľade | 32,142 |
| Úplný 360° oblet Solid, 2840 × 1208 | 42.9 FPS, medián skutočných intervalov |
| Material Preview celej ľahkej pracovnej vetvy | 19.2 FPS |

Výšková pestrosť je uložená deterministicky v registri stromov. Výber chráni
dôležité obrysy lesa z troch kontrolných pohľadov, doplnený hrebeň a presuny
pri trase. Otvorené údolie ostáva bez nových stromov. Staré záhradné stromy a
ovocný strom sa do redukcie lesnej populácie nezapočítavajú.

## Tráva a ovládanie

Pracovná vetva používa jednoduché koruny a približne jednu zo 128 trávnych
plôšok. Prepína ju uzol Is Viewport; inštancie sa nerealizujú. Pri renderi sa
automaticky vyhodnotí podrobnejšia vetva so zjednodušenými predlohami.

Polohy pôvodných koreňov, transformácie a masky zostali presne zachované.
Základ nízkeho pokryvu sa nevypína náhodnými dierami. Jemné priestorové polia
miešajú výškové varianty a hustotu vyšších akcentov; najbujnejšie staré lúčne
varianty sú skrátené, aby menej vystupovali ako tmavé chumáče. Horné atlasové
formy sú znížené na 72 % pôvodnej výšky. Pôvodné záhony pri fasáde ostali zachované.
Po preriedení lesa sa navyše obnovilo 199 122 nízkych plôšok v starých výlukách
odstránených kmeňov, aby nevznikli nové holé kruhy. Ich celkový počet je vyšší
približne o 5 % oproti V07, nie násobne. Všetky nové pôdorysy a koreňové obaly
prešli samostatnou kontrolou voči skutočnému terénu, trase a zostávajúcim kmeňom.
Tri pôvodné stredy spadajú do nezmenenej 0,25 m ochrannej zóny susedných
zachovaných kmeňov; tieto miesta sa zámerne neprekrývajú novou trávou.
Jemné smerové a opakujúce sa vzory sú stále viditeľným limitom, nie uzavretým
dôkazom fotorealizmu.

## Diagnostika po HW resete

Prvý Material Preview celej pôvodnej V07 vegetácie sa zastavil pri inicializácii,
pred prvým zmeraným snímkom. Nasledoval Michalov HW reset. Dostupný journal pri
incidente neobsahuje OOM ani NVIDIA Xid; presnú príčinu nemožno potvrdiť.
Aktívny grafický backend je Vulkan, NVIDIA RTX 3080, ovládač 620.70.06.
Žiadna zmena ovládača, backendu ani uložených preferencií neprebehla.

Kontrolné súčty V07, zdrojov a zálohy boli po reštarte overené. MCP bolo znovu
pripojené a čistá V06, otvorená po reštarte, bola nahradená uloženou V07.
Ďalšie spracovanie predlôh a všetky finálne rendery prebehli v oddelených CPU
procesoch, sériovo. Material Preview sa neskôr preveroval iba na ľahkej pracovnej
vetve po etapách chata/les/tráva/celok s externým sledovaním zdrojov.

V07 mala v pôvodnom Solid teste približne 1 FPS s trávou, 85 FPS iba s lesom
a 191 FPS iba s chatou. Toto meranie je pred resetom; V08 je meraná po obnove,
preto nejde o dokonale izolované porovnanie celého systému. Rozhodujúci cieľ
V08 je samostatne splnený úplným obletom nad 20 FPS.

## Zachovanie a dôkazy

Kontrola potvrdila 1619 pôvodných sietí,
4566 objektov, svetlá, world, staré kamery a materiály.
Všetkých 85 obrázkov je zabalených a ich externé súbory majú zhodné hashe.
Všetky nové bazálne obaly trávy sú podmnožinou pôvodných overených obalov;
opora pôvodných plôšok sa prenáša bez opätovného generovania lúky.
Všetkých 199 122 nových doplnení má samostatne premeranú oporu a nulový zásah
do jadra chodníka, prekážok a priestoru mimo terénu. Opakovaná aplikácia V08
nezmenila použité siete, objekty, register ani trávne atribúty a nemení globálny RNG.

P0 zostal CPU, 8 vlákien, 96 vzoriek, CPU OIDN Accurate/High, AgX/None,
frame/seed 0, expozícia 0 a gamma 1. Hlavné snímky majú 1448 × 1086,
detaily 1024 × 768 a severozápadný pohľad 724 × 543. Všetky finálne snímky
sú natívne z uloženého V08. Porovnania kopírujú pixely v mierke 1:1 bez retuše.
Najvyššie zmerané RSS dokončeného procesu je 8.520 GiB;
najnižšia dostupná RAM v dokončených samostatných úlohách 8.166 GiB.
Vzorky NVML zaznamenávajú celú kartu vrátane desktopu, nie výlučne render.

- [Chata pred/po](../previews/v08/comparison_C1.png)
- [Tráva a bránka pred/po](../previews/v08/comparison_gate.png)
- [Les pred/po](../previews/v08/comparison_age.png)
- [Severozápadný pohľad](../previews/v08/after_NW.png)
- [Údolie a hrebeň](../previews/v08/after_valley.png)
- [Úplné metadáta](../previews/v08/render_metadata.json)

## Zdrojová autorita a zvyšný rozsah

`model/parameters.json::vegetation_v08` a `scripts/vegetation_v08.py::apply_v08`
vlastnia správanie V08; builder ich volá po nezmenenom V07 kroku. Všetkých
19 starších JSON sekcií a v03/v04/v05/v06/v07 moduly zostali zachované.
Pracovné checkpointy a logy pod `work/v08/` sú dočasné dôkazy, nie zdrojová autorita.

V07 ostáva porovnávací základ. Jeho nepravidelná šírka krajníc 0,45–0,75 m
zostáva **otvorená a výslovne odložená** na samostatnú úpravu trasy po tejto
optimalizácii. Trasa, prah a geometria terénu sa pri V08 nemenili.
Optika skla/krbu, architektonické detaily a celkové vizuálne prijatie zostávajú
samostatnými témami. Žiadny Git zápis ani publikovanie neprebehli.

V08: `blender/kysucka_chata_mcp_v08.blend`, 318,348,833 bajtov,
SHA-256 `1ba638c7335319c84558e4f779befe9f6a0f7a1ed255d29097359f816d2e6662`. Súbor obsahuje zachované predchodcovské vrstvy aj nové
pracovné a renderové vetvy, preto veľkosť súboru nie je mierou náročnosti náhľadu.

## Pracovný náhľad a skutočný render

Hladké zelené koruny v pôvodnej pracovnej vetve boli veľmi hrubé zástupné
modely. V natívnych snímkach vyššie sa nepoužívajú. Ani Material Preview
automaticky neprepne uzol Is Viewport na podrobnú renderovú vetvu.
Pracovný náhľad preto nemožno zamieňať s výsledným renderom.

Hotový [obrázok chaty](../previews/v08/after_C1.png) sa dá otvoriť aj bez
Blendera. V Blenderi platí tento krátky postup:

1. **Render → Render Image**, prípadne **F12**, vypočíta nový obrázok z aktívnej
   kamery. Tu je to zachovaná CAM_A_REFERENCE, porovnávací pohľad C1.
2. **Render → View Render**, prípadne **F11**, po výpočte zobrazí alebo schová
   okno s výsledkom. Posledný výsledok musí byť ešte dostupný v otvorenom Blenderi.
3. V okne výsledku použiješ **Image → Save As…** na uloženie obrázka.

F12 a rozdiel medzi interaktívnym náhľadom a renderom popisuje
[oficiálny manuál Blender 5.3](https://docs.blender.org/manual/en/5.3/render/introduction.html).
Posledný uložený C1 sa na CPU počítal 188,6 sekundy; nový čas závisí od zaťaženia.

## Voliteľný kandidát s vernejšími pracovnými stromami

`blender/kysucka_chata_mcp_v08_view.blend` zachováva pôvodnú V08 a jej finálnu
renderovú geometriu. Päť pracovných predlôh stromov teraz vychádza z existujúcich
vetiev a otextúrovaného ihličia, s 6 300 alebo 5 400 trojuholníkmi na predlohu.
Pôvodné hrubé koruny sú uchované. Nevznikol nový stiahnutý model ani materiál.
Zdrojové nastavenie je `vegetation_v08.forest.viewport_model = source_branches`
a `viewport_source_triangle_ratio = 0.3`.

Všetkých 9 733 umiestnení, ich výšky, renderové predlohy, tráva a jej masky,
chata aj kamery zostali zachované. Kontrola pred/po a studené otvorenie
samotného uloženého kandidáta potvrdili zhodu sietí, transformácií, uzlov,
registrov a zabalených obrázkov mimo povolených piatich pracovných odkazov.
Opakované prepnutie pracovných predlôh nemení výsledok.
Vyššie prepojené natívne rendery zostávajú snímkami pôvodnej V08;
pre tento čisto pracovný variant sa nové finálne rendery nepočítali.

Meranie na predchádzajúcom štarte systému pri 2840 × 1208: úplný Solid oblet
**41,8 FPS**; krátky etapový Material Preview **16,7 FPS** za celý ľahký celok.
Samostatný les mal v Material Preview 28,9 FPS. Ide o kompromis medzi vernosťou
náhľadu a plynulosťou; fotorealistické prijatie tým nie je potvrdené.
Externé sledovanie testu nezasiahlo, najnižšia voľná VRAM bola 5 518 MiB.

Po neskoršom odpojení bol pozorovaný nový štart systému a opätovne otvorená V06.
Príčina nie je potvrdená; v dostupnom jadrovom zázname predchádzajúceho štartu
nie je incident NVIDIA Xid ani OOM. Po pripojení bol načítaný uložený pracovný
kandidát so zachovaným Image Editorom a zobrazený hotový C1 bez nového renderu
alebo ďalšieho výkonového testu. Zobrazenie kontrolného PNG sa do scény neukladalo.
Dôkazy tejto úpravy sú dočasne v `work/v08/viewport_review/`.

Kandidát má 319 697 451 bajtov, SHA-256
`07146b03e7e74a54c6368fb51e2affa695d8edec58045953a6fc5d62c084104e`.
Aktuálny modul má SHA-256
`cd3137ed08c09726a29a06ba08452f1840a4981e09267de6c94d965dd492fc73`;
JSON `e567d8cc7afb82bec4d7eab8a18f8323c746538e8cc632ba1b6ce2e774e47ff9`.

# Kontrola dodania S00

Dátum: 13. 11. 2026. Klasifikácia: zachovaný neindependentný dôkaz autora
štartovacieho balíka. Toto nie je Worker report, AP acceptance ani vizuálne
prijatie Michalom. Odtlačky finálnych súborov sú v manifest/.

| Kontrola | Výsledok / dôkaz |
|---|---|
| Reálny Blender súbor | úspešne uložený a otvorený v samostatnom procese Blender 4.3.2 |
| Render farebný | úspešný Cycles CPU, 960 × 720, 96 vzoriek; previews/camera_a_material.png |
| Render sivý | úspešný Cycles CPU, 960 × 720, 32 vzoriek; previews/camera_a_clay.png |
| Jednotky a stopa | metre; základ 14,4 × 8,4 m; horná hrana podlahy +0,450 m |
| Kamera a presklenie | porovnané priamym bpy čítaním s JSON, vrátane ohniska a posunu |
| Referencia | zabalené PNG má rovnaké bajty ako dodaný pôvodný obrázok |
| Externé obrázky | žiadny chýbajúci obrázok; nie sú potrebné internetové textúry |
| Automatické spúšťanie | žiadny projektový auto-run text, objektový driver ani projektový handler; jeden vstavaný handler zhodný s factory spustením |
| Scénové údaje | konečné súradnice všetkých vrcholov; 656 objektov |
| PDF | 21 strán, všetky A3 na šírku, vektorové schémy a vložené písmo; textová aj obrazová kontrola |
| DXF | 13 samostatných schém + 1 spoločný súbor, R2013, milimetre, audit bez chýb |
| SVG | 13 syntakticky platných vektorových schém |
| AP zdroje | 40 nemenných súborov overených ako Git bloby na uvedenom pine |

Podrobnejšie pozorovania sú v scene_readback.json, document_readback.json a
previews/render_*.json. Informácia o lokálnej ceste v render metadata označuje
iba prostredie, v ktorom bol náhľad vytvorený; nie Michalovo pracovisko.

## Vyriešené problémy pri tvorbe

- Testovací Blender build nepodporoval OpenImageDenoise. Pôvodný render
  skončil nenulovým stavom; finálna cesta má odšumovanie vypnuté a bola
  úspešne znovu vykonaná. Zrnitosť náhľadu je známa.
- Prvá kamera bola vysoko nad domom. Po obrazovej kontrole vznikol nižší
  vodorovný pohľad s posunom senzora. Kamera stále nie je vizuálne prijatá.
- Veľké pomocné plošné svetlá sa odrážali v skle ako biele plochy.
  Pomocným svetlám sa vypla viditeľnosť v kamerových/lesklých/prenosových lúčoch.
- Kamenné pásy vstupu pôvodne prechádzali okapovou hranou. Ich vrch je
  teraz +2,900 m, samostatný spoločný parameter, priamym čítaním overený.
- Prvá kontrola počtu handlerov mylne očakávala absolútnu nulu. Čisté
  factory spustenie preukázalo rovnaký vstavaný
  pose_library.gui._on_blendfile_load_post. Opravila sa kontrolná hypotéza,
  nie povolenie projektového auto-run.
- Pri obrazovej kontrole PDF sa posunuli označenia grafickej mierky nad
  pätičku a zväčšili kótovacie texty. Kontroluje sa finálny export.

## Neoverené a zámerne otvorené

Nie je vykonaná subjektívna akceptácia podobnosti, skúška na Michalovom Macu,
architektonická kontrola, statika, výber technológií ani finálny render.
Stromy a nábytok sú náhrady; krajina zatiaľ nedosahuje charakter referencie.
Zadné strany a dispozícia nie sú zistené z obrázka. W01 v dispozičnej hypotéze
prechádza pred dvoma miestnosťami zázemia; detail napojenia priečky na delenie
okna je otvorený a nie je vyriešeným stavebným detailom.
Žiadne Git init/commit/push, hosting, platený provider alebo kontaktovanie
architekta neprebehlo. Presný budúci grant pripraví Chat Orchestrator po správe
prvého Plannera.

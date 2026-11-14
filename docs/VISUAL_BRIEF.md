# Vizuálny zámer S00

Vzťah k AP: projektový vizuálny zámer. Univerzálnu sémantiku vlastní .ap/AP.md na commite zaznamenanom gitlinkom .ap; prijatý pin je d7023cf037f6d17885c3ede5c04812c61640da50. Projektové pravidlá sú v AGENTS.md; životný cyklus v ARTIFACT_LIFECYCLE.md. Meta je historický dôkaz, nie aktuálne povolenie.

## Prijaté rozhodnutia Michala

1. Vytvoriť čo najvernejšiu 3D vizualizáciu podľa dodaného obrázka, postupne
   cez ohraničené úlohy Workerov v klientovi zvolenom Michalom.
2. Master Orchestrator koordinuje vývojový beh; Orchestrator aktuálneho celku koordinuje jeho plán, granty, prijatie a uzavretie. Worker koná iba podľa aktuálneho úplného grantu. S00 je počiatočný podklad, nie dokončený model.
3. Architektovi zatiaľ nič neposielať ani nežiadať kontrolu. K prípadnej
   architektonickej fáze sa vrátiť až po veľmi dobrej vizualizácii.
4. Dodať PDF schémy, upraviteľný CAD a reálny otvárateľný Blender projekt.
5. Používať overený protokol AP; neprenášať projekt Jelena ani jeho stav do
   tejto novej práce. Toto je samostatný projekt.

## Viditeľné znaky, ktoré treba zachovať

- Jednoduchý pozdĺžny dom so strmou sedlovou strechou a hlbokým presahom.
- Nízka dlhá vstupná strana, teplé horizontálne drevo a svetlý sokel.
- Veľké presklenie pravého štítu, zreteľné tmavé subtílne profily,
  horné drevené plochy a teplé lineárne osvetlenie.
- Vstup medzi svetlými kamennými pásmi, pozdĺžne okno naľavo,
  otvorený priestor na drevo, lavica a jednoduché schody.
- Svetlý komín, zelená lúka, členité zalesnené kopce, ovocný strom,
  nízky drevený plot a kultivovaný predzáhradný detail.

## Navrhnuté hodnoty, ktoré ešte Michal neprijal

Čísla v `model/parameters.json`, vrátane 14,4 × 8,4 m, sklonu 45°,
výškových úrovní, členenia skla a kamery, sú pracovné odhady Orchestratora.
Dispozícia, zadná fasáda, opačný štít a konštrukčné rezervy sú návrh.
S00 obsahuje jedno prízemie otvorené do strechy, bez obytného podkrovia.

Rozmery sa pri zmene prijatého zámeru aktualizujú v spoločnom zdroji.
Geometrický model nie je meranie, statika, stavebná dokumentácia ani BIM.
Plochy sú geometrické súčty obdĺžnikov, nie normové výpočty.

## Úvodný rozsah a ďalšie možnosti

Aktuálny inicializačný celok zavádza pripnuté AP, projektové pravidlá a externú Meta stopu bez zmeny scény. Po jeho uzavretí môže Master odporučiť samostatný celok kanonického renderu a kamery; vyberá ho Michal. Toto nie je povolenie vizuálnych úprav.

Pôvodný obrázok má nezmeranú perspektívu a môže obsahovať nejednoznačnú
geometriu alebo odrazy. Pri konflikte má prednosť ucelený prijatý model;
rozdiel sa označí a rozhodne ho Michal, nie skryté deformácie.

## Vizuálne prijatie

Pri rovnakom pomere strán porovnávať 1 siluetu, 2 kameru, 3 vstup a okná,
4 členenie štítu, 5 materiály a svetlo, 6 okolie. Michal môže označiť
PASS / FAIL / NOT TESTED. Po technickej kontrole nevzniká automaticky
subjektívne prijatie. Finálny vizuálny cieľ zatiaľ nie je uzavretý.

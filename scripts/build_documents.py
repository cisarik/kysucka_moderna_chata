"""Author the S00 A3 visual brief, 2D DXF and SVGs from shared seed geometry.
Dependencies are listed in requirements-docs.txt. No network access.
"""
from pathlib import Path
import sys,math,json,html
sys.path.insert(0,str(Path(__file__).resolve().parent))
from design import *
import ezdxf
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor,white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph,Table,TableStyle
from reportlab.lib.styles import ParagraphStyle

OUT=ROOT/'docs';OUT.mkdir(exist_ok=True)
CAD=ROOT/'cad';CAD.mkdir(exist_ok=True)
SVG=CAD/'svg';SVG.mkdir(exist_ok=True)
for name,fn in [('D','DejaVuSans.ttf'),('DB','DejaVuSans-Bold.ttf')]:
    font=Path('/usr/share/fonts/truetype/dejavu')/fn
    if not font.exists():
        candidates=list(Path('/usr/share/fonts').rglob(fn));font=candidates[0] if candidates else None
    if not font:raise RuntimeError('Install DejaVu Sans fonts for Slovak PDF text')
    pdfmetrics.registerFont(TTFont(name,str(font)))
pdfmetrics.registerFontFamily('D',normal='D',bold='DB')
NAVY=HexColor('#16333d');TEAL=HexColor('#287e86');MUTED=HexColor('#667b83');GOLD=HexColor('#a67b47');PALE=HexColor('#eef4f3')

def cad_exports():
    combined=ezdxf.new('R2013');combined.units=4
    def init(doc):
        for layer,color in COLORS.items():
            doc.layers.new(layer,dxfattribs={'true_color':int(color[1:],16),'lineweight':25 if layer in ['OUTLINE','WALL'] else 13})
        doc.header['$INSUNITS']=4;doc.header['$MEASUREMENT']=1
        doc.styles.new('SEED',dxfattribs={'font':'DejaVuSans.ttf'})
    init(combined)
    for idx,d in enumerate(all_drawings()):
        doc=ezdxf.new('R2013');doc.units=4;init(doc)
        for target,offset in [(doc,(0,0)),(combined,((idx%3)*35000,-(idx//3)*27000))]:
            ms=target.modelspace();ox,oy=offset
            def pt(a):return (a[0]*1000+ox,a[1]*1000+oy)
            for it in d.items:
                kind=it[0]
                if kind=='line':ms.add_line(pt(it[1]),pt(it[2]),dxfattribs={'layer':it[3]})
                elif kind=='poly':
                    _,pts,layer,fill,close=it
                    ms.add_lwpolyline([pt(a) for a in pts],close=close,dxfattribs={'layer':layer})
                elif kind=='circle':ms.add_circle(pt(it[1]),it[2]*1000,dxfattribs={'layer':it[3]})
                elif kind=='text':
                    _,xy,s,h,layer,anchor=it
                    from ezdxf.enums import TextEntityAlignment
                    align={'start':TextEntityAlignment.LEFT,'middle':TextEntityAlignment.CENTER,'end':TextEntityAlignment.RIGHT}[anchor]
                    ms.add_text(s,dxfattribs={'height':h*1000,'layer':layer,'style':'SEED'}).set_placement(pt(xy),align=align)
            if target is combined:ms.add_text(d.name,dxfattribs={'height':300,'layer':'TEXT','style':'SEED'}).set_placement((ox,oy-3400))
        doc.set_modelspace_vport(20000,center=(7000,3500));doc.saveas(CAD/(d.name+'.dxf'))
        xmin,ymin,xmax,ymax=d.bounds;pad=.2;vw=xmax-xmin+pad*2;vh=ymax-ymin+pad*2
        def sx(x):return x-xmin+pad
        def sy(y):return ymax-y+pad
        bits=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {vw} {vh}" width="{vw*1000/d.scale}mm" height="{vh*1000/d.scale}mm"><rect width="100%" height="100%" fill="white"/>']
        for it in d.items:
            kind=it[0]
            if kind=='line':
                _,a,b,layer=it;bits.append(f'<line x1="{sx(a[0])}" y1="{sy(a[1])}" x2="{sx(b[0])}" y2="{sy(b[1])}" stroke="{COLORS[layer]}" stroke-width="0.014"/>')
            elif kind=='poly':
                _,pts,layer,fill,close=it;points=' '.join(f'{sx(a[0])},{sy(a[1])}' for a in pts)
                tag='polygon' if close else 'polyline';bits.append(f'<{tag} points="{points}" fill="{fill or "none"}" stroke="{COLORS[layer]}" stroke-width="0.018"/>')
            elif kind=='circle':
                _,xy,r,layer=it;bits.append(f'<circle cx="{sx(xy[0])}" cy="{sy(xy[1])}" r="{r}" fill="none" stroke="{COLORS[layer]}" stroke-width="0.014"/>')
            else:
                _,xy,s,h,layer,anchor=it;bits.append(f'<text x="{sx(xy[0])}" y="{sy(xy[1])}" font-family="DejaVu Sans,sans-serif" font-size="{h}" text-anchor="{anchor}" fill="{COLORS[layer]}">{html.escape(s)}</text>')
        bits.append('</svg>');(SVG/(d.name+'.svg')).write_text('\n'.join(bits))
    combined.set_modelspace_vport(50000,center=(30000,-40000));combined.saveas(CAD/'Kysucka_chata_S00_all_views.dxf')

C=canvas.Canvas(str(OUT/'Kysucka_chata_pracovna_studia_S00.pdf'),pagesize=(420*mm,297*mm))
C.setTitle('Kysucká chata - vizualizačná štúdia S00');C.setAuthor('Pripravené pre Michala - pracovná hypotéza z referenčného obrázka')
PAGE=0

def text(x,y,s,size=10,bold=False,col=NAVY):
    C.setFillColor(col);C.setFont('DB' if bold else 'D',size);C.drawString(x*mm,y*mm,s)

def para(x,y,w,s,size=9.2,col=NAVY,leading=None):
    style=ParagraphStyle('p',fontName='D',fontSize=size,leading=leading or size*1.5,textColor=col,spaceAfter=0)
    obj=Paragraph(s,style);ww,hh=obj.wrap(w*mm,1000*mm);obj.drawOn(C,x*mm,y*mm-hh);return y-hh/mm

def rule(x,y,w,col=TEAL):
    C.setStrokeColor(col);C.setLineWidth(.5);C.line(x*mm,y*mm,(x+w)*mm,y*mm)

def box(x,y,w,h,color=PALE):
    C.setFillColor(color);C.roundRect(x*mm,y*mm,w*mm,h*mm,2*mm,stroke=0,fill=1)

def table(x,y,width,rows,colwidths=None,size=8.6):
    st=ParagraphStyle('t',fontName='D',fontSize=size,leading=size*1.4,textColor=NAVY)
    ss=[[Paragraph(html.escape(str(v)),st) for v in row] for row in rows]
    cw=[v*mm for v in colwidths] if colwidths else None
    t=Table(ss,colWidths=cw or [width*mm/len(rows[0])]*len(rows[0]),hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#dfeceb')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),('LINEBELOW',(0,0),(-1,0),.7,TEAL),('LINEBELOW',(0,1),(-1,-1),.25,HexColor('#d1dedd'))]))
    w,h=t.wrap(width*mm,1000*mm)
    if y-h/mm<27:raise RuntimeError(f'Table overflow on page {PAGE}: {y-h/mm:.1f}')
    t.drawOn(C,x*mm,y*mm-h);return y-h/mm

def page(code,title,sub=''):
    global PAGE
    if PAGE:C.showPage()
    PAGE+=1
    C.setFillColor(white);C.rect(0,0,420*mm,297*mm,fill=1,stroke=0)
    text(14,282,'KYSUCKÁ CHATA',10,True);text(267,282,'VIZUALIZAČNÁ ŠTÚDIA / S00 / 13. 11. 2026',8,col=MUTED)
    text(14,267,title,22,True);text(14,256,sub,9,col=MUTED);rule(14,250,392)
    rule(14,23,392,HexColor('#c1d1d2'))
    text(14,14,'PRACOVNÝ MODEL Z JEDNÉHO OBRÁZKA | KÓTY SÚ NÁVRHOVÉ ODHADY | NIE REALIZAČNÝ PROJEKT',7.4,col=MUTED)
    text(359,14,f'{code}  /  {PAGE:02d}',8,True)

def drawing(d,x=14,y=39,w=270,h=204,scale=None):
    sc=scale or d.scale;k=1000/sc
    xmin,ymin,xmax,ymax=d.bounds;ww=(xmax-xmin)*k;hh=(ymax-ymin)*k
    if ww>w+.1 or hh>h+.1:raise RuntimeError(f'Drawing overflow {d.name} {ww} {hh} in {w} {h}')
    ox=x+(w-ww)/2-xmin*k;oy=y+(h-hh)/2-ymin*k
    def p(a):return ((ox+a[0]*k)*mm,(oy+a[1]*k)*mm)
    for it in d.items:
        C.saveState();kind=it[0];layer=it[-1] if kind=='line' else None
        if kind=='line':
            _,a,b,layer=it;C.setStrokeColor(HexColor(COLORS[layer]));C.setLineWidth(.62 if layer in ['WALL','OUTLINE'] else .32)
            if layer in ['HIDDEN','GRID']:C.setDash(3,2)
            C.line(*p(a),*p(b))
        elif kind=='poly':
            _,pts,layer,fill,close=it;path=C.beginPath();path.moveTo(*p(pts[0]))
            for a in pts[1:]:path.lineTo(*p(a))
            if close:path.close()
            C.setStrokeColor(HexColor(COLORS[layer]));C.setLineWidth(.7 if layer=='WALL' else .45)
            if layer in ['HIDDEN','GRID']:C.setDash(3,2)
            if fill:C.setFillColor(HexColor(fill))
            C.drawPath(path,stroke=1,fill=bool(fill))
        elif kind=='circle':
            _,xy,r,layer=it;C.setStrokeColor(HexColor(COLORS[layer]));C.setLineWidth(.4);C.circle(*p(xy),r*k*mm,stroke=1,fill=0)
        else:
            _,xy,s,h0,layer,anchor=it;C.setFillColor(HexColor(COLORS[layer]));C.setFont('D',h0*k*mm)
            fn={'start':C.drawString,'middle':C.drawCentredString,'end':C.drawRightString}[anchor];fn(*p(xy),s)
        C.restoreState()
    text(x,y-5,f'Mierka 1 : {sc} pri tlači A3 na 100 % | kóty v mm, výšky v m',8,col=MUTED)
    # Exact 5 m graphic scale, even when a viewer resizes the sheet.
    if sc>=50:
        for i in range(5):
            C.setFillColor(NAVY if i%2==0 else white);C.setStrokeColor(NAVY);C.rect((x+i*k)*mm,(y-10)*mm,k*mm,2*mm,fill=1,stroke=1)
        text(x,y-14,'0',7,col=MUTED);text(x+5*k-3,y-14,'5 m',7,col=MUTED)

def notes(items):
    x,y,w=296,240,106
    for heading,body in items:
        text(x,y,heading,10,True,col=TEAL);y-=5
        y=para(x,y,w,body,9.0)-9
    return y

def viewpage(code,title,d,items,sub='Pracovná geometria S00. Viditeľné znaky sú interpretované; absolútna mierka je zvolená.'):
    page(code,title,sub);drawing(d);notes(items)

def imagefit(path,x,y,w,h):
    from PIL import Image
    im=Image.open(path);iw,ih=im.size;f=min(w/iw,h/ih);ww,hh=iw*f,ih*f
    C.drawImage(str(path),(x+(w-ww)/2)*mm,(y+(h-hh)/2)*mm,ww*mm,hh*mm,mask='auto')
    return x+(w-ww)/2,y+(h-hh)/2,ww,hh

m=metrics()
page('A00','Obrázok ako začiatok 3D projektu','Koncepčný CAD + pracovný Blender model + riadený postup cez AP')
imagefit(ROOT/'reference/kysucka_chata_moderna.png',14,43,270,202.5)
notes([('CIEĽ TERAZ','Postupne vytvoriť čo najpodobnejšiu vizualizáciu. Architektonické preverenie a prípadná dokumentácia prídu až po vizuálnom odsúhlasení.'),('ČO JE TENTO BALÍK','Otvoriteľný .blend, editovateľné 2D DXF/SVG, 21 listov A3, zdieľané parametre a prvý plánovací prompt pre Cursor.'),('MIERKA S00','Celkový obrys 14,4 × 8,4 m; z toho otvorený prístrešok 2,4 m. Všetky metre sú zvolená pracovná hypotéza.'),('ROZHODUJÚCA HRANICA','Z jediného obrázka sa nedá zistiť skutočný pôdorys, skryté fasády, skladby ani nosný systém. Tieto časti sú výslovne navrhnuté.'),('AUTORITA','Číselným zdrojom je model/parameters.json. Balík je štartovací podklad, nie prijatý AP implementačný kandidát.')])

page('A01','Čítanie referencie a miera istoty','Zachovať charakter domu; nevydávať domnienky za zameranie.')
ix,iy,iw,ih=imagefit(ROOT/'reference/kysucka_chata_moderna.png',14,43,270,202.5)
landmarks=[('1',1244,107),('2',1180,444),('3',706,636),('4',949,179),('5',329,688),('6',940,708),('7',511,569),('8',702,957)]
for no,px,py in landmarks:
    xx=ix+iw*px/1448;yy=iy+ih*(1-py/1086);C.setFillColor(NAVY);C.circle(xx*mm,yy*mm,3.5*mm,fill=1,stroke=0);C.setFillColor(white);C.setFont('DB',9);C.drawCentredString(xx*mm,(yy-1.1)*mm,no)
notes([('1 / STRECHA','Výrazná sedlová silueta, tmavé pravidelné pásy, hlboký presah. Sklon 45° je voľba S00.'),('2 / ŠTÍT','Veľké prízemné aj horné presklenie, tmavé stĺpiky, drevené kraje a teplá línia pod strechou.'),('3, 5, 6 / VSTUPNÁ STRANA','Dvere v kamennom ráme, bočné okno, otvorené drevo, lavica a doplnky. Ich presné rozostupy nepoznáme.'),('4, 7, 8 / KOMPOZÍCIA','Svetlý komín, okapová línia, ovocný strom, nízky plot, lúka a lesnaté kopce.'),('LEGENDA ISTOTY','VIDITEĽNÉ: prítomnosť a charakter prvku.<br/>ODHAD: metre, proporcie, kamera a farby.<br/>NÁVRH: dispozícia, zadná strana, technické riešenia.')])

viewpage('A02','Súradnice, osi a základné rozmery',datums(),[
('JEDEN SYSTÉM','X: od dreva k presklenému štítu. Y: od vstupu k zadnej fasáde. Z: nahor. Počiatok je ľavý predný roh; terén má Z = 0.'),
('HLAVNÉ ODHADY','A-D = 14 400 mm; šírka = 8 400 mm.<br/>A-B = 2 400 mm prístrešok.<br/>B-D = 12 000 mm uzavretý objem.'),
('VÝŠKOVÉ ÚROVNE','Podlaha +0,450 m.<br/>Horná hrana steny +3,250 m.<br/>Nominálna rovina hrebeňa +7,450 m.<br/>Vrchol komínovej krycej dosky +8,450 m.'),
('SÚČTY PÔDORYSU',f'Celková stopa {m["gross_total"]:.2f} m².<br/>Uzavretý vonkajší obal {m["gross_enclosed"]:.2f} m².<br/>Prístrešok {m["covered_bay"]:.2f} m².'),
('NIE GEODETICKÁ SITUÁCIA','Nie je určený sever, parcela, nadmorská výška ani vzťah k reálnemu pozemku.')])

page('A03','Pôdorys prízemia - dispozičná hypotéza','Mierka 1 : 75 | všetky miestnosti a priečky sú navrhnuté, nie odčítané z obrázka')
drawing(base_plan());rows=[['ID / miestnosť','Vnútorné mm','m²']]
for rr,r in zip(m['rooms'],P['rooms']):
    x,y0,x1,y1=r['rect'];rows.append([rr[0]+' / '+rr[1],f'{(x1-x)*1000:.0f} × {(y1-y0)*1000:.0f}',f'{rr[2]:.2f}'])
y=table(296,241,106,rows,[53,32,21],8.2)
y=para(296,y-8,106,f'Súčet čistých obdĺžnikov miestností: <b>{m["net_rooms"]:.2f} m²</b>. Nejde o normovú podlahovú alebo úžitkovú plochu.',9)
para(296,y-9,106,'Vonkajšia stena 300 mm a priečky 150 mm sú iba geometrické rezervy. Hrúbky nie sú overenou stavebnou skladbou. Obývacia časť je otvorená do krovu; obytné podkrovie ani schodisko nie sú navrhnuté.',9)

viewpage('A04','Prízemie - orientačné zariadenie',base_plan(True),[
('ÚČEL DISPOZÍCIE','Dať otvorom a preskleniu zrozumiteľný vnútorný kontext. Nie je to schválená dispozícia ani návrh pre konkrétne potreby domácnosti.'),
('DENNÁ ZÓNA','Obývanie, stôl a kuchynský blok pri presklenom štíte. Krb je v rovnakej osi ako komín; doplnky v .blend sú samostatné náhrady.'),
('SÚKROMNÁ ZÓNA','Dve izby vzadu, kúpeľňa, technická miestnosť a zádverie vľavo. Zadné okná sú iba návrh.'),
('ČO SA ZATIAĽ NERIEŠI','Ergonómia v detailoch, hygienické požiadavky, bezbariérovosť, únikové cesty a technológie. Ich preverenie patrí do prípadnej neskoršej fázy.'),
('KONZISTENCIA','Blender obsahuje jednoduché priečky a denný nábytok. Nábytok súkromných izieb zostáva iba v 2D štúdii.')])

viewpage('A05','Strecha - pôdorys a presahy',roof_plan(),[
('GEOMETRIA',f'Dve rovnaké roviny, sklon {m["roof_angle"]:.1f}°. Hrebeň rovnobežný s X. Bez vikierov a strešných okien.'),
('ROZMER STRECHY','Pôdorysný obrys 15 500 × 10 100 mm.<br/>Presah pri okape 850 mm.<br/>Presah štítu 550 mm.'),
('PLOCHA',f'Geometrická plocha oboch rovín približne {m["roof_area"]:.1f} m². Bez odpadu, lemovaní, komína a technologických rezerv; nie výkaz na objednávku.'),
('K01 / KOMÍN','Os X = 11,300 m, Y = 3,200 m. Teleso 800 × 800 mm. Krycia doska 1 000 × 1 000 mm. Iba vizuálny návrh.'),
('KRYTINA','Skladanie a tmavá farba vychádzajú z obrázka. Konkrétny materiál, výrobok, kotvenie a klampiarske detaily sú otvorené.')])

viewpage('A06','Vstupná pozdĺžna fasáda',long_elevation(),[
('IDENTITA DOMU','Dlhá nízka okapová línia, teplé drevo, otvor na drevo naľavo a výrazný vstup.'),
('D01 / W01','D01: 1 250 × 2 300 mm.<br/>W01: 2 000 × 1 150 mm; parapet 900 mm nad podlahou. Rozmery sú vizuálne odhady.'),
('KAMENNÝ PORTÁL','Dva zvislé svetlé pásy, tmavé dvere, subtilná kľučka a malé nástenné svietidlá. Škáry a kresba kameňa sa budú dolaďovať.'),
('PRESAH','V ortogonálnom pohľade sa hlboký okap čiastočne prekrýva so stenou. Otvory sú pre čitateľnosť v schéme zobrazené celé.'),
('MIERA PRESNOSTI','Rytmus fasády je návrh S00; pred materiálovou prácou ho treba porovnať z kamery A s referenciou.')])

viewpage('A07','Presklený štít - hlavný vizuálny prvok',gable_elevation(),[
('ZÁKLAD','Šírka štítu 8 400 mm. Výška od podlahy po nominálny hrebeň 7 000 mm. Celková silueta má v S00 sklon 45°.'),
('G01 / G02','G01: spodná presklená zóna +0,450 až +3,180 m. G02: horná časť od +3,180 m, orezaná strechou. Nejde o výrobný výkres skla.'),
('STĹPIKY','Osové polohy Y: 150 / 2 175 / 4 200 / 6 225 / 8 250 mm. Vizuálna šírka profilu 75 mm, hĺbka v modeli 130 mm.'),
('KRAJE ŠTÍTU','Horné sklo je medzi Y = 1,350 a 7,050 m. Krajné trojuholníkové plochy sú drevené.'),
('OTVORENÉ OTÁZKY','Skutočné členenie, nosná konštrukcia, bezpečnostné sklo, spôsob otvárania a tienenie zostávajú neurčené.')])

viewpage('A08','Zadná fasáda - výslovne navrhnutá',long_elevation(True),[
('NEVIDENÁ STRANA','Obrázok zadnú stranu neukazuje. Každé okno na tomto liste je návrh pre pracovný model.'),
('OTVORY','W02 a W03: 1 400 × 1 200 mm, parapet 900 mm. W04: 1 800 × 1 100 mm, parapet 1 100 mm. Hodnoty od podlahy.'),
('ZJEDNOTENIE','Pokračuje rovnaké horizontálne drevo, svetlý sokel a strecha. Bez ďalších prístavieb a efektov.'),
('PRE VIZUALIZÁCIU','Nehľadať drahé detaily na nevidenej strane skôr, než bude odsúhlasený hlavný pohľad. Tento list udržiava uzavretý model.'),
('NESKORŠIA REVÍZIA','Po vizuálnom odsúhlasení sa strana prispôsobí skutočnému pozemku, dispozícii a potrebám.')])

viewpage('A09','Opačný štít - výslovne navrhnutý',gable_elevation(True),[
('PREDPOKLAD','Opačný štít uzatvára drevená plocha pri X = 2,400 m. Priestor X = 0 až 2,400 m zostáva otvoreným prístreškom.'),
('BEZ NOVÝCH MOTÍVOV','V S00 nie sú navrhnuté ďalšie štítové okná, balkón ani bočný vstup. Referencia o nich neposkytuje informáciu.'),
('PRÍSTREŠOK','Má spoločnú strechu s domom. V modeli sú predné stĺpiky a drevo; nevidené zadné podopretie a statické riešenie sa nepredstierajú.'),
('ČO TENTO POHĽAD JE','Schéma profilu a výplne, nie pohľad na zameranú existujúcu stavbu. Nosný systém nie je riešený.')])

viewpage('A10','Priečny rez A-A / otvorený objem',gable_elevation(section=True),[
('ROVINA REZU','X = 10,000 m; smer pohľadu pozdĺž X. Zobrazuje geometrický priečny obal dennej zóny.'),
('SVETLÝ PRIESTOR','Podlaha +0,450 m, stena +3,250 m. Vizuálna výška k stene 2 800 mm; po hrebeň 7 000 mm. Skutočná čistá výška závisí od budúcich skladieb.'),
('BEZ PODKROVIA','S00 zámerne nepridáva druhé podlažie. Neznámy interiér sa tak nepremení na falošne istý návrh poschodia.'),
('ZJEDNODUŠENIE','Strecha je vizuálna škrupina. Väzníky, krokvy, tepelná izolácia, parotesnosť a základové konštrukcie nie sú určené.'),
('SÚRADNICE REZOV','A-A: X = 10,000 m.<br/>B-B: Y = 4,200 m, pozdĺž hrebeňa. Rezy nepredstavujú výpočet nosnosti.')])

viewpage('A11','Pozdĺžny rez B-B / organizácia objemu',long_section(),[
('ROVINA REZU','Y = 4,200 m; smer pohľadu k vstupnej strane. Krb a komín sú premietnuté pre súvislosť, neležia priamo v rovine rezu.'),
('OBJEMY','Otvorený prístrešok 2,4 m, zázemie s izbami a vysoká denná zóna pri presklenom štíte.'),
('PRIEČKY','V modeli končia v +3,050 m; horný priestor nie je riešený ako uzavreté obytné podkrovie. Akustika a stropy sú otvorené.'),
('KRB / KOMÍN','Os X = 11,300 m, Y = 3,200 m. Stĺpec na liste je schematická projekcia. Odstupy od dreva a technické napojenie sa zatiaľ neurčujú.'),
('NIE KONŠTRUKČNÝ REZ','Neobsahuje základy, výstuž, nosné spojenia, izolácie ani technologické vrstvy.')])

page('A12','Otvory a geometria presklenia','Rozmery sú nominálne vizualizačné hodnoty; žiadny záznam nie je podklad na výrobu.')
rows=[['ID','Strana / zóna','Šírka mm','Výška mm','Parapet nad podlahou mm','Istota']]
for o in P['openings']:rows.append([o['id'],'Vstup' if o['side']=='front' else 'Zadná strana',f'{o["width"]*1000:.0f}',f'{o["height"]*1000:.0f}',f'{o["sill"]*1000:.0f}','ODHAD' if o['status']=='estimated' else 'NÁVRH'])
for o in P['interior_doors']:rows.append([o['id'],'Vnútorné dvere',f'{o["width"]*1000:.0f}','2 100','0','NÁVRH'])
y=table(14,240,392,rows,[22,83,50,50,107,80],9)
text(14,y-14,'Horná hranica skla G02: vybrané body profilu v lokálnom štíte',12,True)
rows=[['Y od vstupnej hrany mm','Horná hrana výplne Z, m','Poznámka']]
for yy in [1.35,2.175,4.2,6.225,7.05]:rows.append([f'{yy*1000:.0f}',f'{roof_z(yy)-.18:.3f}','Rovina strechy mínus 180 mm, iba vizuálna medzera'])
y=table(14,y-20,392,rows,[100,86,206],8.8)
para(14,y-7,392,'G01: pole široké nominálne 8 100 mm, medzi Y 150 a 8 250 mm; horná hrana Z +3,180 m. Profily uberajú zo svetlého rozmeru. Osemdesiatmilimetrové a ďalšie rezervy nie sú výrobnými toleranciami. V DXF sú kóty textové a čiarové, neasociatívne.',8.6)

page('A13','Detail D1 / okap ako vizuálna hranica','Mierka 1 : 15 | štúdia tvaru a svetla, bez skladby strešného plášťa')
drawing(eave_detail(),14,57,183,174)
text(215,238,'Čo je zafixované v S00',13,True)
y=para(215,229,186,'Presah 850 mm, nominálna okapová hrana +2,400 m, horná hrana steny +3,250 m. Podhľad tvorí drevo; tenká teplá svetelná línia vedie pri okraji.',10)
text(215,y-12,'Čo je iba vizuálna náhrada',12,True)
y=para(215,y-20,186,'Hrúbka škrupiny 160 mm slúži na tieň a okraj strechy. Nie je to návrh skladby. Tmavá okrajová lišta, naznačené odvodnenie a LED nemajú definované technické riešenie.',9.5)
text(215,y-12,'Podobnosť s obrázkom',12,True)
y=para(215,y-20,186,'Najprv sledovať siluetu, hĺbku tieňa, tenkosť čelnej hrany a súvislú líniu podsvietenia. Nepoužívať silné žlté pásy a nadmerný žiarivý efekt.',9.5)
para(215,y-12,186,'Pred prípadnou realizáciou treba samostatne určiť konštrukciu, vetranie, odvodnenie, požiarne odstupy a servis osvetlenia. V tejto fáze sa ich správnosť netvrdí.',9.3,col=MUTED)

viewpage('A14','Detail D2 / vstup, lavica a schody',entry_detail(),[
('DVERNÉ POLE','D01 1 250 × 2 300 mm. Dva kamenné pásy šírky 480 mm a pozdĺžna kovová kľučka. Všetko ako odhad proporcií.'),
('LAVICA','Dĺžka 2 100 mm, hĺbka 650 mm, vrch približne 565 mm nad podlahou v 3D náhrade. Pre skutočné sedenie sa výška ešte upraví.'),
('SCHODY','Tri výšky po 150 mm = rozdiel 450 mm. Nominálna stopa 350 mm; šírka 2 350 mm. Zatiaľ bez zábradlia a normového preverenia.'),
('DREVO A DOPLNKY','Naskladané polená patria do otvoreného ľavého poľa. Dekorácia, kvety a textílie sú odložiteľné prvky; nesmú maskovať chybnú geometriu.'),
('NEZAHŔŇA','Kotvenie, hydroizoláciu prahu, základ lavice, bezpečné povrchy a technické detaily svietidiel.')])

page('A15','Materiály, farby a svetlo','V S00 sú všetky materiály procedurálne a zabalené v .blend; žiadne externé textúry nie sú potrebné.')
rows=[['ID v Blenderi','Vizuálny cieľ','Referenčná farba','Drsnosť S00','Ďalší krok']]
for mat in P['materials']:rows.append([mat['id'],mat['label'],mat['color'],mat['roughness'],'Neskôr vybrať konkrétnu PBR textúru' if 'WOOD' in mat['id'] or 'STONE' in mat['id'] else 'Vyladiť až po kamere a siluete'])
y=table(14,241,392,rows,[68,99,54,45,126],9)
for i,mat in enumerate(P['materials']):
    C.setFillColor(HexColor(mat['color']));C.roundRect((14+i*49)*mm,(y-22)*mm,43*mm,12*mm,2*mm,fill=1,stroke=0)
text(14,y-34,'Svetelný zámer',12,True)
para(14,y-42,185,'Denné mäkké svetlo a teplé lokálne svetlá súčasne. LED má približovať vzhľad okolo 2 700 K; nejde o vypočítaný svetelný návrh. Sklo potrebuje odrazy okolitej krajiny aj čitateľný interiér.',9.6)
text(215,y-34,'Neskoršie externé podklady',12,True)
para(215,y-42,187,'Poly Haven: drevo, kameň, prípadne HDRI. ambientCG: PBR povrchy. Na oboch zdrojoch sú dostupné CC0 aktíva. Každý vybraný súbor treba zapísať s URL, licenciou, autorom a hashom; zoznam zatiaľ nepredstiera výber.',9.6)

viewpage('A16','Kompozičná situácia / záhrada',site_plan(),[
('LEN VIZUÁLNA SCÉNA','Obrys plochy je pracovný rozsah modelu. Nepredstavuje hranicu parcely, osadenie domu ani záhradný projekt.'),
('VRSTVY OBRAZU','Popredie: plot a tráva.<br/>Stred: chodník, záhon, dom.<br/>Bok: ovocný strom.<br/>Pozadie: lúka, členité kopce a les.'),
('KAMERA','Presná 3D poloha CAM A je v parameters.json. Symbol na tejto schéme je posunutý do listu iba pre čitateľnosť; neurčuje súradnice kamery.'),
('NÁHRADY','Stromy a kríky v .blend sú jednoduché objekty. Ich neskoršia náhrada nesmie potichu meniť kameru, mierku a tvar domu.'),
('NÁKLADY NA VÝKON','Najprv nízke počty vzoriek a malé výstupy, potom lepšie aktíva a finálny render. Pracovný súbor má zostať zvládnuteľný aj na 8 GB RAM.')])

page('A17','Blender projekt a opakovateľný pôvod','Bez zásuvných modulov, online závislostí a automaticky spúšťaných skriptov')
rows=[['Kolekcia','Obsah / význam','Istota']]
for row in [('00_REFERENCE','Zabalený pôvodný obrázok a neviditeľná pomôcka','Zdroj dodaný používateľom'),('10_ENVELOPE','Sokel, steny, vodorovné a zvislé drevo','Odhad geometrie'),('20_ROOF','Strešné roviny, pásy krytiny, podhľad, komín','Odhad geometrie'),('30_GLAZING','Skutočné sklenené plochy a samostatné profily','Odhad geometrie'),('40_ENTRY_DETAILS','Dvere, lavica, portál, drevo a svietidlá','Odhad / náhrady'),('50_INTERIOR_PROXY','Priečky, jednoduchý nábytok, krb a svetelný kruh','Navrhnuté náhrady'),('60_LIGHTS','Procedurálna obloha, slnko a lokálne svetlá','Pracovné svetlo'),('70_SITE','Terén, schody, chodník, plot a záhony','Pracovná kompozícia'),('80_CAMERAS','CAM_A_REFERENCE','Neodsúhlasený prvý odhad'),('90_VEGETATION_PROXY','Stromy, kríky a kvety','Náhrady na výmenu')]:rows.append(row)
y=table(14,241,392,rows,[74,222,96],9)
para(14,y-10,188,'<b>Primárny pracovný súbor:</b> blender/kysucka_chata_seed.blend. Vytvorený a overený v Blenderi 4.3.2. V novšej lokálnej verzii najprv otvoriť ako kópiu. Pri spustení netreba povoľovať Python auto-run.',9.3)
para(216,y-10,188,'<b>Zdroj:</b> model/parameters.json + scripts/design.py + scripts/build_scene.py. Obnova štandardne zapisuje work/rebuild.blend. Súbor .blend je samostatne upraviteľný, ale ručné zmeny sa samy nevrátia do JSON.',9.3)

page('A18','Postup ladenia a prijímanie výsledkov','Každý celok má jeden hlavný výsledok. Toto je odporúčané poradie, nie automatické povolenie práce.')
rows=[['Poradie','Ohraničený výsledok','Dôkaz pred ďalším krokom','Nepridávať zatiaľ']]
for row in [('1','Lokálne prostredie + pripojenie Worker → Blender + kamera','Lokálne otvorenie, verzia, čitateľný výstup, rovnaký záber','Nové aktíva, zmeny štýlu, ďalšie kamery'),('2','Silueta a rytmus otvorov','Sivý render + prekrytie s referenciou','Rastliny, dekorácie, efekty'),('3','Strecha, drevo, sklo a kameň','Farebný render a označené rozdiely','Zmena prijatej geometrie'),('4','Denný interiér a teplé svetlo','Viditeľný interiér bez prepálených svetiel','Nová dispozícia mimo odsúhlaseného rozsahu'),('5','Terén, záhrada a pozadie','Rovnaká kamera; primerané aktíva a výkon','Náhodné importy nejasného pôvodu'),('6','Finálny obraz a odovzdanie','Kontrola detailov v plnom rozlíšení, zabalené dáta','Architektonické tvrdenia bez overenia')]:rows.append(row)
y=table(14,241,392,rows,[22,113,137,120],9.2)
text(14,y-15,'Porovnanie s referenciou',12,True)
para(14,y-24,188,'Sledovať polohu vrcholu štítu, oba rohy okapu, päty stien, os dverí, hornú a dolnú hranu okna, komín a členenie skla. Porovnávať v pomerných súradniciach obrázka (u, v), nie podľa dojmu z rôznych kamier.',9.6)
text(216,y-15,'Subjektívne prijatie zostáva na Michalovi',12,True)
para(216,y-24,188,'Pri každom vizuálnom kroku možno označiť: 1 silueta, 2 kamera, 3 otvory, 4 materiály, 5 svetlo, 6 prostredie ako PASS / FAIL / NOT TESTED. Technické kontroly nenahrádzajú tvoje posúdenie podobnosti.',9.6)

page('A19','Skutočný počiatočný render S00','Render vznikol z dodaného .blend. Je to kontrola štartovacieho modelu, nie hotová vizualizácia.')
preview=ROOT/'previews/camera_a_material.png'
if preview.exists():imagefit(preview,14,43,270,202.5)
else:para(14,225,270,'Render zatiaľ nevytvorený. Pred odovzdaním sa musí doplniť.',14)
notes([('ÚČEL NÁHĽADU','Overiť, že projekt sa otvorí, vygeneruje obraz a má základné čitateľné prvky. Neznamená to prijatie podobnosti.'),
('KAMERA A','Poloha (27,500; -15,500; 1,700) m.<br/>Cieľ (7,450; 3,150; 1,700) m.<br/>Ohnisko 50 mm / senzor 36 mm.<br/>Zvislý posun 0,170; pomer 4 : 3.'),
('ZNÁME ROZDIELY','Kamera potrebuje kalibráciu. Krajina, rastliny, nábytok, drevo a sklo sú pracovné náhrady. Materiály nemajú finálne textúry.'),
('DÔKAZ','Blender 4.3.2; CPU Cycles. Konkrétne rozlíšenie, vzorky a kontrola zabalených dát sú uložené pri náhľade v JSON.'),
('NASLEDUJÚCI KROK','Čerstvý Planner v Cursor Plan Mode overí lokálne podmienky a pripraví jediný rozhodnuteľný postup.')])

page('A20','Otvorené rozhodnutia a odovzdanie ďalej','K architektovi až po vizuálnom odsúhlasení - podľa aktuálneho rozhodnutia Michala')
rows=[['Oblasť','Stav S00','Kto / kedy rozhodne']]
for row in [('Absolútna mierka','14,4 × 8,4 m je pracovná voľba, nie zameranie','Michal po prvých zladených pohľadoch'),('Tvar a kamera','Prvý odhad, bez subjektívneho prijatia','Michal + Orchestrator z renderu a referencie'),('Dispozícia a skryté strany','Navrhnuté pre celistvý model','Neskôr podľa potrieb; prípadne architekt'),('Materiálové výrobky','Žiadna konkrétna krytina ani obklad','Po prijatí geometrie'),('Nosný systém a skladby','Neriešené','Architekt / projektanti v samostatnej fáze'),('Pozemok a orientácia','Neznáme; vizuálne prostredie je vymyslené','Po výbere skutočného pozemku'),('Energetika, technológie a bezpečnosť','Bez preverenia; model nič netvrdí','Samostatná odborná fáza, ak sa bude stavať'),('Autorské a licenčné zdroje','Vstupný obrázok od používateľa, vlastná procedurálna scéna','Externé aktíva evidovať pri ich výbere')]:rows.append(row)
y=table(14,241,392,rows,[77,171,144],9.3)
text(14,y-15,'Čo potom dostane architekt',12,True)
para(14,y-24,188,'Vybraný finálny pohľad, tento pracovný balík po aktualizácii, rozmery a potreby potvrdené Michalom, zoznam zámerne zachovaných motívov a otvorené rozhodnutia. Architekt nebude musieť spätne hádať, čo je predstava a čo overený fakt.',9.5)
text(216,y-15,'Zdrojové odkazy',12,True)
para(216,y-24,188,'AP: https://github.com/cisarik/ap<br/>Overený pin: d7023cf037f6d17885c3ede5c04812c61640da50<br/>Materiály neskôr: https://polyhaven.com/license<br/>https://ambientcg.com/<br/>Podrobnosti, pôvod a kontrolné súčty: SOURCES.md a manifest/.',9.2)
C.save()
cad_exports()
(OUT/'computed_metrics.json').write_text(json.dumps(m,ensure_ascii=False,indent=2))
print('DOCS_OK',PAGE,'pages',len(all_drawings()),'views')

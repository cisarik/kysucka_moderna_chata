"""Shared, dependency-free seed geometry. Metres in memory; DXF exports mm.
Classification: durable operational source. Consumer: PDF/CAD/Blender builders.
Canonical numeric owner: model/parameters.json. No architectural approval implied.
"""
from pathlib import Path
import json, math
ROOT = Path(__file__).resolve().parents[1]
P = json.loads((ROOT / 'model/parameters.json').read_text())
B = P['building']
L, W, F, E, R = (B[k] for k in ['length','width','floor_z','wall_plate_z','ridge_z'])

def roof_z(y):
    return R - abs(y-W/2) * (R-E)/(W/2)

def metrics():
    rooms = [(r['id'],r['name'],round((r['rect'][2]-r['rect'][0])*(r['rect'][3]-r['rect'][1]),3)) for r in P['rooms']]
    return dict(gross_total=L*W,gross_enclosed=(L-B['wood_bay_length'])*W,
                covered_bay=B['wood_bay_length']*W,net_rooms=sum(r[2] for r in rooms),
                roof_angle=math.degrees(math.atan((R-E)/(W/2))),
                roof_area=2*(L+2*B['roof_gable_overhang'])*(W/2+B['roof_eave_overhang'])*math.sqrt(1+((R-E)/(W/2))**2),
                rooms=rooms)

class Drawing:
    def __init__(self, name, bounds, scale=75):
        self.name=name; self.bounds=bounds; self.scale=scale; self.items=[]
    def line(self,a,b,layer='OUTLINE'):
        self.items.append(('line',a,b,layer))
    def poly(self,pts,layer='OUTLINE',fill=None,close=True):
        self.items.append(('poly',pts,layer,fill,close))
    def rect(self,x,y,w,h,layer='OUTLINE',fill=None):
        self.poly([(x,y),(x+w,y),(x+w,y+h),(x,y+h)],layer,fill)
    def text(self,x,y,s,h=.18,layer='TEXT',anchor='middle'):
        self.items.append(('text',(x,y),s,h,layer,anchor))
    def circle(self,x,y,r,layer='FURNITURE'):
        self.items.append(('circle',(x,y),r,layer))
    def door(self,x,y,w,sgn=1):
        self.line((x,y),(x,y+sgn*w),'DOORS')
        pts=[(x+w*math.cos(a),y+sgn*w*math.sin(a)) for a in [i*math.pi/2/20 for i in range(21)]]
        self.poly(pts,'DOORS',None,False)
    def dimh(self,a,b,y,ref_y,label=None):
        for x in [a,b]:
            self.line((x,ref_y),(x,y+.12),'DIM')
            self.line((x-.07,y-.07),(x+.07,y+.07),'DIM')
        self.line((a,y),(b,y),'DIM');self.text((a+b)/2,y+.10*self.scale/75,label or f'{(b-a)*1000:.0f}',.19*self.scale/75,'DIM')
    def dimv(self,a,b,x,ref_x,label=None):
        for y in [a,b]:
            self.line((ref_x,y),(x-.12,y),'DIM');self.line((x-.07,y-.07),(x+.07,y+.07),'DIM')
        self.line((x,a),(x,b),'DIM');self.text(x-.14*self.scale/75,(a+b)/2,label or f'{(b-a)*1000:.0f}',.19*self.scale/75,'DIM','end')
    def level(self,x,z,txt):
        self.poly([(x,z),(x+.14,z+.10),(x+.28,z)],'DIM')
        self.line((x,z),(x+.9,z),'DIM');self.text(x+.31,z+.09,txt,.16,'DIM','start')

COLORS={'OUTLINE':'#253a40','WALL':'#253a40','GLASS':'#2e93a0','WOOD':'#a67c4b','STONE':'#9b978c','ROOF':'#495764','DIM':'#647c85','GRID':'#98acb2','TEXT':'#203942','FURNITURE':'#91a4a8','PROPOSED':'#b08457','LANDSCAPE':'#6e9161','DOORS':'#516c75','HIDDEN':'#aeb8ba','LIGHT':'#d7a556'}

def base_plan(furniture=False):
    d=Drawing('03_podorys' if not furniture else '04_dispozicna_studia',(-1.9,-3.1,17.8,10.3))
    t=B['wall_thickness'];bay=B['wood_bay_length']
    # Front and rear wall segments retain exact breaks for the declared openings.
    for side,y in [('front',0),('rear',W-t)]:
        ops=sorted([o for o in P['openings'] if o['side']==side],key=lambda x:x['start'])
        last=bay
        for o in ops:
            a=o['start'];b=a+o['width']
            if a>last:d.rect(last,y,a-last,t,'WALL','#dbe2e3')
            d.line((a,y+t/2),(b,y+t/2),'GLASS' if o['id'].startswith('W') else 'DOORS')
            if o['id'].startswith('W'):
                d.line((a,y+t*.3),(b,y+t*.3),'GLASS');d.line((a,y+t*.7),(b,y+t*.7),'GLASS')
            elif side=='front':d.door(a,t,o['width'],1)
            d.text((a+b)/2,y+(-.5 if side=='front' else .5),o['id'],.2,'TEXT')
            last=b
        if last<L:d.rect(last,y,L-last,t,'WALL','#dbe2e3')
    d.rect(bay,t,t,W-2*t,'WALL','#dbe2e3')
    d.rect(L-.15,0,.15,W,'GLASS','#d9eff1')
    for y in B['gable_mullions_y']:d.rect(L-.20,y-.0375,.20,.075,'WALL','#354f56')
    for r in P['partitions']:
        x,y,x1,y1=r;d.rect(x,y,x1-x,y1-y,'PROPOSED','#f0e5d8')
    for o in P['interior_doors']:d.door(o['x'],o['y'],o['width'],o['swing'])
    d.rect(0,0,bay,W,'HIDDEN')
    for x in [.12,bay-.12]:d.rect(x-.09,0,.18,.18,'WOOD','#b89262')
    d.rect(.3,.35,1.8,.8,'WOOD','#ead7b9');d.text(1.2,1.55,'DREVO',.20)
    d.text(1.2,4.5,'OTVORENY',.19);d.text(1.2,4.14,'PRISTRESOK',.19)
    for i in range(3):d.rect(6.7,-1.05+i*.35,2.35,.35,'STONE')
    d.rect(0,-.65,6.7,.65,'STONE');d.rect(9.05,-.65,L-9.05,.65,'STONE')
    d.line((-.55,-.85),(L+.55,-.85),'HIDDEN');d.line((-.55,W+.85),(L+.55,W+.85),'HIDDEN')
    for r in P['rooms']:
        x,y,x1,y1=r['rect'];cx=(x+x1)/2;cy=(y+y1)/2
        d.text(cx,cy+.16,r['id'],.26)
        d.text(cx,cy-.18,f"{(x1-x)*(y1-y):.2f} m2",.17)
    if furniture:add_furniture(d)
    else:
        d.dimh(0,L,-2.45,0);d.dimh(0,bay,-1.9,0);d.dimh(bay,L,-1.9,0)
        d.dimv(0,W,-.9,0);d.dimh(bay,bay+t,9.5,W,'300');d.dimh(bay+t,L-t,9.5,W)
        d.dimv(.3,3.2,16.0,L);d.dimv(3.2,4.65,16.,L);d.dimv(4.65,8.1,16.,L)
        for a,b in [(2.7,5.65),(5.8,8.65),(8.8,14.1)]:d.dimh(a,b,7.65,8.1)
        d.line((10.,-.3),(10.,8.65),'GRID');d.text(10.,8.9,'A-A',.20)
        d.line((2.1,4.2),(14.8,4.2),'GRID');d.text(15.05,4.16,'B-B',.20)
    return d

def add_furniture(d):
    d.rect(3.0,6.0,1.6,2.,'FURNITURE');d.rect(3.,7.55,1.6,.35,'FURNITURE')
    d.rect(6.2,6.0,1.6,2.,'FURNITURE');d.rect(6.2,7.55,1.6,.35,'FURNITURE')
    d.rect(2.9,.55,.9,.9,'FURNITURE');d.circle(4.5,.9,.24);d.rect(4.5,2.,.5,.8,'FURNITURE')
    d.rect(5.5,.6,.85,.75,'FURNITURE');d.circle(5.95,1.0,.3)
    d.rect(9.25,.85,3.0,1.,'FURNITURE');d.rect(9.3,2.35,1.4,.7,'FURNITURE')
    d.rect(12.0,5.3,1.1,2.0,'FURNITURE')
    for y in [5.6,6.4,7.2]:
        for x in [11.55,13.3]:d.rect(x,y,.40,.44,'FURNITURE')
    d.rect(9.05,7.45,3.7,.55,'FURNITURE');d.rect(9.05,6.3,.55,1.15,'FURNITURE')
    c=B['chimney'];d.rect(c['x']-.4,c['y']-.4,.8,.8,'STONE','#d6d2c7')

def roof_plan():
    d=Drawing('05_strecha',(-1.9,-2.8,17.8,11.0))
    a=B['roof_gable_overhang'];h=B['roof_eave_overhang']
    d.rect(-a,-h,L+2*a,W+2*h,'ROOF','#e1e7eb');d.rect(0,0,L,W,'HIDDEN')
    d.line((-a,W/2),(L+a,W/2),'ROOF')
    for i in range(1,13):
        y=-h+i*(W+2*h)/13
        if abs(y-W/2)>.15:d.line((-a,y),(L+a,y),'GRID')
    c=B['chimney'];d.rect(c['x']-.4,c['y']-.4,.8,.8,'STONE','#d4cdbb')
    d.text(c['x'],c['y']+.8,'K01 KOMIN',.20)
    for y in [1.4,7.0]:
        d.line((5,W/2),(5,y),'DIM');d.text(5.5,y,'45 deg',.20)
    d.dimh(-a,L+a,-2.15,-h);d.dimv(-h,W+h,-1.2,-a)
    d.text(7.2,10,'PRESAH OKAPU 850 / STITU 550',.23)
    return d

def long_elevation(rear=False):
    d=Drawing('08_zadna_fasada' if rear else '06_vstupna_fasada',(-1.0,-1.4,18.,9.2))
    bay=B['wood_bay_length'];x0=-.55;x1=L+.55
    d.line((-1,0),(L+1,0),'LANDSCAPE');d.rect(0,.2,L,.25,'STONE','#d0cbc0')
    d.rect(bay,F,L-bay,E-F,'WOOD','#f3e7d3')
    for z in [F+i*.22 for i in range(1,13)]:d.line((bay,z),(L,z),'WOOD')
    for x in [.12,bay-.12]:d.rect(x-.09,F,.18,E-F,'WOOD','#b78850')
    d.poly([(x0,roof_z(-.85)),(x1,roof_z(-.85)),(x1,R),(x0,R)],'ROOF','#e1e7eb')
    for z in [roof_z(-.85)+i*.36 for i in range(1,15)]:
        if z<R:d.line((x0,z),(x1,z),'GRID')
    c=B['chimney'];d.rect(c['x']-.4,roof_z(c['y'])-.1,.8,c['top_z']-.35-roof_z(c['y'])+.1,'STONE','#c6c2b6')
    d.rect(c['x']-.5,c['top_z']-.11,1.,.11,'ROOF','#a3acb1')
    for o in P['openings']:
        if o['side']!=('rear' if rear else 'front'):continue
        z=F+o['sill'];d.rect(o['start'],z,o['width'],o['height'],'GLASS' if o['id'].startswith('W') else 'DOORS','#d4ebec' if o['id'].startswith('W') else '#535751')
        d.text(o['start']+o['width']/2,z+o['height']+.17,o['id'],.20)
    if not rear:
        d.rect(6.71,F,.48,B['entry_stone_top_z']-F,'STONE','#c6c2b6');d.rect(8.54,F,.48,B['entry_stone_top_z']-F,'STONE','#c6c2b6')
        d.rect(10.25,F+.395,2.1,.17,'STONE','#cbc8bb');d.circle(11.3,F+1.65,.42,'WOOD')
        d.rect(.3,F,1.8,1.6,'WOOD','#b7905c');d.line((0,roof_z(-.85)-.08),(L,roof_z(-.85)-.08),'LIGHT')
    d.dimh(0,L,-.85,0)
    for z,txt in [(F,'+0.450'),(E,'+3.250'),(R,'+7.450')]:d.level(15.6,z,txt)
    return d

def gable_elevation(other=False,section=False):
    name='10_priecny_rez' if section else ('09_opacny_stit' if other else '07_preskleny_stit')
    d=Drawing(name,(-1.3,-1.0,11.5,9.1),50)
    d.line((-1,0),(W+1,0),'LANDSCAPE');d.rect(0,.2,W,.25,'STONE','#ccc8ba')
    d.poly([(0,F),(W,F),(W,E),(W/2,R),(0,E)],'WOOD','#f0e0c5')
    if not other and not section:
        d.rect(.15,F,8.1,B['gable_glass_base_top_z']-F,'GLASS','#d4ebec')
        yl=B['gable_upper_glass_y_min'];yr=B['gable_upper_glass_y_max'];z0=B['gable_glass_base_top_z']
        d.poly([(yl,z0),(yr,z0),(yr,roof_z(yr)-.12),(W/2,R-.12),(yl,roof_z(yl)-.12)],'GLASS','#d4ebec')
        for y in B['gable_mullions_y']:
            top=roof_z(y)-.1 if yl<=y<=yr else z0
            d.rect(y-.0375,F,.075,top-F,'WALL','#304b52')
        d.line((.1,z0),(W-.1,z0),'WALL')
    if section:
        d.rect(0,F,.3,E-F,'WALL','#40535a');d.rect(W-.3,F,.3,E-F,'WALL','#40535a')
        d.rect(.3,F,W-.6,.04,'STONE')
        d.text(4.2,2.2,'OTVORENY OBJEM',.23);d.text(4.2,1.8,'BEZ OBYTNEHO PODKROVIA',.18)
        d.line((0,E),(W,E),'HIDDEN')
        d.dimv(F,R,9.4,W,'7000');d.dimv(F,E,-.8,0,'2800')
    d.poly([(-.85,roof_z(-.85)),(W/2,R),(W+.85,roof_z(W+.85))],'ROOF',None,False)
    d.poly([(-.85,roof_z(-.85)+.16),(W/2,R+.16),(W+.85,roof_z(W+.85)+.16)],'ROOF',None,False)
    d.dimh(0,W,-.65,0)
    for z,txt in [(0,'0.000 TEREN'),(F,'+0.450'),(E,'+3.250'),(R,'+7.450')]:d.level(9.5,z,txt)
    return d

def long_section():
    d=Drawing('11_pozdlzny_rez',(-1,-1.3,18,9.2),75)
    d.line((-1,0),(L+1,0),'LANDSCAPE');d.rect(0,.2,L,.25,'STONE','#bdb9ae')
    d.rect(2.4,F,.3,E-F,'WALL','#40535a');d.rect(8.65,F,.15,2.6,'PROPOSED','#e5ceb4')
    d.line((-.55,R),(L+.55,R),'ROOF');d.line((-.55,R+.16),(L+.55,R+.16),'ROOF')
    d.line((2.4,E),(L,E),'HIDDEN')
    c=B['chimney'];d.rect(c['x']-.4,F,.8,c['top_z']-F,'STONE','#c6c2b6')
    d.line((L,F),(L,R),'GLASS');d.line((L-.1,F),(L-.1,R),'GLASS')
    d.text(1.2,1.5,'PRISTRESOK',.18);d.text(5.5,1.7,'IZBY / ZAZEMIE',.23);d.text(10.8,2.,'DENNA ZONA',.23)
    d.text(8.0,5.5,'ZATIAL BEZ STROPU A KROVU',.24);d.text(8.0,5.05,'REZ VIZUALNEHO OBALU, NIE STATICKY NAVRH',.17)
    d.dimh(0,L,-.85,0)
    for z,txt in [(F,'+0.450'),(E,'+3.250'),(R,'+7.450')]:d.level(15.6,z,txt)
    return d

def all_drawings():
    return [datums(),base_plan(),base_plan(True),roof_plan(),long_elevation(),gable_elevation(),long_elevation(True),gable_elevation(True),gable_elevation(section=True),long_section(),eave_detail(),entry_detail(),site_plan()]

def datums():
    d=Drawing('02_suradnice',(-1.8,-2.8,17.8,10.4))
    d.rect(0,0,L,W,'OUTLINE','#edf2f1');d.rect(2.4,0,L-2.4,W,'OUTLINE')
    d.rect(-.55,-.85,L+1.1,W+1.7,'HIDDEN')
    for i,x in enumerate([0,2.4,8.8,L]):
        d.line((x,-1.2),(x,W+1.2),'GRID');d.circle(x,W+1.,.25,'GRID');d.text(x,W+.94,chr(65+i),.23)
    for i,y in enumerate([0,4.2,W]):
        d.line((-1.0,y),(L+1.,y),'GRID');d.circle(-.9,y,.25,'GRID');d.text(-.9,y-.07,str(i+1),.23)
    d.text(8.4,4.9,'UZAVRETY OBAL 12 000 x 8 400',.27)
    d.text(1.2,4.9,'BAY',.23);d.text(1.2,4.4,'2400',.23)
    d.dimh(0,L,-2.1,0);d.dimv(0,W,16.5,L)
    d.line((0,-1.3),(2,-1.3),'DIM');d.text(2.2,-1.35,'X+',.23,'TEXT','start')
    d.line((0,0),(0,2),'DIM');d.text(-.25,2,'Y+',.23,'TEXT','end')
    return d

def eave_detail():
    d=Drawing('13_detail_okapu',(-1.15,1.95,1.25,4.35),15)
    d.rect(0,2.0,.3,1.25,'WALL','#d6e0e2')
    d.poly([(-.85,2.4),(.85,4.1),(.85,3.94),(-.85,2.24)],'ROOF','#c8d1d5')
    d.line((-.85,2.24),(.85,3.94),'WOOD');d.circle(-.77,2.24,.018,'LIGHT')
    d.rect(-.91,2.25,.13,.12,'ROOF','#8b999f')
    d.dimh(-.85,0,2.08,2.4,'850')
    d.line((.35,2.75),(.85,2.75),'HIDDEN');d.text(.86,2.75,'D01 hlava',.075,'TEXT','start')
    d.text(.42,3.18,'+3.250',.075);d.text(-.8,2.51,'+2.400',.075)
    return d

def entry_detail():
    d=Drawing('14_detail_vstupu',(6.3,-.4,13.0,3.85),25)
    d.rect(6.7,F,6.3,E-F,'WOOD','#f4ead9')
    d.rect(6.71,F,.48,B['entry_stone_top_z']-F,'STONE','#c6c2b6');d.rect(8.54,F,.48,B['entry_stone_top_z']-F,'STONE','#c6c2b6')
    d.rect(7.25,F,1.25,2.3,'DOORS','#5c665f')
    d.line((8.30,F+.8),(8.30,F+1.43),'LIGHT')
    d.rect(10.25,F+.395,2.1,.17,'STONE','#cdc7b8');d.circle(11.3,F+1.65,.42,'WOOD')
    for i in range(3):d.rect(6.7,.15*i,2.35,.15,'STONE')
    d.dimh(7.25,8.5,3.55,E,'1250');d.dimv(F,F+2.3,9.55,8.5,'2300')
    d.text(11.3,3.5,'DEKORACIA JE VOLITELNA',.12)
    return d

def site_plan():
    d=Drawing('16_kompozicna_situacia',(-6,-10,23,17),150)
    d.rect(-5,-9,27,25,'HIDDEN');d.rect(0,0,L,W,'OUTLINE','#d8e4e4')
    d.rect(-.55,-.85,L+1.1,W+1.7,'ROOF')
    d.line((-.55,4.2),(L+.55,4.2),'ROOF')
    d.rect(2.4,-1.65,12.3,.9,'LANDSCAPE','#dde9d5')
    d.rect(6.7,-5.8,2.35,4.7,'STONE','#e6e3db')
    d.line((-1.5,-5.8),(16.8,-5.8),'WOOD')
    for x,y,r in [(-.6,-3,1.7),(-3,6,2.1),(17,10,1.6),(-2,12,2.1),(6,14,1.6)]:d.circle(x,y,r,'LANDSCAPE')
    d.circle(21,-7,.3,'DIM');d.line((21,-7),(7.45,3.15),'DIM');d.text(19,-8.1,'CAM A - SCHEMATICKY',.30)
    d.text(7,11.5,'POZADIE: LUKA / LES',.35,'LANDSCAPE')
    d.text(7,-7.8,'PLOT V POPREDI',.30,'WOOD');d.text(7,-9,'BEZ HRANIC PARCELY / BEZ SEVERU',.25)
    return d

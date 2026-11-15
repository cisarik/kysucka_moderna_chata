"""Build the portable S00 visualization seed in Blender 4.3+.
Run only in a separately authorized local Blender process. No network/add-ons.
Default output is work/rebuild.blend, preserving the delivered seed.
"""
import bpy, math, random, sys, json, argparse
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from design import P,B,L,W,F,E,R,roof_z

args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
parser=argparse.ArgumentParser()
parser.add_argument('--output',default=str(ROOT/'work/rebuild.blend'))
opt=parser.parse_args(args)
out=Path(opt.output).resolve();out.parent.mkdir(parents=True,exist_ok=True)
random.seed(137)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
scene.unit_settings.system='METRIC';scene.unit_settings.length_unit='METERS'
scene['seed_revision']='S00'
scene['geometry_authority']='model/parameters.json; unmeasured visualization hypothesis'
scene['architectural_status']='No construction, structure, energy, fire, or planning approval'
scene['reference_fit_status']='Initial camera estimate; visual acceptance pending'
scene['rebuild_policy']='External scripts; no auto-run handlers, drivers or add-ons'

def collection(name):
    c=bpy.data.collections.new(name);scene.collection.children.link(c);return c
cols={n:collection(n) for n in ['00_REFERENCE','10_ENVELOPE','20_ROOF','30_GLAZING','40_ENTRY_DETAILS','50_INTERIOR_PROXY','60_LIGHTS','70_SITE','80_CAMERAS','90_VEGETATION_PROXY']}

def attach(o,col):
    for c in list(o.users_collection):c.objects.unlink(o)
    cols[col].objects.link(o);return o

def basic(name,color,rough=.5,metal=0):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1)
    bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal
    m['asset_origin']='local procedural seed; not a downloaded PBR asset'
    return m

def wood(name,col,vertical=False):
    m=basic(name,col,.46);n=m.node_tree.nodes;l=m.node_tree.links;bs=n.get('Principled BSDF')
    tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=3;tex.inputs['Detail'].default_value=3;tex.inputs['Roughness'].default_value=.68
    coord=n.new('ShaderNodeTexCoord');mapping=n.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY'
    mapping.inputs[1].default_value=(11,11,.55) if vertical else (.55,11,11)
    l.new(coord.outputs['Object'],mapping.inputs[0]);l.new(mapping.outputs['Vector'],tex.inputs['Vector'])
    ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.18;ramp.color_ramp.elements[0].color=(*(x*.50 for x in col),1)
    ramp.color_ramp.elements[1].position=.85;ramp.color_ramp.elements[1].color=(*(min(1,x*1.2) for x in col),1)
    l.new(tex.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs['Color'],bs.inputs['Base Color'])
    bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.19;bump.inputs['Distance'].default_value=.018
    # Retain the seed's authored bump filtering across Blender default changes.
    if 'Filter Width' in bump.inputs:bump.inputs['Filter Width'].default_value=1.0
    l.new(tex.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs[0],bs.inputs['Normal']);return m

specs={v['id']:v for v in P['materials']}
def reference_rgb(name):
    srgb=[int(specs[name]['color'][i:i+2],16)/255 for i in [1,3,5]]
    return tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in srgb)
woodh=wood('MAT_WOOD_H',reference_rgb('MAT_WOOD_H'));woodv=wood('MAT_WOOD_V',reference_rgb('MAT_WOOD_V'),True)
for name in ['MAT_WOOD_H','MAT_WOOD_V']:bpy.data.materials[name].node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=specs[name]['roughness']
dark=basic('MAT_FRAME',reference_rgb('MAT_FRAME'),specs['MAT_FRAME']['roughness'],.55)
stone=basic('MAT_STONE',reference_rgb('MAT_STONE'),specs['MAT_STONE']['roughness'])
concrete=basic('MAT_CONCRETE',reference_rgb('MAT_CONCRETE'),specs['MAT_CONCRETE']['roughness'])
inside=basic('MAT_INTERIOR_PLASTER',(.71,.66,.54),.85)
fabric=basic('MAT_FABRIC',(.54,.50,.40),.9)
floorwood=wood('MAT_FLOOR',(.31,.20,.10))
grass=basic('MAT_GRASS',(.105,.22,.038),.9)
soil=basic('MAT_SOIL',(.085,.064,.039),1)
leaf=basic('MAT_LEAF_PROXY',(.10,.27,.045),.82)
conifer=basic('MAT_CONIFER_PROXY',(.035,.13,.064),.9)
logmat=basic('MAT_LOG_END',(.60,.39,.17),.85)
roofbase=reference_rgb('MAT_ROOF')
roofm=[basic('MAT_ROOF' if i==0 else f'MAT_ROOF_VARIANT_{i}',tuple(v*(1+i*.08) for v in roofbase),specs['MAT_ROOF']['roughness'],.40) for i in range(4)]
glass=basic('MAT_GLASS',(.92,.97,.99),specs['MAT_GLASS']['roughness'])
bs=glass.node_tree.nodes.get('Principled BSDF');bs.inputs['Transmission Weight'].default_value=1;bs.inputs['IOR'].default_value=1.45
led=basic('MAT_LED',(1,.48,.12),.4);bs=led.node_tree.nodes.get('Principled BSDF');bs.inputs['Emission Color'].default_value=(1,.42,.075,1);bs.inputs['Emission Strength'].default_value=5
fire=basic('MAT_FIRE_PROXY',(1,.14,.008),.6);bs=fire.node_tree.nodes.get('Principled BSDF');bs.inputs['Emission Color'].default_value=(1,.14,.008,1);bs.inputs['Emission Strength'].default_value=7
flower=basic('MAT_FLOWER_PROXY',(.30,.10,.37),.8)

def cube(name,loc,dim,mat,col='10_ENVELOPE',bev=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name
    o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if mat:o.data.materials.append(mat)
    attach(o,col)
    if bev:
        mod=o.modifiers.new('Edge softening','BEVEL');mod.width=bev;mod.segments=2
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def mesh(name,verts,faces,mat,col):
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);cols[col].objects.link(o)
    if mat:me.materials.append(mat)
    return o

def beam(name,a,b,width,mat,col='20_ROOF',depth=None):
    a,b=Vector(a),Vector(b);o=cube(name,(a+b)/2,(width,depth or width,(b-a).length),mat,col)
    o.rotation_mode='QUATERNION';o.rotation_quaternion=(b-a).to_track_quat('Z','Y');return o

def cyl(name,loc,rad,depth,mat,col='40_ENTRY_DETAILS',direction=None,verts=12):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=rad,depth=depth,location=loc)
    o=bpy.context.object;o.name=name;o.data.materials.append(mat);attach(o,col)
    if direction:o.rotation_mode='QUATERNION';o.rotation_quaternion=Vector(direction).to_track_quat('Z','Y')
    return o

def sphere(name,loc,scale,mat,col='90_VEGETATION_PROXY',sub=1):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub,radius=1,location=loc);o=bpy.context.object;o.name=name;o.scale=scale
    o.data.materials.append(mat);attach(o,col)
    for p in o.data.polygons:p.use_smooth=True
    return o

def area(name,loc,target,power,color,size=3):
    data=bpy.data.lights.new(name,'AREA');data.energy=power;data.color=color;data.shape='DISK';data.size=size
    o=bpy.data.objects.new(name,data);cols['60_LIGHTS'].objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
    o.visible_camera=False;o.visible_glossy=False;o.visible_transmission=False
    return o

# Base and shell. No hidden automatic operations or imported executable assets.
cube('BASE_slab',(L/2,W/2,(F+B['slab_bottom_z'])/2),(L,W,F-B['slab_bottom_z']),concrete,bev=.025)
cube('FLOOR_interior',((L+2.4)/2,W/2,F+.022),(L-2.4-.12,W-.12,.044),floorwood)
cube('WALL_left_closed',(2.55,W/2,(F+E)/2),(.30,W,E-F),inside)
for side,y in [('front',.15),('rear',W-.15)]:
    openings=[o for o in P['openings'] if o['side']==side]
    # Core strips at all opening height boundaries; no fake window on a solid wall.
    levels=sorted({F,E,*[F+o['sill'] for o in openings],*[F+o['sill']+o['height'] for o in openings]})
    for j,(z0,z1) in enumerate(zip(levels,levels[1:])):
        if z1<=z0:continue
        spans=[(2.4,L)]
        for o in openings:
            if F+o['sill']<=(z0+z1)/2<=F+o['sill']+o['height']:
                new=[]
                for a,b in spans:
                    if a<o['start']:new.append((a,min(b,o['start'])))
                    if b>o['start']+o['width']:new.append((max(a,o['start']+o['width']),b))
                spans=[(a,b) for a,b in new if b-a>.001]
        for k,(a,b) in enumerate(spans):cube(f'WALL_{side}_{j}_{k}',((a+b)/2,y,(z0+z1)/2),(b-a,.30,z1-z0),inside)
    # Horizontal facing boards with the same real holes.
    z=F+.01;row=0
    while z<E-.01:
        top=min(z+.205,E-.01);spans=[(2.4,L)]
        # Split each board vertically around opening boundaries for accurate reveals.
        breaks=sorted({z,top,*[q for o in openings for q in [F+o['sill'],F+o['sill']+o['height']] if z<q<top]})
        for za,zb in zip(breaks,breaks[1:]):
            spans=[(2.4,L)]
            for o in openings:
                if F+o['sill']<=(za+zb)/2<=F+o['sill']+o['height']:
                    result=[]
                    for a,b in spans:
                        if a<o['start']:result.append((a,min(b,o['start'])))
                        if b>o['start']+o['width']:result.append((max(a,o['start']+o['width']),b))
                    spans=[s for s in result if s[1]-s[0]>.001]
            for k,(a,b) in enumerate(spans):cube(f'CLADDING_{side}_{row}_{za:.2f}_{k}',((a+b)/2,-.018 if side=='front' else W+.018,(za+zb)/2),(b-a,.060,zb-za),woodh,bev=.007)
        z+=.22;row+=1

# Other gable is an explicit proposed closure, not inferred measured design.
mesh('GABLE_other_proposed',[(2.4,0,E),(2.4,W,E),(2.4,W/2,R)],[(0,1,2)],woodv,'10_ENVELOPE')

# Window/door assemblies.
for o in P['openings']:
    isfront=o['side']=='front';y=-.06 if isfront else W+.06;x=o['start'];ww=o['width'];z=F+o['sill'];hh=o['height']
    if o['id'].startswith('D'):
        cube(o['id']+'_leaf',(x+ww/2,y,z+hh/2),(ww,.09,hh),dark,'40_ENTRY_DETAILS',.014)
        beam('D01_handle',(x+ww-.14,y-.08,z+.80),(x+ww-.14,y-.08,z+1.43),.023,led,'40_ENTRY_DETAILS')
    else:
        cube(o['id']+'_glass',(x+ww/2,y,z+hh/2),(ww-.10,.023,hh-.10),glass,'30_GLAZING')
        for xx in [x+.035,x+ww-.035,x+ww/2]:cube(o['id']+'_mullion',(xx,y-.025,z+hh/2),(.065,.10,hh),dark,'30_GLAZING')
        for zz in [z+.035,z+hh-.035]:cube(o['id']+'_rail',(x+ww/2,y-.025,zz),(ww,.10,.065),dark,'30_GLAZING')

# Glazed main gable: lower strip and cropped triangular upper panes.
x=L+.012;zmid=B['gable_glass_base_top_z'];lo,hi=B['gable_glass_y_min'],B['gable_glass_y_max']
g=cube('G01_lower_glass',(x,(lo+hi)/2,(F+zmid)/2),(.02,hi-lo,zmid-F),glass,'30_GLAZING')
yl,yr=B['gable_upper_glass_y_min'],B['gable_upper_glass_y_max']
v=[(x,yl,zmid),(x,yr,zmid),(x,yr,roof_z(yr)-.18),(x,W/2,R-.18),(x,yl,roof_z(yl)-.18)]
g=mesh('G02_upper_glass',v,[(0,1,2,3,4)],glass,'30_GLAZING');g.modifiers.new('Pane thickness','SOLIDIFY').thickness=.02
for y in B['gable_mullions_y']:
    top=roof_z(y)-.12 if yl<=y<=yr else zmid
    cube(f'GABLE_mullion_{y:.3f}',(L+.055,y,(F+top)/2),(.13,.075,top-F),dark,'30_GLAZING')
for y in [yl,yr]:cube(f'GABLE_upper_edge_{y}',(L+.055,y,(zmid+roof_z(y)-.18)/2),(.13,.075,roof_z(y)-.18-zmid),dark,'30_GLAZING')
cube('GABLE_horizontal_transom',(L+.055,W/2,zmid),(.13,W,.12),dark,'30_GLAZING')
for yy0,yy1 in [(0,yl),(yr,W)]:
    y=yy0
    while y<yy1-.001:
        y1=min(y+.17,yy1);mesh(f'GABLE_timber_{y:.2f}',[(L+.035,y,zmid),(L+.035,y1,zmid),(L+.035,y1,roof_z(y1)-.11),(L+.035,y,roof_z(y)-.11)],[(0,1,2,3)],woodv,'10_ENVELOPE');y+=.18

# Roof: lightweight grouped tiles, underside, gable fascia and LED.
a=B['roof_gable_overhang'];h=B['roof_eave_overhang'];x0,x1=-a,L+a
for s,(ya,yb) in enumerate([(-h,W/2),(W/2,W+h)]):
    verts=[(x0,ya,roof_z(ya)),(x1,ya,roof_z(ya)),(x1,yb,roof_z(yb)),(x0,yb,roof_z(yb))]
    o=mesh('ROOF_underlay_'+str(s),verts,[(0,1,2,3)],roofm[0],'20_ROOF');o.modifiers.new('Roof visual shell','SOLIDIFY').thickness=.12
    under=[(xx,yy,zz-.13) for xx,yy,zz in verts];mesh('SOFFIT_wood_'+str(s),under,[(0,1,2,3)],woodv,'20_ROOF')
    vv=[];ff=[];mi=[];course=B['roof_tile_course']/math.sqrt(1+((R-E)/(W/2))**2)
    y=ya;row=0
    while y<yb-.001:
        yy=min(y+course,yb);xx=x0;col=0
        while xx<x1-.001:
            width=B['roof_tile_width'] if col else (B['roof_tile_width']/2 if row%2 else B['roof_tile_width']);xx1=min(xx+width,x1)
            k=len(vv);gap=.008
            vv.extend([(xx+gap,y+gap,roof_z(y+gap)+.028),(xx1-gap,y+gap,roof_z(y+gap)+.028),(xx1-gap,yy-gap,roof_z(yy-gap)+.028),(xx+gap,yy-gap,roof_z(yy-gap)+.028)])
            ff.append((k,k+1,k+2,k+3));mi.append(random.randrange(4));xx=xx1;col+=1
        y=yy;row+=1
    o=mesh('ROOF_tiles_'+str(s),vv,ff,roofm[0],'20_ROOF')
    for mat in roofm[1:]:o.data.materials.append(mat)
    for poly,ind in zip(o.data.polygons,mi):poly.material_index=ind
    o.modifiers.new('Tile visual thickness','SOLIDIFY').thickness=.014
for xx in [x0,x1]:
    for ya,yb in [(-h,W/2),(W/2,W+h)]:
        beam('FASCIA_gable',(xx,ya,roof_z(ya)-.03),(xx,yb,roof_z(yb)-.03),.16,dark,depth=.19)
        beam('LED_gable',(xx-.045,ya+.09,roof_z(ya+.09)-.15),(xx-.045,yb-.09,roof_z(yb-.09)-.15),.025,led)
beam('RIDGE_cap',(x0,W/2,R+.05),(x1,W/2,R+.05),.15,roofm[0],depth=.20)
for yy in [-h,W+h]:
    beam('FASCIA_eave',(x0,yy,roof_z(yy)-.06),(x1,yy,roof_z(yy)-.06),.16,dark)
    beam('LED_eave',(x0+.06,yy+.05,roof_z(yy)-.13),(x1-.06,yy+.05,roof_z(yy)-.13),.022,led)

# Fireplace and one aligned chimney, visualization-only.
c=B['chimney'];cx,cy=c['x'],c['y'];z0=roof_z(cy)-.1
shaft_top=c['top_z']-.35
cube('CHIMNEY_shaft',(cx,cy,(z0+shaft_top)/2),(.8,.8,shaft_top-z0),stone,'20_ROOF',.015)
for z in [z0+i*.23 for i in range(1,7)]:
    if z<shaft_top:cube('CHIMNEY_course',(cx,cy-.405,z),(.8,.012,.018),concrete,'20_ROOF')
for dx in [-.34,.34]:
    for dy in [-.34,.34]:cube('CHIMNEY_cap_post',(cx+dx,cy+dy,c['top_z']-.23),(.045,.045,.24),dark,'20_ROOF')
cube('CHIMNEY_cap',(cx,cy,c['top_z']-.055),(1.0,1.0,.11),dark,'20_ROOF',.015)
cube('FIREPLACE_stone',(cx,cy,1.7),(.8,.8,2.5),stone,'50_INTERIOR_PROXY',.025)
cube('FIREPLACE_recess',(cx,cy-.408,1.2),(.63,.03,.8),dark,'50_INTERIOR_PROXY')
for i in range(6):
    xx=cx-.24+i*.095
    bpy.ops.mesh.primitive_cone_add(vertices=7,radius1=.06,radius2=.005,depth=.25+random.random()*.15,location=(xx,cy-.44,1.04+random.random()*.05))
    o=bpy.context.object;o.name='FIRE_proxy';o.data.materials.append(fire);attach(o,'50_INTERIOR_PROXY')

# Entry stone surround, bench, three 150 mm risers.
for xx in [6.95,8.78]:
    cube('ENTRY_stone_pier',(xx,-.10,(F+B['entry_stone_top_z'])/2),(.48,.22,B['entry_stone_top_z']-F),stone,'40_ENTRY_DETAILS',.015)
    cube('SCONCE_body',(xx,-.26,1.95),(.10,.08,.27),dark,'40_ENTRY_DETAILS',.008)
    area('SCONCE_wash',(xx,-.29,1.85),(xx,-.1,.7),22,(1,.55,.23),.28)
cube('BENCH_seat',(11.3,-.37,F+.48),(2.1,.65,.17),stone,'40_ENTRY_DETAILS',.03)
cyl('WALL_DECOR_proxy',(11.3,-.10,F+1.65),.42,.04,woodv,'40_ENTRY_DETAILS',direction=(0,1,0),verts=48)
for xx in [10.55,12.05]:cube('BENCH_support',(xx,-.32,F+.20),(.15,.48,.4),dark,'40_ENTRY_DETAILS')
for xx in [.12,2.28]:cube('WOOD_BAY_post',(xx,.08,(F+E)/2),(.18,.20,E-F),woodv,'40_ENTRY_DETAILS',.01)
cube('WOOD_BAY_rack',(1.2,.55,F+.04),(1.9,1.0,.08),dark,'40_ENTRY_DETAILS')
for row in range(8):
    for col in range(10):
        xx=.32+col*.185+(row%2)*.045;zz=F+.13+row*.18
        o=cyl('FIREWOOD_log',(xx,.57,zz),.075+random.random()*.018,.70,logmat,direction=(0,1,0),verts=9)
for i in range(3):
    width=2.35;dep=1.05-i*.35;top=.15*(i+1)
    cube('ENTRY_step_'+str(i+1),(7.875,-dep/2,top/2),(width,dep,top),concrete,'70_SITE',.015)
for xa,xb in [(0,6.7),(9.05,L)]:cube('PORCH_paving',((xa+xb)/2,-.325,.36),(xb-xa,.65,.18),concrete,'70_SITE',.02)
for i in range(8):cube('PATH_slab',(7.875,-1.3-i*.6,.055),(2.1,.55,.11),concrete,'70_SITE',.015)

# Simple furniture proxies are intentionally separate from the enclosure.
cube('SOFA_base',(10.8,1.35,F+.26),(3.0,1.0,.42),fabric,'50_INTERIOR_PROXY',.12)
cube('SOFA_back',(10.8,.94,F+.60),(3.,.20,.75),fabric,'50_INTERIOR_PROXY',.08)
for xx in [9.45,12.15]:cube('SOFA_arm',(xx,1.36,F+.52),(.23,.95,.62),fabric,'50_INTERIOR_PROXY',.08)
cube('COFFEE_table',(10.0,2.7,F+.42),(1.4,.7,.07),woodh,'50_INTERIOR_PROXY',.03)
for xx in [9.5,10.5]:beam('COFFEE_leg',(xx,2.7,F),(xx,2.7,F+.40),.045,dark,'50_INTERIOR_PROXY')
cube('DINING_table',(12.55,6.35,F+.76),(1.1,2.0,.09),woodh,'50_INTERIOR_PROXY',.04)
for xx in [12.15,12.95]:
    for yy in [5.65,7.05]:beam('DINING_leg',(xx,yy,F),(xx,yy,F+.74),.05,dark,'50_INTERIOR_PROXY')
for yy in [5.65,6.35,7.05]:
    for xx in [11.65,13.45]:
        cube('CHAIR_seat',(xx,yy,F+.44),(.43,.45,.07),woodh,'50_INTERIOR_PROXY',.025)
        cube('CHAIR_back',(xx+(-.18 if xx<12 else .18),yy,F+.71),(.06,.45,.55),woodv,'50_INTERIOR_PROXY',.02)
        for dx in [-.15,.15]:
            for dy in [-.15,.15]:beam('CHAIR_leg',(xx+dx,yy+dy,F),(xx+dx,yy+dy,F+.43),.035,dark,'50_INTERIOR_PROXY')
cube('KITCHEN_proxy',(10.9,7.75,F+.45),(3.7,.58,.9),inside,'50_INTERIOR_PROXY',.015)
cube('KITCHEN_worktop',(10.9,7.73,F+.92),(3.8,.65,.055),stone,'50_INTERIOR_PROXY',.01)
for r in P['partitions']:
    x,y,x1,y1=r;cube('PARTITION_proposed',((x+x1)/2,(y+y1)/2,F+1.3),(x1-x,y1-y,2.6),inside,'50_INTERIOR_PROXY')
# Hanging ring as a visual proxy.
bpy.ops.mesh.primitive_torus_add(major_radius=.60,minor_radius=.016,major_segments=40,minor_segments=6,location=(12.55,6.35,3.0))
o=bpy.context.object;o.name='PENDANT_ring_proxy';o.data.materials.append(led);attach(o,'50_INTERIOR_PROXY')
for xx in [12.2,12.9]:beam('PENDANT_suspension',(xx,6.35,3.02),(xx,6.35,5.25),.008,dark,'50_INTERIOR_PROXY')
area('INTERIOR_warm',(12.,4.8,3.2),(13.9,3.4,1.3),200,(1,.64,.34),2.6)
area('DINING_downlight',(12.5,6.35,3.1),(12.5,6.35,.5),110,(1,.60,.29),1.5)

# Low-cost landscape, exact replacements reserved for a later whole.
verts=[];faces=[];nx,ny=45,52
for j in range(ny):
    y=-18+j*2.4
    for i in range(nx):
        x=-45+i*2.5;factor=max(0,min(1,(y-12)/32))
        z=-.055+factor*(5.0+3.8*math.sin(x*.065+y*.06)+2.5*math.sin(x*.11-y*.04))
        verts.append((x,y,z))
for j in range(ny-1):
    for i in range(nx-1):a0=j*nx+i;faces.append((a0,a0+1,a0+nx+1,a0+nx))
o=mesh('SITE_terrain_proxy',verts,faces,grass,'70_SITE')
for p in o.data.polygons:p.use_smooth=True
cube('BED_entry',(8.8,-1.20,-.005),(12.8,.9,.08),soil,'70_SITE',.1)
for i in range(25):
    xx=2.6+i*.47;yy=-1.4+random.uniform(-.25,.3)
    if 6.5<xx<9.2:continue
    sphere('SHRUB_proxy',(xx,yy,.24),(.38,.30,.34),leaf)
    if i%3==0:sphere('FLOWER_proxy',(xx,yy,.52),(.16,.15,.18),flower)
for x,y,zz in [(4.3,-1.65,.65),(12.8,-1.6,.65)]:
    cube('BOLLARD_body',(x,y,zz/2),(.10,.10,zz),dark,'70_SITE',.012)
    cube('BOLLARD_light',(x,y-.06,zz-.12),(.06,.02,.10),led,'70_SITE')
# Foreground fence, kept as its own editable proxy group.
for i in range(26):
    xx=-1.2+i*.68;zz=.75+random.uniform(-.14,.17)
    cube('FENCE_post_proxy',(xx,-5.8,zz/2),(.10,.11,zz),woodv,'70_SITE',.015)
for zz in [.26,.57]:beam('FENCE_rail_proxy',(-1.5,-5.78,zz),(16.8,-5.78,zz),.065,woodh,'70_SITE')
# Background conifers, meshes linked after first template.
tree_parts=[]
for i in range(38):
    xx=random.uniform(-32,37);yy=random.uniform(19,60)
    factor=max(0,min(1,(yy-12)/32));z=-.055+factor*(5+3.8*math.sin(xx*.065+yy*.06)+2.5*math.sin(xx*.11-yy*.04))
    hh=random.uniform(3,7)
    cyl('TREE_trunk_proxy',(xx,yy,z+hh*.30),.08,hh*.6,woodv,'90_VEGETATION_PROXY',verts=6)
    for t in range(4):
        bpy.ops.mesh.primitive_cone_add(vertices=9,radius1=hh*(.23-.035*t),radius2=0,depth=hh*.48,location=(xx,yy,z+hh*(.40+.15*t)))
        ob=bpy.context.object;ob.name='CONIFER_proxy';ob.data.materials.append(conifer);attach(ob,'90_VEGETATION_PROXY')
# Orchard tree proxy at the left edge; a later asset replacement is expected.
tx,ty=-.6,-3.0
beam('APPLE_trunk_proxy',(tx,ty,0),(tx+.1,ty,2.9),.20,woodh,'90_VEGETATION_PROXY')
for i in range(23):
    a=random.random()*math.tau;r=random.uniform(.25,1.6)
    xx=tx+math.cos(a)*r;yy=ty+math.sin(a)*r;zz=2.7+random.uniform(-.2,1.4)
    beam('APPLE_branch_proxy',(tx,ty,2.2),(xx,yy,zz),.055,woodh,'90_VEGETATION_PROXY')
    sphere('APPLE_foliage_proxy',(xx,yy,zz),(.68,.61,.62),leaf,sub=2)

# Lighting and camera. Generated sky is procedural; no HDRI is required.
world=bpy.data.worlds.new('WORLD_procedural_sky');scene.world=world;world.use_nodes=True
n=world.node_tree.nodes;n.clear();sky=n.new('ShaderNodeTexSky');sky.sky_type='NISHITA' if 'NISHITA' in [i.identifier for i in sky.bl_rna.properties['sky_type'].enum_items] else 'SINGLE_SCATTERING';sky.sun_elevation=math.radians(26);sky.sun_rotation=math.radians(228);sky.altitude=.5;sky.air_density=1.1;sky.sun_disc=False
bg=n.new('ShaderNodeBackground');bg.inputs['Strength'].default_value=.26;wo=n.new('ShaderNodeOutputWorld');world.node_tree.links.new(sky.outputs['Color'],bg.inputs['Color']);world.node_tree.links.new(bg.outputs[0],wo.inputs[0])
sun_data=bpy.data.lights.new('SUN_key','SUN');sun_data.energy=2.0;sun_data.angle=math.radians(5)
sun=bpy.data.objects.new('SUN_key',sun_data);cols['60_LIGHTS'].objects.link(sun);sun.rotation_euler=(math.radians(28),math.radians(-28),math.radians(-32))
area('FILL_front',(7,-8,6),(8,2,2),280,(.72,.83,1),7)
cp=P['camera'];camdata=bpy.data.cameras.new(cp['name']);cam=bpy.data.objects.new(cp['name'],camdata);cols['80_CAMERAS'].objects.link(cam)
cam.location=cp['location'];cam.rotation_euler=(Vector(cp['target'])-cam.location).to_track_quat('-Z','Y').to_euler();camdata.lens=cp['lens_mm'];camdata.sensor_width=cp['sensor_width_mm'];camdata.shift_y=cp.get('shift_y',0);camdata.clip_end=500;scene.camera=cam
ref=ROOT/'reference/kysucka_chata_moderna.png'
if ref.exists():
    im=bpy.data.images.load(str(ref));im.name='REF_kysucka_chata_moderna';im.pack()
    camdata.show_background_images=True;back=camdata.background_images.new();back.image=im;back.alpha=.20;back.display_depth='BACK'
    o=bpy.data.objects.new('REF_IMAGE_not_rendered',None);o.empty_display_type='IMAGE';o.data=im;o.empty_display_size=10;o.hide_render=True;o.hide_viewport=True;cols['00_REFERENCE'].objects.link(o)
txt=bpy.data.texts.new('START_HERE.txt');txt.write('KYSUCKA CHATA - S00\n\nOpen README_SK.md beside this file.\nThis is an editable visual seed, not a final visualization or architectural design.\nCamera A is an unaccepted first estimate.\nThe image is packed as REF_kysucka_chata_moderna.\nNo add-ons, internet textures, handlers or auto-run scripts are required.\nPrimary source: model/parameters.json.\nCollections ending PROXY are replaceable.\nRun external scripts only under an explicit local Worker grant.\n')
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=96;scene.cycles.use_denoising=False
scene.cycles.max_bounces=8;scene.cycles.transmission_bounces=6
scene.render.resolution_x=cp['resolution'][0];scene.render.resolution_y=cp['resolution'][1];scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.filepath='//../work/camera_a.png'
scene.view_settings.view_transform='AgX'
scene.render.film_transparent=False
scene.render.threads_mode='FIXED';scene.render.threads=8
for screen in bpy.data.screens:
    for a in screen.areas:
        if a.type=='VIEW_3D':
            a.spaces.active.region_3d.view_perspective='CAMERA';a.spaces.active.clip_end=500
            a.spaces.active.shading.type='MATERIAL';a.spaces.active.overlay.show_overlays=False
# Preserve the original fence draws and all later vegetation before v03 refinement.
from timber_fence_v03 import apply_v03, configure_comparison_render
v03_rng_before = random.getstate()
v03_result = apply_v03(scene, P, ROOT)
assert random.getstate() == v03_rng_before
configure_comparison_render(scene)
print('V03_REFINEMENT', json.dumps(v03_result, sort_keys=True))
from landscape_v04 import apply_v04
v04_rng_before = random.getstate()
v04_result = apply_v04(scene, P, ROOT)
assert random.getstate() == v04_rng_before
print('V04_REFINEMENT', json.dumps(v04_result, sort_keys=True))
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
print('SEED_SAVED',out,'Blender',bpy.app.version_string,'objects',len(scene.objects),'meters',L,W,F,E,R)

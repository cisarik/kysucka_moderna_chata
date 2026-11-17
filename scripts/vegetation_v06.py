"""Owned v06 vegetation. Explicit live/replay invocation; no import side effects."""
import math, random, json, hashlib
from pathlib import Path
import bpy
from mathutils import Vector, Quaternion
from mathutils.bvhtree import BVHTree
from site_v05 import inside_polygon, polygon_distance, SpatialPoints, GrassMask
PLAIN_MAPS={q:'assets/textures/grass/Grass005/Grass005_1K-JPG_'+q+'.jpg' for q in ['Color','Roughness','NormalGL']}


def collection(name,parent=None):
 c=bpy.data.collections.get(name)
 if c is None:c=bpy.data.collections.new(name);c['v06_owned']=True
 assert c.get('v06_owned'),('Unowned collection',name)
 if parent and name not in parent.children:parent.children.link(c)
 if parent is None:c.use_fake_user=True
 return c

def mesh(name,vs,fs,mats=()):
 me=bpy.data.meshes.get(name)
 if me is None:me=bpy.data.meshes.new(name);me['v06_owned']=True
 assert me.get('v06_owned'),name
 me.clear_geometry();me.from_pydata(vs,[],fs);me.update();me.materials.clear()
 for m in mats:me.materials.append(m)
 return me

def obj(name,data,col):
 assert name not in bpy.data.objects,name
 o=bpy.data.objects.new(name,data);o['v06_owned']=True;col.objects.link(o);return o

def rng_for(seed,*keys):
 h=hashlib.blake2b((':'.join(map(str,(seed,)+keys))).encode(),digest_size=8).digest()
 return random.Random(int.from_bytes(h,'big'))

def smooth(a,b,x):
 t=max(0,min(1,(x-a)/(b-a)));return t*t*(3-2*t)

def field(x,y):
 return max(0,min(1,.5+.25*math.sin(x*math.tau/27+.9*math.sin(y*.17))+.16*math.sin(y*math.tau/65-x*.07)+.09*math.sin(x*math.tau/8+y*.39)))

def compress_axis(v,lo,hi,factor):
 if v<lo:return lo+(v-lo)*factor
 if v>hi:return hi+(v-hi)*factor
 return v

def compress_point(x,y,z,spec):
 t=spec.get('landscape_transform')
 if not t:return x,y,z
 x0,x1,y0,y1=t['fixed_core'];f=t['factor'];d=math.hypot(max(x0-x,0,x-x1),max(y0-y,0,y-y1));sz=1-(1-f)*smooth(0,t['join_m'],d)
 return compress_axis(x,x0,x1,f),compress_axis(y,y0,y1,f),t['datum']+(z-t['datum'])*sz

def terrain_v06(scene,spec,parent):
 """Derived compressed terrain; original v05 mesh bytes remain intact."""
 import array
 col=collection('V06_TERRAIN',parent);made=[]
 for source,name in [('SITE_terrain_proxy','V06_TERRAIN_NEAR'),('V05_TERRAIN','V06_TERRAIN_FAR')]:
  src=scene.objects[source];old=bpy.data.meshes.get(name+'_MESH')
  if old:
   assert old.get('v06_owned') and old.users==0
   bpy.data.meshes.remove(old)
  me=src.data.copy();me.name=name+'_MESH';me['v06_owned']=True
  if 'v05_owned' in me:del me['v05_owned']
  xyz=array.array('f')
  for v in src.data.vertices:xyz.extend(compress_point(*(src.matrix_world@v.co),spec))
  me.vertices.foreach_set('co',xyz);me.update();me.normals_split_custom_set([(0,0,0)]*len(me.loops))
  o=obj(name,me,col);made.append(o);src.hide_render=True;src.hide_viewport=True
 # Shared, area-weighted normals at the retained two-mesh seam.
 normals={}
 for o in made:
  shell=o.data.attributes.get('V05_shell')
  for face in o.data.polygons:
   if shell and shell.data[face.index].value:continue
   weighted=face.normal*face.area
   for i in face.vertices:
    key=tuple(round(v,6) for v in o.data.vertices[i].co);normals[key]=normals.get(key,Vector((0,0,0)))+weighted
 for o in made:
  me=o.data;shell=me.attributes.get('V05_shell');values=[]
  for face in me.polygons:
   for li in face.loop_indices:
    key=tuple(round(v,6) for v in me.vertices[me.loops[li].vertex_index].co)
    values.append(normals[key].normalized() if key in normals and not(shell and shell.data[face.index].value) else face.normal)
  me.normals_split_custom_set(values)
 return made

class Surface:
 def __init__(self,scene,original=False):
  self.v=[];self.f=[];self.grid={};self.planes=[]
  names=['SITE_terrain_proxy','V05_TERRAIN'] if original or 'V06_TERRAIN_NEAR' not in scene.objects else ['V06_TERRAIN_NEAR','V06_TERRAIN_FAR']
  for name in names:
   o=scene.objects[name];off=len(self.v);self.v.extend(tuple(o.matrix_world@v.co) for v in o.data.vertices);shell=o.data.attributes.get('V05_shell')
   self.f.extend(tuple(off+i for i in p.vertices) for p in o.data.polygons if not shell or not shell.data[p.index].value)
  self.bvh=BVHTree.FromPolygons(self.v,self.f,all_triangles=True)
  self.extent=[min(v[0] for v in self.v),max(v[0] for v in self.v),min(v[1] for v in self.v),max(v[1] for v in self.v)]
  for i,face in enumerate(self.f):
   a,b,c=[self.v[k] for k in face];den=(b[0]-a[0])*(c[1]-a[1])-(c[0]-a[0])*(b[1]-a[1])
   if abs(den)<1e-12:self.planes.append(None);continue
   ax=((b[2]-a[2])*(c[1]-a[1])-(c[2]-a[2])*(b[1]-a[1]))/den;ay=((b[0]-a[0])*(c[2]-a[2])-(c[0]-a[0])*(b[2]-a[2]))/den;self.planes.append((ax,ay,a[2]-ax*a[0]-ay*a[1]))
   for iy in range(math.floor(min(q[1] for q in [a,b,c])/4),math.floor(max(q[1] for q in [a,b,c])/4)+1):
    for ix in range(math.floor(min(q[0] for q in [a,b,c])/4),math.floor(max(q[0] for q in [a,b,c])/4)+1):self.grid.setdefault((ix,iy),[]).append(i)
 def sample(self,x,y):
  p,n,i,d=self.bvh.ray_cast(Vector((x,y,150)),Vector((0,0,-1)),300)
  assert p is not None,(x,y)
  # Double-precision plane at the exact XY; removes ray-float height noise.
  a,b,c=self.planes[i];return a*x+b*y+c,n,i
 def range_over_box(self,box,origin,normal):
  """Exact extrema of actual piecewise-linear ground minus root tangent plane."""
  x0,x1,y0,y1=box;ox,oy,oz=origin;nx,ny,nz=normal;ids=set()
  for iy in range(math.floor(y0/4),math.floor(y1/4)+1):
   for ix in range(math.floor(x0/4),math.floor(x1/4)+1):ids.update(self.grid.get((ix,iy),()))
  lo=1e20;hi=-1e20;pieces=0
  for i in ids:
   poly=[self.v[k][:2] for k in self.f[i]]
   for axis,bound,greater in [(0,x0,True),(0,x1,False),(1,y0,True),(1,y1,False)]:
    if not poly:break
    out=[];prev=poly[-1];pin=prev[axis]>=bound if greater else prev[axis]<=bound
    for curr in poly:
     cin=curr[axis]>=bound if greater else curr[axis]<=bound
     if cin!=pin:
      t=(bound-prev[axis])/(curr[axis]-prev[axis]);out.append((prev[0]+t*(curr[0]-prev[0]),prev[1]+t*(curr[1]-prev[1])))
     if cin:out.append(curr)
     prev=curr;pin=cin
    poly=out
   if not poly:continue
   a,b,c=self.planes[i];pieces+=1
   for x,y in poly:
    delta=a*x+b*y+c-(oz-(nx*(x-ox)+ny*(y-oy))/nz);lo=min(lo,delta);hi=max(hi,delta)
  assert pieces,box
  return lo,hi,pieces

def bounds(me):
 return [[min(v.co[k] for v in me.vertices),max(v.co[k] for v in me.vertices)] for k in range(3)]

def pose(n,yaw):return tuple((n.to_track_quat('Z','Y')@Quaternion((0,0,1),yaw)).to_euler())

def cameras(scene,spec,surface):
 col=collection('V06_CAMERAS',collection('97_VEGETATION_V06',scene.collection))
 for name,row in spec['cameras'].items():
  if name in scene.objects:continue
  d=bpy.data.cameras.new(name);d['v06_owned']=True;d.lens=row['lens'];d.sensor_width=36;d.clip_end=1000
  o=obj(name,d,col);loc=list(row['location']);target=list(row['target']) if 'target' in row else None
  if row.get('ground_relative'):
   loc[2]+=surface.sample(*loc[:2])[0];target[2]+=surface.sample(*target[:2])[0]
  o.location=loc
  if row.get('copy_inside'):
   src=scene.objects['CAM_V05_VALLEY_INSIDE'];o.rotation_euler=src.rotation_euler;d.sensor_fit=src.data.sensor_fit;d.shift_x=src.data.shift_x;d.shift_y=src.data.shift_y
  else:o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()

def in_trial(x,y,trial):
 if not trial:return True
 if trial=='A':return -42<=x<=-6 and 4<=y<=42
 return (-90<=x<=-20 and 15<=y<=110) or (240<=x<=318)

def edge_depth(x,y,spec):
 best=-1e6
 for points in spec['stands'].values():
  for a,b in zip(points,points[1:]):
   dx=b[0]-a[0];dy=b[1]-a[1];t=max(0,min(1,((x-a[0])*dx+(y-a[1])*dy)/(dx*dx+dy*dy)))
   w=(a[2]+t*(b[2]-a[2]))*(1+.10*math.sin(.043*x+.3*math.sin(.037*y))+.05*math.sin(.071*y+.011*x))
   best=max(best,w-math.hypot(x-a[0]-dx*t,y-a[1]-dy*t))
 for cx,cy,rx,ry in spec['glades']:
  q=math.hypot((x-cx)/rx,(y-cy)/ry)
  if q<1:return -(1-q)*min(rx,ry)
 return best

def valley_clear(x,y,r,spec=None):
 if x<=20:return True
 w=22+.15*(min(x,235)-20)+10
 if x>235:w+=((spec or {}).get('forest',{}).get('far_glade_half_width_m',18)-w)*min(1,(x-235)/35)
 cy=3+(8*math.sin((x-235)*.025) if x>235 else 0)
 return abs(y-cy)>w+r

def instances(prefix,records,col,masters,chunk):
 ng=bpy.data.node_groups.get(prefix+'_GN')
 if ng is None:
  ng=bpy.data.node_groups.new(prefix+'_GN','GeometryNodeTree');ng['v06_owned']=True;ng.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry');ng.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
 assert ng.get('v06_owned');ng.nodes.clear();n=ng.nodes;l=ng.links;inp=n.new('NodeGroupInput');out=n.new('NodeGroupOutput');ci=n.new('GeometryNodeCollectionInfo');ci.inputs['Collection'].default_value=masters;ci.inputs['Separate Children'].default_value=True;ci.inputs['Reset Children'].default_value=True;inst=n.new('GeometryNodeInstanceOnPoints');inst.inputs['Pick Instance'].default_value=True;l.new(inp.outputs['Geometry'],inst.inputs['Points']);l.new(ci.outputs['Instances'],inst.inputs['Instance'])
 for name,kind,port in [('prototype','INT','Instance Index'),('rotation','FLOAT_VECTOR','Rotation'),('scale','FLOAT_VECTOR','Scale')]:
  a=n.new('GeometryNodeInputNamedAttribute');a.data_type=kind;a.inputs['Name'].default_value=name;l.new(a.outputs['Attribute'],inst.inputs[port])
 l.new(inst.outputs['Instances'],out.inputs['Geometry']);chunks={}
 for row in records:chunks.setdefault((math.floor(row[0][0]/chunk),math.floor(row[0][1]/chunk)),[]).append(row)
 for (ix,iy),rows in sorted(chunks.items()):
  name=f'{prefix}_{ix:+04d}_{iy:+04d}';me=mesh(name+'_POINTS',[r[0] for r in rows],[])
  for key,kind,k in [('prototype','INT',1),('rotation','FLOAT_VECTOR',2),('scale','FLOAT_VECTOR',3)]:
   a=me.attributes.get(key) or me.attributes.new(key,kind,'POINT')
   for d,row in zip(a.data,rows):
    if kind=='INT':d.value=row[k]
    else:d.vector=row[k]
  o=obj(name,me,col);o['v06_instances']=len(rows);mod=o.modifiers.new('Linked V06 cover','NODES');mod.node_group=ng
 return len(chunks)

def forest(scene,P,spec,surf,col,trial,actual_surface=None):
 cfg=spec['forest'];masters=collection('V06_MASTER_FOREST');sources=[];bb=[]
 for kind in ['ABIES','MARIANA']:
  for lod in ['LOD0','LOD1']:
   src=next(iter(bpy.data.collections[f'V04_MASTER_{kind}_{lod}'].objects));sources.append(src);bb.append(bounds(src.data))
 for i,src in enumerate(sources):obj('V06_TREE_MASTER_'+str(i),src.data,masters)
 young=next(iter(bpy.data.collections['V04_MASTER_ABIES_YOUNG'].objects));obj('V06_TREE_MASTER_4',young.data,masters);bb.append(bounds(young.data))
 radial=[max(math.hypot(vert.co.x,vert.co.y) for vert in src.data.vertices) for src in sources]+[max(math.hypot(vert.co.x,vert.co.y) for vert in young.data.vertices)]
 witness_cameras=[(c.matrix_world.inverted(),c.data.lens/c.data.sensor_width,c.location.copy()) for c in scene.objects if c.type=='CAMERA']
 records=[];accepted={};root_errors=[];species=[0,0,0];poly=P['site_v05']['garden_polygon'];seed=spec['seed'];candidates=[]
 # Stable two-dimensional dart priorities; global RNG is never sampled.
 for iy in range(-196,221):
  for ix in range(-241,319):
   if not in_trial(ix+.5,iy+.5,trial) or edge_depth(ix+.5,iy+.5,spec)<-2:continue
   rr=rng_for(seed,'tree',ix,iy)
   for j in range(4):candidates.append((rr.random(),ix+rr.random(),iy+rr.random(),rr.random()))
 candidates.sort()
 for priority,x,y,u in candidates:
  depth=edge_depth(x,y,spec)
  if depth<0:continue
  rr=rng_for(seed,'morph',round(x,6),round(y,6));kind=0 if depth<8 or u<(cfg['mid_abies'] if depth<24 else cfg['rear_abies']) else 1
  h=rr.uniform(*cfg['edge_height_m']) if depth<8 else rr.uniform(*cfg['abies_height_m']) if kind==0 else rr.uniform(*cfg['mariana_height_m'])
  lod=1;proto=kind*2+lod;b=bb[proto];sz=h/(b[2][1]-b[2][0]);width_factor=rr.uniform(*cfg['abies_width_scale']) if kind==0 else rr.uniform(*cfg['mariana_width_scale']);sxy=sz*width_factor
  # True radial bounds of both reusable LOD meshes govern overlap and clearance.
  r=max(radial[k]/(bb[k][2][1]-bb[k][2][0]) for k in [kind*2,kind*2+1])*h*width_factor
  if inside_polygon(x,y,poly) or polygon_distance(x,y,poly)<8+r or not valley_clear(x,y,r,spec):continue
  z,n,face=surf.sample(x,y)
  if n.z<math.cos(math.radians(50)):continue
  key=(math.floor(x/5),math.floor(y/5));near=[p for yy in range(key[1]-2,key[1]+3) for xx in range(key[0]-2,key[0]+3) for p in accepted.get((xx,yy),[])]
  if any(math.hypot(x-a,y-bb0)<cfg['crown_spacing_factor']*(r+rad) for a,bb0,rad in near):continue
  if depth<cfg['high_lod_edge_depth_m']:
   factor=spec.get('landscape_transform',{}).get('factor',1);xx,yy,_=compress_point(x,y,z,spec);zz,nn,ff=(actual_surface or surf).sample(xx,yy);centre=Vector((xx,yy,zz+h*factor*.5));maximum_px=0;near=False
   for inverse,fx,eye in witness_cameras:
    q=inverse@centre;distance=-q.z
    if distance>.1 and abs(q.x/distance)*fx<.65 and abs(q.y/distance)*fx<.55:maximum_px=max(maximum_px,1448*fx*2*r*factor/distance)
    near=near or (centre-eye).length<cfg['high_lod_near_m']
   if maximum_px>=cfg['high_lod_crown_px'] or near:
    proto=kind*2;b=bb[proto];sz=h/(b[2][1]-b[2][0]);sxy=sz*width_factor
  accepted.setdefault(key,[]).append((x,y,r));records.append(((x,y,z-b[2][0]*sz-.012),proto,(0,0,rr.random()*math.tau),(sxy,sxy,sz)));species[kind]+=1
  if depth<12 and rr.random()<.11:
   xx=x+rr.uniform(-2,2);yy=y+rr.uniform(-2,2)
   if not(surf.extent[0]<xx<surf.extent[1] and surf.extent[2]<yy<surf.extent[3]):continue
   hh=rr.uniform(1.2,4);zb,nn,_=surf.sample(xx,yy);sc=hh/(bb[4][2][1]-bb[4][2][0]);rad=radial[4]*sc
   if polygon_distance(xx,yy,poly)>8+rad and valley_clear(xx,yy,rad,spec):records.append(((xx,yy,zb-.012),4,(0,0,rr.random()*math.tau),(sc,sc,sc)));species[2]+=1
 if spec.get('landscape_transform'):
  contracted=[];factor=spec['landscape_transform']['factor']
  for point,proto,rot,scale in records:
   x,y,_=compress_point(*point,spec);z,n,face=actual_surface.sample(x,y);sc=tuple(v*factor for v in scale);low=bb[proto][2][0];contracted.append(((x,y,z-low*sc[2]-.006),proto,rot,sc))
  source=scene.objects['V04_YOUNG_03'];xx,yy,_=compress_point(*source.location,spec);zz,nn,ff=actual_surface.sample(xx,yy);sc=tuple(a*factor for a in source.scale);contracted.append(((xx,yy,zz-bb[4][2][0]*sc[2]-.006),4,tuple(source.rotation_euler),sc));species[2]+=1;source.hide_render=True;source.hide_viewport=True
  scene['v06_retained_young03_replacement']=json.dumps({'location':contracted[-1][0],'rotation':contracted[-1][2],'scale':sc,'source':'V04_YOUNG_03'},sort_keys=True)
  records=contracted
 instances('V06_FOREST',records,col,masters,32)
 return records,{'adult_abies':species[0],'adult_mariana':species[1],'young':species[2],'placements':len(records)}

def leaf_material(name,colors):
 m=bpy.data.materials.get(name)
 if m is None:m=bpy.data.materials.new(name);m['v06_owned']=True
 assert m.get('v06_owned');m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;n.clear()
 a=n.new('ShaderNodeAttribute');a.attribute_name='v06_t';r=n.new('ShaderNodeValToRGB');r.color_ramp.elements[0].color=(*colors[0],1);r.color_ramp.elements[1].color=(*colors[1],1);l.new(a.outputs['Fac'],r.inputs[0]);bs=n.new('ShaderNodeBsdfPrincipled');l.new(r.outputs['Color'],bs.inputs['Base Color']);rough=n.new('ShaderNodeMapRange');rough.inputs['To Min'].default_value=.85;rough.inputs['To Max'].default_value=.65;l.new(a.outputs['Fac'],rough.inputs['Value']);l.new(rough.outputs['Result'],bs.inputs['Roughness']);tr=n.new('ShaderNodeBsdfTranslucent');l.new(r.outputs['Color'],tr.inputs['Color']);mix=n.new('ShaderNodeMixShader');mix.inputs[0].default_value=.12;l.new(bs.outputs[0],mix.inputs[1]);l.new(tr.outputs[0],mix.inputs[2]);out=n.new('ShaderNodeOutputMaterial');l.new(mix.outputs[0],out.inputs[0]);return m

def blade(vs,fs,slots,ts,x,y,h,w,bend,angle,twist,segments,slot):
 off=len(vs)
 for j in range(segments+1):
  t=j/segments;cx=x+math.cos(angle)*bend*t*t;cy=y+math.sin(angle)*bend*t*t;z=h*math.sin(math.pi*t/2);aa=angle+math.pi/2+twist*t;ww=w*(1-t)**.8
  for side in [-1,0,1]:vs.append((cx+math.cos(aa)*ww*side/2,cy+math.sin(aa)*ww*side/2,z+(.15*ww if side==0 else 0)));ts.append(t)
 for j in range(segments):
  for k in range(2):fs.append((off+j*3+k,off+j*3+k+1,off+(j+1)*3+k+1,off+(j+1)*3+k));slots.append(slot)

def grass_masters(spec,lawn):
 if not lawn:return meadow_masters(spec)
 cfg=spec['lawn' if lawn else 'meadow']
 col=collection('V06_MASTER_LAWN' if lawn else 'V06_MASTER_MEADOW');mats=[leaf_material('MAT_V06_GREEN',[(.035,.075,.012),(.13,.24,.038)]),leaf_material('MAT_V06_OLIVE',[(.075,.105,.023),(.22,.28,.065)]),leaf_material('MAT_V06_THATCH',[(.12,.085,.025),(.34,.26,.10)])]
 original=next(iter(bpy.data.collections['V04_MASTER_GRASS_MEDIUM_01_0'].objects)).data.materials[0]
 card=bpy.data.materials.get('MAT_V06_MEADOW_CARD')
 if card is None:card=original.copy();card.name='MAT_V06_MEADOW_CARD';card['v06_owned']=True
 mats.append(card);sources=[next(iter(bpy.data.collections[f'V04_MASTER_GRASS_MEDIUM_01_{i}'].objects)).data for i in range(3)]
 desc=[]
 for tier,size in enumerate(cfg['patch_sizes_m']):
  for variant in range(4):
   rr=rng_for(spec['seed'],'lawn' if lawn else 'meadow',tier,variant);vs=[];fs=[];slots=[];ts=[];uvfaces=[]
   count=round(size*size*rr.uniform(*cfg['density_m2'])) if lawn else round(size*size*cfg['density_m2'][tier])
   for k in range(count):
    thatch=rr.random()<cfg['thatch_fraction'];h=rr.uniform(*cfg['thatch_height_m']) if thatch else rr.uniform(*cfg['height_m']);w=rr.uniform(*cfg['width_m'])*(1 if lawn else cfg['width_lod_scale'][tier])
    bend=rr.uniform(*cfg['bend_m']);bend*=min(1,size/.5);x=rr.uniform(-size/2,size/2);y=rr.uniform(-size/2,size/2);sl=2 if thatch or (not lawn and variant==2 and rr.random()<.25) else (1 if rr.random()<(.50 if variant==1 else .18) else 0)
    blade(vs,fs,slots,ts,x,y,h,w,bend,rr.random()*math.tau,rr.uniform(-.52,.52),cfg['segments'],sl)
   # Distributed intermediate atlas leaves and seed heads, never the sole lower cover.
   if not lawn:
    for k in range(math.floor(size*size*12+rr.random())):
     src=sources[k%3];b=bounds(src);h=rr.uniform(.12,.30) if k%3!=1 else rr.uniform(.25,.55);sz=h/(b[2][1]-b[2][0]);xy=min(1,size/.5)*rr.uniform(.9,1.3);a=rr.random()*math.tau;cs=math.cos(a);sn=math.sin(a);x=rr.uniform(-size/2,size/2);y=rr.uniform(-size/2,size/2);off=len(vs)
     vs.extend((x+(v.co.x*cs-v.co.y*sn)*xy,y+(v.co.x*sn+v.co.y*cs)*xy,(v.co.z-b[2][0])*sz) for v in src.vertices);ts.extend((v.co.z-b[2][0])/(b[2][1]-b[2][0]) for v in src.vertices)
     for p in src.polygons:fs.append(tuple(off+i for i in p.vertices));slots.append(3);uvfaces.append((len(fs)-1,[tuple(src.uv_layers.active.data[li].uv) for li in p.loop_indices]))
    for k in range(math.floor(size*size*12+rr.random())):
     x=rr.uniform(-size/2,size/2);y=rr.uniform(-size/2,size/2);h=rr.uniform(.25,.65);blade(vs,fs,slots,ts,x,y,h,.0012,.02,rr.random()*math.tau,0,4,2)
   name=('V06_LAWN_' if lawn else 'V06_MEADOW_')+f'MASTER_{tier:02d}_{variant}';me=mesh(name+'_MESH',vs,fs,mats)
   for p,k in zip(me.polygons,slots):p.material_index=k;p.use_smooth=True
   at=me.attributes.get('v06_t') or me.attributes.new('v06_t','FLOAT','POINT')
   for d,t in zip(at.data,ts):d.value=t
   uv=me.uv_layers.get('UVMap') or me.uv_layers.new(name='UVMap')
   for pi,uvs in uvfaces:
    for li,u in zip(me.polygons[pi].loop_indices,uvs):uv.data[li].uv=u
   roots=[tuple(v.co) for v,t in zip(me.vertices,ts) if t<=.002]
   rb=[[min(q[k] for q in roots),max(q[k] for q in roots)] for k in range(3)];b=bounds(me)
   descriptor={'size':size,'tier':tier,'radius':math.hypot(max(abs(t) for t in b[0]),max(abs(t) for t in b[1])),'root_bounds':rb,'bounds':b,'root_count':len(roots),'triangles':sum(len(p.vertices)-2 for p in me.polygons)}
   me['v06_root_definition']='v06_t <= 0.002; procedural first sections and atlas basal vertices';me['v06_descriptor']=json.dumps(descriptor,sort_keys=True)
   obj(name,me,col);desc.append(descriptor)
 return col,desc

def ground(scene,ROOT,spec):
 keep=collection('V06_RETAINED_GROUND');hold=mesh('V06_GROUND_HOLD',[],[],[bpy.data.materials['MAT_V05_LAWN_BASE'],bpy.data.materials['MAT_V05_MEADOW_BASE']]);obj('V06_GROUND_HOLD',hold,keep)
 mats=[]
 for old in ['MAT_V05_LAWN_BASE','MAT_V05_MEADOW_BASE']:
  name=old.replace('V05','V06');m=bpy.data.materials.get(name)
  if m is None:m=bpy.data.materials[old].copy();m.name=name;m['v06_owned']=True
  for node in m.node_tree.nodes:
   if node.type=='HUE_SAT':node.inputs['Value'].default_value=.92;node.inputs['Saturation'].default_value=.86
   if node.type=='TEX_IMAGE' and node.image and 'Grass005' in node.image.name:
    role=next(q for q in ['Color','Roughness','NormalGL'] if q in node.image.name)
    path=Path(ROOT)/(spec['maps_2k'][role] if spec['texture']=='2K' else PLAIN_MAPS[role])
    im=bpy.data.images.get(path.name)
    if im is None:
     im=bpy.data.images.load(str(path),check_existing=True);im['v06_owned']=True;im.colorspace_settings.name='sRGB' if role=='Color' else 'Non-Color';im.pack()
    node.image=im
  mats.append(m)
 for name in ['SITE_terrain_proxy','V05_TERRAIN','V06_TERRAIN_NEAR','V06_TERRAIN_FAR']:
  if name not in scene.objects:continue
  me=scene.objects[name].data
  for i,m in enumerate(mats):me.materials[i]=m

def scatter_grass(scene,P,spec,surf,col,masters,desc,forest_records,lawn,trial):
 if not lawn:return scatter_meadow(scene,P,spec,surf,col,masters,desc,forest_records,trial)
 poly=P['site_v05']['garden_polygon'];summary=json.loads(scene['site_v05_summary']);fence=summary['fence'].copy();fence['post_points']=[(o.location.x,o.location.y,.1) for o in scene.objects if o.name.startswith(('FENCE_post_proxy','V05_FENCE_POST_','V05_GATE_POST_'))];spatial=SpatialPoints([r[0] for r in forest_records]);mask=GrassMask(scene,P['site_v05'],fence,spatial);mask.trunks=[(o.location.x,o.location.y) for o in scene.objects if o.name in ['V04_ORCHARD','V04_YOUNG_00','V04_YOUNG_01','V04_YOUNG_02','V04_YOUNG_03'] and not o.hide_render];records=[];certificates=[];subdivided=0;support_rejected=0;lost_area=0.;max_spread=0.;proof_pieces=0
 cams=[]
 for c in scene.objects:
  if c.type=='CAMERA' and (c.name.startswith('CAM_V06') or c.name in ['CAM_A_REFERENCE','CAM_V05_ORBIT_NE','CAM_V05_ORBIT_SW','CAM_V05_ORBIT_SE','CAM_V05_OVERVIEW','CAM_V05_VALLEY_INSIDE']):cams.append((c.matrix_world.inverted(),c.data.lens/c.data.sensor_width))
 def tier_at(x,y,z):
  best=0
  for inv,fx in cams:
   q=inv@Vector((x,y,z));d=-q.z
   if d>.1 and abs(q.x/d)*fx<.65 and abs(q.y/d)*fx<.55:best=max(best,.15*1448*fx/d)
  return 0 if best>=4 else 1 if best>=1 else 2
 def projected_box(local_bounds,rotation):
  points=[rotation@Vector((x,y,z)) for x in local_bounds[0] for y in local_bounds[1] for z in local_bounds[2]]
  return [min(p.x for p in points),max(p.x for p in points),min(p.y for p in points),max(p.y for p in points)]
 def place(x,y,size,tier):
  nonlocal subdivided,support_rejected,max_spread,lost_area,proof_pieces
  # Stable jitter and continuous yaw break repeated tile seams without density bands.
  rr=rng_for(spec['seed'],'scatter',lawn,round(x,5),round(y,5),size);variant=rr.randrange(4) if lawn else min(3,int(field(x,y)*4));proto=tier*4+variant;d=desc[proto]
  if not lawn:x+=rr.uniform(-.06,.06)*size;y+=rr.uniform(-.06,.06)*size
  z,n,face=surf.sample(x,y)
  if n.z<math.cos(math.radians(60 if not lawn else 50)):return
  yaw=rr.random()*math.tau;rotation=pose(n,yaw);matrix=__import__('mathutils').Euler(rotation).to_matrix();fb=projected_box(d['bounds'],matrix);radius=max(math.hypot(a,b) for a in fb[:2] for b in fb[2:])
  if lawn:
   if not mask.lawn(x,y,radius):
    if size>.125:subdivide(x,y,size,1)
    return
  else:
   if inside_polygon(x,y,poly) or polygon_distance(x,y,poly)<radius or not mask.clear(x,y,radius):return
   if spatial.nearest(x,y,radius+.25)<radius+.25:return
  rb=projected_box(d['root_bounds'],matrix);box=[x+rb[0],x+rb[1],y+rb[2],y+rb[3]];x0,x1,y0,y1=surf.extent
  if box[0]<x0 or box[1]>x1 or box[2]<y0 or box[3]>y1:return
  lo,hi,pieces=surf.range_over_box(box,(x,y,z),n);span=hi-lo
  if span>.005 and size>.063:
   subdivided+=1;newtier=(1 if size>.125 else 2) if lawn else (1 if size>1 else 0 if size>.5 else 3 if size>.125 else 4);subdivide(x,y,size,newtier);return
  root_headroom=max(0,d['root_bounds'][2][1])/n.z
  if span+root_headroom>.017:support_rejected+=1;lost_area+=size*size;return
  embed=.002+root_headroom;origin=(x,y,z+lo-embed);records.append((origin,proto,rotation,(1,1,1)));certificates.append((lo,hi,embed,span,root_headroom));max_spread=max(max_spread,span);proof_pieces+=pieces
 def subdivide(x,y,size,newtier):
  target=([.5,.125,.0625] if lawn else [.5,1,2,.125,.0625])[newtier];nn=max(1,round(size/target))
  for j in range(nn):
   for i in range(nn):place(x-size/2+(i+.5)*target,y-size/2+(j+.5)*target,target,newtier)
 if lawn:
  x0,x1,y0,y1=-15.5,19.2,-8.62,16.5;step=.5
  for iy in range(math.floor(y0/step),math.ceil(y1/step)):
   for ix in range(math.floor(x0/step),math.ceil(x1/step)):
    x=(ix+.5)*step;y=(iy+.5)*step
    if in_trial(x,y,trial):place(x,y,step,0)
 else:
  x0,x1,y0,y1=surf.extent
  for iy in range(math.ceil((y0+2)/2),math.floor((y1-2)/2)):
   for ix in range(math.ceil((x0+2)/2),math.floor((x1-2)/2)):
    x=(ix+.5)*2;y=(iy+.5)*2
    if not in_trial(x,y,trial) or inside_polygon(x,y,poly):continue
    z,n,_=surf.sample(x,y);t=tier_at(x,y,z)
    if field(x,y)<.11:continue
    size=[.5,1,2][t];nn=round(2/size)
    for j in range(nn):
     for i in range(nn):place(x-1+(i+.5)*size,y-1+(j+.5)*size,size,t)
 chunks=instances('V06_LAWN' if lawn else 'V06_MEADOW',records,col,masters,8 if lawn else 32)
 return {'instances':len(records),'chunks':chunks,'support_subdivisions':subdivided,'support_rejected':support_rejected,'support_rejected_area_m2':lost_area,'max_exact_support_spread':max_spread,'clipped_triangle_pieces':proof_pieces,'root_certificate_max_burial_m':max((c[3]+c[2] for c in certificates),default=0),'root_certificate_max_exposure_m':-.002,'expanded_triangles':sum(desc[r[1]]['triangles'] for r in records)}

def apply_v06(scene,P,ROOT,trial=None):
 before=random.getstate();spec=P['vegetation_v06'];assert spec['seed']==13706;assert trial in [None,'A','B'];assert not bpy.app.is_job_running('RENDER')
 # Remove only generated v06 objects, including off-scene sources; shared data survive.
 for o in list(bpy.data.objects):
  if o.get('v06_owned'):bpy.data.objects.remove(o,do_unlink=True)
 for d in list(bpy.data.cameras):
  if d.get('v06_owned') and d.users==0:bpy.data.cameras.remove(d)
 parent=collection('97_VEGETATION_V06',scene.collection);cols={k:collection('V06_'+k.upper(),parent) for k in ['forest','lawn','meadow']};original_surface=Surface(scene,original=True);terrain_v06(scene,spec,parent);surf=Surface(scene);cameras(scene,spec,surf);bpy.context.view_layer.update()
 for o in scene.objects:
  if o.name.startswith(('V04_FOREST_','V05_FOREST_')):
   hide=in_trial(o.location.x,o.location.y,trial);o.hide_render=hide;o.hide_viewport=hide
  elif o.name.startswith(('V05_LAWN_CHUNK','V05_MEADOW_CHUNK','V05_MEADOW_PART_CHUNK','V04_EDGE_GRASS_')):
   if not trial:o.hide_render=True;o.hide_viewport=True
 frecs,fstats=forest(scene,P,spec,original_surface,cols['forest'],trial,actual_surface=surf)
 ground(scene,ROOT,spec)
 lm,ld=grass_masters(spec,True)
 # Hide old grass chunks intersecting trial to prevent overlapping lower layers.
 if trial:
  for o in scene.objects:
   if o.name.startswith(('V05_LAWN_CHUNK','V05_MEADOW_CHUNK','V05_MEADOW_PART_CHUNK')) and any(in_trial(v.co.x,v.co.y,trial) for v in o.data.vertices):o.hide_render=True;o.hide_viewport=True
 lawn=scatter_grass(scene,P,spec,surf,cols['lawn'],lm,ld,frecs,True,trial);meadow=apply_meadow_v06(scene,P,ROOT,surf=surf,forest_records=frecs,trial=trial)
 scene.camera=scene.objects[P['camera']['name']];scene.cycles.device='GPU' if spec['profile']=='P1' else 'CPU';scene.cycles.denoising_use_gpu=False;scene.cycles.denoising_prefilter='ACCURATE';scene.cycles.denoising_quality='HIGH';bpy.context.view_layer.update();assert before==random.getstate()
 result={'trial':trial,'forest':fstats,'lawn':lawn,'meadow':meadow,'global_rng_unchanged':True,'original_terrain_meshes_unchanged':True,'landscape_transform':spec.get('landscape_transform')};scene['vegetation_v06_summary']=json.dumps(result,sort_keys=True);return result


# Shared meadow-only refinement. No import or module-load scene effects.
def meadow_leaf(vs, fs, slots, ts, x, y, h, width, bend, angle, twist, segments, slot):
    """Folded arching leaf, including basal lean rather than upright stalks."""
    offset = len(vs)
    for j in range(segments + 1):
        t = j / segments
        along = bend * (.65 * t + .35 * math.sin(t * math.pi / 2))
        cross = bend * .10 * math.sin(math.pi * t) * math.sin(twist * 3)
        cx = x + math.cos(angle) * along - math.sin(angle) * cross
        cy = y + math.sin(angle) * along + math.cos(angle) * cross
        z = h * math.sin(1.7 * t) / math.sin(1.7)
        a = angle + math.pi / 2 + twist * t
        w = width * (1 - t) ** .75
        for side in (-1, 0, 1):
            vs.append((cx + math.cos(a) * w * side / 2,
                       cy + math.sin(a) * w * side / 2,
                       z + (.12 * w if side == 0 else 0)))
            ts.append(t)
    for j in range(segments):
        for k in range(2):
            fs.append((offset + j * 3 + k, offset + j * 3 + k + 1,
                       offset + (j + 1) * 3 + k + 1, offset + (j + 1) * 3 + k))
            slots.append(slot)


def meadow_masters(spec):
    cfg = spec['meadow']
    col = collection('V06_MASTER_MEADOW')
    # Existing shared shaders stay byte/semantically unchanged, including lawn.
    mats = [bpy.data.materials[name] for name in
            ['MAT_V06_GREEN', 'MAT_V06_OLIVE', 'MAT_V06_THATCH', 'MAT_V06_MEADOW_CARD']]
    sources = [next(iter(bpy.data.collections[f'V04_MASTER_GRASS_MEDIUM_01_{i}'].objects)).data for i in range(3)]
    descriptors = []
    for tier, size in enumerate(cfg['patch_sizes_m']):
        for variant in range(4):
            rr = rng_for(spec['seed'], 'continuous-meadow-master', tier, variant)
            vs, fs, slots, ts, uvfaces = [], [], [], [], []
            count = max(1, round(size * size * cfg['density_m2'][variant]))
            for k in range(count):
                dry = rr.random() < cfg['thatch_fraction'][variant]
                h = rr.uniform(*(cfg['thatch_height_m'] if dry else cfg['variant_height_m'][variant]))
                w = rr.uniform(*cfg['width_m'])
                bend = h * rr.uniform(*cfg['bend_ratio']) * (1.4 if dry else 1)
                meadow_leaf(vs, fs, slots, ts, rr.uniform(-size/2, size/2), rr.uniform(-size/2, size/2),
                            h, w, bend, rr.random() * math.tau, rr.uniform(-.8, .8),
                            cfg['segments'], 2 if dry else (1 if rr.random() < .28 else 0))
            # Distributed reusable atlas forms supply the middle layer. The
            # low ecological variants remain naturally sparse in taller stems.
            for k in range(math.floor(size * size * cfg['middle_density_m2'][variant] + rr.random())):
                src = sources[k % 3]; b = bounds(src)
                h = rr.uniform(*cfg['middle_height_m']); sz = h / (b[2][1] - b[2][0])
                xy = min(1, size/.5) * rr.uniform(.9, 1.3)
                a = rr.random() * math.tau; cs = math.cos(a); sn = math.sin(a)
                x = rr.uniform(-size/2, size/2); y = rr.uniform(-size/2, size/2); off = len(vs)
                vs.extend((x + (p.co.x*cs-p.co.y*sn)*xy,
                           y + (p.co.x*sn+p.co.y*cs)*xy,
                           (p.co.z-b[2][0])*sz) for p in src.vertices)
                ts.extend((p.co.z-b[2][0])/(b[2][1]-b[2][0]) for p in src.vertices)
                for face in src.polygons:
                    fs.append(tuple(off+i for i in face.vertices)); slots.append(3)
                    uvfaces.append((len(fs)-1, [tuple(src.uv_layers.active.data[li].uv) for li in face.loop_indices]))
            for k in range(math.floor(size * size * cfg['upper_density_m2'][variant] + rr.random())):
                h = rr.uniform(*cfg['upper_tip_height_m'])
                meadow_leaf(vs, fs, slots, ts, rr.uniform(-size/2, size/2), rr.uniform(-size/2, size/2),
                            h, .0012, h * rr.uniform(.08, .20), rr.random()*math.tau, .1, 4, 2)
            name = f'V06_MEADOW_MASTER_{tier:02d}_{variant}'
            me = mesh(name+'_MESH', vs, fs, mats)
            for face, slot in zip(me.polygons, slots):
                face.material_index = slot; face.use_smooth = True
            at = me.attributes.new('v06_t', 'FLOAT', 'POINT')
            for datum, t in zip(at.data, ts): datum.value = t
            uv = me.uv_layers.new(name='UVMap')
            for pi, values in uvfaces:
                for li, value in zip(me.polygons[pi].loop_indices, values): uv.data[li].uv = value
            roots = [tuple(vertex.co) for vertex, t in zip(me.vertices, ts) if t <= .002]
            rb = [[min(q[k] for q in roots), max(q[k] for q in roots)] for k in range(3)]
            b = bounds(me)
            d = {'size':size, 'tier':tier, 'variant':variant,
                 'radius':math.hypot(max(abs(q) for q in b[0]),max(abs(q) for q in b[1])),
                 'root_bounds':rb, 'bounds':b, 'root_count':len(roots),
                 'triangles':sum(len(p.vertices)-2 for p in me.polygons)}
            me['v06_root_definition'] = 'v06_t <= 0.002; basal procedural sections and atlas basal vertices'
            me['v06_descriptor'] = json.dumps(d, sort_keys=True)
            obj(name, me, col); descriptors.append(d)
    # Additional owned low-cover forms; the twelve existing meshes/descriptors
    # and their prototype indices stay unchanged. No shared shader is copied.
    slope = cfg['steep_slope']
    for source, old in zip(sorted(col.objects, key=lambda o:o.name), list(descriptors)):
        name = f"V06_MEADOW_MASTER_SLOPE_{old['tier']:02d}_{old['variant']}"
        me = source.data.copy(); me.name = name+'_MESH'
        for vertex in me.vertices: vertex.co.z *= slope['height_factor']
        me.update()
        roots = [tuple(vertex.co) for vertex, t in zip(me.vertices, me.attributes['v06_t'].data)
                 if t.value <= .002]
        b = bounds(me)
        d = dict(old, bounds=b,
                 root_bounds=[[min(q[k] for q in roots),max(q[k] for q in roots)] for k in range(3)],
                 radius=math.hypot(max(abs(q) for q in b[0]),max(abs(q) for q in b[1])),
                 slope_class='steep', height_factor=slope['height_factor'])
        me['v06_descriptor'] = json.dumps(d, sort_keys=True)
        obj(name, me, col); descriptors.append(d)
    return col, descriptors


def meadow_footprint_normal_z(surf, box):
    """Minimum actual triangle normal Z over the complete projected footprint.

    Clip every intersecting terrain triangle, including corners and interior
    edges. A centre/corner-only test can miss a steeper triangle inside a patch.
    This conservative rectangle contains every transformed plant vertex.
    """
    x0,x1,y0,y1 = box; ids = set(); minimum = 1.; pieces = 0
    for iy in range(math.floor(y0/4),math.floor(y1/4)+1):
        for ix in range(math.floor(x0/4),math.floor(x1/4)+1):
            ids.update(surf.grid.get((ix,iy),()))
    for i in ids:
        poly = [surf.v[k][:2] for k in surf.f[i]]
        for axis,bound,greater in [(0,x0,True),(0,x1,False),(1,y0,True),(1,y1,False)]:
            if not poly: break
            out = []; prev = poly[-1]; pin = prev[axis]>=bound if greater else prev[axis]<=bound
            for curr in poly:
                cin = curr[axis]>=bound if greater else curr[axis]<=bound
                if cin != pin:
                    t = (bound-prev[axis])/(curr[axis]-prev[axis])
                    out.append((prev[0]+t*(curr[0]-prev[0]),prev[1]+t*(curr[1]-prev[1])))
                if cin: out.append(curr)
                prev = curr; pin = cin
            poly = out
        if poly:
            a,b,_ = surf.planes[i]
            minimum = min(minimum,1/math.sqrt(1+a*a+b*b)); pieces += 1
    assert pieces,box
    return minimum,pieces


def scatter_meadow(scene, P, spec, surf, col, masters, desc, forest_records, trial=None):
    cfg = spec['meadow']; poly = P['site_v05']['garden_polygon']
    fence = json.loads(scene['site_v05_summary'])['fence'].copy()
    fence['post_points'] = [(o.location.x,o.location.y,.1) for o in scene.objects
                            if o.name.startswith(('FENCE_post_proxy','V05_FENCE_POST_','V05_GATE_POST_'))]
    spatial = SpatialPoints([r[0] for r in forest_records])
    mask = GrassMask(scene, P['site_v05'], fence, spatial)
    mask.trunks = [(o.location.x,o.location.y) for o in scene.objects
                   if o.name in ['V04_ORCHARD','V04_YOUNG_00','V04_YOUNG_01','V04_YOUNG_02','V04_YOUNG_03'] and not o.hide_render]
    records = []; counts = {'support_subdivisions':0,'boundary_subdivisions':0,'support_rejected':0,
                            'hard_mask_rejected':0,'extent_rejected':0,'slope_rejected':0,
                            'steep_instances':0,'steep_nonclass_skipped':0,'steep_footprint_rejected':0,
                            'steep_footprint_subdivisions':0,'steep_footprint_pieces':0}
    lost_area = 0.; max_spread = 0.; max_burial = 0.; proof_pieces = 0
    slope = cfg['steep_slope']; old_limit = math.cos(math.radians(slope['starts_above_degrees']))
    new_limit = math.cos(math.radians(slope['maximum_degrees'])); steep_area = 0.
    x0,x1,y0,y1 = surf.extent
    def projected_box(b, matrix):
        pts = [matrix@Vector((x,y,z)) for x in b[0] for y in b[1] for z in b[2]]
        return [min(p.x for p in pts),max(p.x for p in pts),min(p.y for p in pts),max(p.y for p in pts)]
    def refine(x, y, size, tier, steep_branch=False):
        target = cfg['patch_sizes_m'][tier+1]; n = round(size/target)
        for j in range(n):
            for i in range(n): place(x-size/2+(i+.5)*target, y-size/2+(j+.5)*target, target, tier+1, steep_branch)
    def place(cx, cy, size, tier, steep_branch=False):
        nonlocal lost_area,max_spread,max_burial,proof_pieces,steep_area
        rr = rng_for(spec['seed'],'continuous-meadow-place',round(cx,6),round(cy,6),size)
        x = cx+rr.uniform(-cfg['jitter_fraction'],cfg['jitter_fraction'])*size
        y = cy+rr.uniform(-cfg['jitter_fraction'],cfg['jitter_fraction'])*size
        if not (x0<=x<=x1 and y0<=y<=y1): counts['extent_rejected']+=1; return
        # Stochastic interpolation mixes adjacent ecological forms continuously.
        mixture = min(2.999999,3*field(x,y)); low = int(mixture)
        variant = low + (1 if rr.random()<mixture-low else 0)
        proto = tier*4+variant; d = desc[proto]
        z,n,face = surf.sample(x,y)
        steep = n.z < old_limit
        # A formerly excluded parent must never introduce ordinary-slope
        # children. The old normal-slope traversal/placements stay identical.
        if steep_branch and not steep: counts['steep_nonclass_skipped']+=1; return
        if n.z < new_limit: counts['slope_rejected']+=1; return
        if steep: proto += len(cfg['patch_sizes_m'])*4; d = desc[proto]
        rotation = pose(n,rr.random()*math.tau); matrix = __import__('mathutils').Euler(rotation).to_matrix()
        fb = projected_box(d['bounds'],matrix)
        radius = max(math.hypot(a,b) for a in fb[:2] for b in fb[2:])
        outside = x+fb[0]<x0 or x+fb[1]>x1 or y+fb[2]<y0 or y+fb[3]>y1
        blocked = (inside_polygon(x,y,poly) or polygon_distance(x,y,poly)<radius or
                   not mask.clear(x,y,radius) or spatial.nearest(x,y,radius+.25)<radius+.25)
        if outside or blocked:
            if tier+1<len(cfg['patch_sizes_m']) and not inside_polygon(x,y,poly):
                counts['boundary_subdivisions']+=1; refine(cx,cy,size,tier,steep_branch or steep)
            else: counts['extent_rejected' if outside else 'hard_mask_rejected']+=1
            return
        if steep:
            minimum,pieces = meadow_footprint_normal_z(surf,[x+fb[0],x+fb[1],y+fb[2],y+fb[3]])
            counts['steep_footprint_pieces'] += pieces
            if minimum < new_limit:
                if tier+1 < len(cfg['patch_sizes_m']):
                    counts['steep_footprint_subdivisions']+=1; refine(cx,cy,size,tier,True)
                else: counts['steep_footprint_rejected']+=1
                return
        rb = projected_box(d['root_bounds'],matrix); box = [x+rb[0],x+rb[1],y+rb[2],y+rb[3]]
        lo,hi,pieces = surf.range_over_box(box,(x,y,z),n); span = hi-lo
        if span>.005 and tier+1<len(cfg['patch_sizes_m']):
            counts['support_subdivisions']+=1; refine(cx,cy,size,tier,steep_branch or steep); return
        headroom = max(0,d['root_bounds'][2][1])/n.z
        if span+headroom>.017:
            counts['support_rejected']+=1; lost_area+=size*size; return
        embed = .002+headroom
        records.append(((x,y,z+lo-embed),proto,rotation,(1,1,1)))
        if steep: counts['steep_instances']+=1; steep_area+=size*size
        max_spread=max(max_spread,span);max_burial=max(max_burial,span+embed);proof_pieces+=pieces
    step = cfg['patch_sizes_m'][0]; pitch = step*cfg['row_pitch_ratio']
    for iy in range(math.ceil((y0+step/2)/pitch),math.floor((y1-step/2)/pitch)+1):
        y = (iy+.5)*pitch
        for ix in range(math.ceil((x0+step/2)/step),math.floor((x1-step/2)/step)+1):
            x = (ix+.5+.5*(iy&1))*step
            if not in_trial(x,y,trial) or inside_polygon(x,y,poly): continue
            place(x,y,step,0)
    chunks = instances('V06_MEADOW',records,col,masters,32)
    return dict(counts, instances=len(records), chunks=chunks, master_variants=len(desc),
                steep_nominal_cell_area_m2=steep_area, steep_slope_policy=slope,
                support_rejected_area_m2=lost_area, area_method='Sum of rejected nominal root-cell areas; staggered footprints may overlap',
                max_exact_support_spread=max_spread, clipped_triangle_pieces=proof_pieces,
                root_certificate_max_burial_m=max_burial,root_certificate_max_exposure_m=-.002,
                expanded_triangles=sum(desc[r[1]]['triangles'] for r in records),
                mechanism=cfg['mechanism'],screen_lod=False,binary_field_omission=False)


def apply_meadow_v06(scene, P, ROOT, *, surf=None, forest_records=None, trial=None):
    """Shared deterministic meadow-only mutation; frozen forest/lawn/terrain stay intact."""
    before = random.getstate(); spec = P['vegetation_v06']
    assert not bpy.app.is_job_running('RENDER') and spec['meadow']['mechanism']=='continuous-root-field-v1'
    # Explicitly own only meadow chunks and off-scene meadow masters.
    for ob in list(bpy.data.objects):
        if ob.name.startswith('V06_MEADOW_'):
            assert ob.get('v06_owned'),ob.name
            bpy.data.objects.remove(ob,do_unlink=True)
    for me in list(bpy.data.meshes):
        if me.name.startswith('V06_MEADOW_') and me.users==0:
            assert me.get('v06_owned'),me.name
            bpy.data.meshes.remove(me)
    parent = collection('97_VEGETATION_V06',scene.collection)
    col = collection('V06_MEADOW',parent)
    if surf is None: surf=Surface(scene)
    # Always use the actual stored float32 forest anchors. Full generation's
    # temporary double-precision records can differ at hard-mask thresholds.
    # This matches the live meadow-only call and does not move any tree.
    forest_records=[]
    for ob in sorted(scene.objects,key=lambda x:x.name):
        if ob.name.startswith('V06_FOREST_') and ob.data and 'prototype' in ob.data.attributes:
            forest_records.extend((tuple(p.co),0,(0,0,0),(1,1,1)) for p in ob.data.vertices)
    masters,desc = meadow_masters(spec)
    result = scatter_meadow(scene,P,spec,surf,col,masters,desc,forest_records,trial)
    result['global_rng_unchanged']=random.getstate()==before
    assert result['global_rng_unchanged']
    if 'vegetation_v06_summary' in scene:
        summary=json.loads(scene['vegetation_v06_summary']);summary['meadow']=result
        scene['vegetation_v06_summary']=json.dumps(summary,sort_keys=True)
    scene['v06_meadow_correction_summary']=json.dumps(result,sort_keys=True)
    bpy.context.view_layer.update()
    return result

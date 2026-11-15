"""Explicit deterministic v04 environment refinement, shared by MCP and replay.

No import-time scene effects or downloads. Only normalized tracked libraries
and owned v04 data are used. Existing near-ground mesh coordinates are immutable.
"""
import hashlib
import math
import random
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from timber_fence_v03 import configure_comparison_render

PROXY_COUNTS = {'SHRUB_proxy':19, 'FLOWER_proxy':7, 'TREE_trunk_proxy':38,
                'CONIFER_proxy':152, 'APPLE_trunk_proxy':1,
                'APPLE_branch_proxy':23, 'APPLE_foliage_proxy':23}
_Z_BOUNDS = {}


def _collection(name, parent):
    c=bpy.data.collections.get(name)
    if c is None:
        c=bpy.data.collections.new(name);c['v04_owned']=True;parent.children.link(c)
    else:
        assert c.get('v04_owned'), ('Unowned collection collision',name)
        if c.name not in parent.children:parent.children.link(c)
    return c


def _masters(spec, root):
    masters={}
    for asset,record in sorted(spec['assets'].items()):
        path=(root/record['library']).resolve()
        assert path.is_relative_to(root) and path.is_file() and not path.is_symlink(),path
        digest=hashlib.sha256(path.read_bytes()).hexdigest()
        assert digest==record['sha256'], ('Asset library changed',asset)
        missing=[n for n in record['collections'] if n not in bpy.data.collections]
        if missing:
            with bpy.data.libraries.load(str(path),link=False) as (a,b):
                assert all(n in a.collections for n in missing)
                b.collections=missing
        for name in record['collections']:
            c=bpy.data.collections[name]
            assert c.get('v04_owned') and len(c.objects)==1,name
            # Source collections are intentionally outside the visible scene;
            # retain them through a cold save/reopen for repeatable application.
            c.use_fake_user=True
            c['v04_library_sha256']=digest;c['v04_asset_id']=asset
            source=next(iter(c.objects));assert source.type=='MESH'
            masters[name]=source
            for mat in source.data.materials:
                assert mat and mat.get('v04_owned')
                for node in mat.node_tree.nodes:
                    if node.type=='TEX_IMAGE' and node.image:
                        im=node.image;file=root/'assets/models'/asset/'textures'/Path(im.filepath).name
                        assert file.is_file(),file
                        if not im.packed_file:
                            im.filepath=str(file);im.pack()
                        im.filepath='//../'+file.relative_to(root).as_posix()
    return masters


def _ground_bvh(obj):
    verts=[obj.matrix_world@v.co for v in obj.data.vertices]
    return BVHTree.FromPolygons(verts,[tuple(p.vertices) for p in obj.data.polygons],all_triangles=False)


def _height(bvh,x,y,default=-.055):
    hit,_,_,_=bvh.ray_cast(Vector((x,y,300)),Vector((0,0,-1)),600)
    return hit.z if hit is not None else default


def _ground_material(name,colors,roughness,bump):
    mat=bpy.data.materials.get(name)
    if mat is None:mat=bpy.data.materials.new(name);mat['v04_owned']=True
    assert mat.get('v04_owned');mat.use_nodes=True
    n=mat.node_tree.nodes;l=mat.node_tree.links;n.clear()
    pos=n.new('ShaderNodeNewGeometry');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=.58;noise.inputs['Detail'].default_value=3
    l.new(pos.outputs['Position'],noise.inputs['Vector'])
    ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.2;ramp.color_ramp.elements[0].color=(*colors[0],1)
    ramp.color_ramp.elements[1].position=.8;ramp.color_ramp.elements[1].color=(*colors[1],1);l.new(noise.outputs['Fac'],ramp.inputs[0])
    fine=n.new('ShaderNodeTexNoise');fine.inputs['Scale'].default_value=65;fine.inputs['Detail'].default_value=2;l.new(pos.outputs['Position'],fine.inputs['Vector'])
    normal=n.new('ShaderNodeBump');normal.inputs['Distance'].default_value=bump;normal.inputs['Strength'].default_value=.3;l.new(fine.outputs['Fac'],normal.inputs['Height'])
    bs=n.new('ShaderNodeBsdfPrincipled');bs.inputs['Roughness'].default_value=roughness;l.new(ramp.outputs['Color'],bs.inputs['Base Color']);l.new(normal.outputs['Normal'],bs.inputs['Normal'])
    out=n.new('ShaderNodeOutputMaterial');l.new(bs.outputs[0],out.inputs[0]);return mat


def _lerp_profile(u,knots,values):
    if u<=knots[0]:return values[0]
    for a,b,va,vb in zip(knots,knots[1:],values,values[1:]):
        if u<=b:
            t=(u-a)/(b-a);t=t*t*(3-2*t);return va+(vb-va)*t
    return values[-1]


def _hill(scene,record,index,spec,ground,material,col):
    camera=scene.camera;origin=camera.location.copy()
    forward=(camera.rotation_euler.to_matrix()@Vector((0,0,-1)));forward.z=0;forward.normalize()
    right=Vector((forward.y,-forward.x,0));fx=camera.data.lens/camera.data.sensor_width
    fy=fx*scene.render.resolution_x/scene.render.resolution_y;horizon=.5+camera.data.shift_y*scene.render.resolution_x/scene.render.resolution_y
    u0,u1=record['u_range'];d0,dc,d1=record['depth_m'];knots=spec['crest_u'];profile=record['crest_v']
    def xyz(u,d):return origin+forward*d+right*((u-.5)*d/fx)
    def surface(u,d):
        xy=xyz(u,d);base=_height(ground,xy.x,xy.y)
        v=_lerp_profile(u,knots,profile)
        crest=origin.z+(horizon-v)*dc/fy
        q=(d-d0)/(dc-d0) if d<=dc else (d1-d)/(d1-dc)
        q=max(0,min(1,q));shape=q*q*(3-2*q)
        z=base+max(0,crest-base)*shape
        # Low, nonperiodic undulation vanishes at the joining feet.
        z+=shape*.45*(math.sin(u*17+d*.037+index)+.4*math.sin(u*31-d*.062))
        return (xy.x,xy.y,z)
    nx,ny=record['grid'];vertices=[];faces=[]
    for j in range(ny):
        d=d0+(d1-d0)*j/(ny-1)
        for i in range(nx):vertices.append(surface(u0+(u1-u0)*i/(nx-1),d))
    for j in range(ny-1):
        for i in range(nx-1):
            k=j*nx+i;faces.append((k,k+1,k+nx+1,k+nx))
    name='LANDSCAPE_hills_v04_'+str(index+1);mesh=bpy.data.meshes.new(name+'_mesh');mesh['v04_owned']=True
    mesh.from_pydata(vertices,[],faces);mesh.materials.append(material);mesh.update()
    obj=bpy.data.objects.new(name,mesh);obj['v04_generated']=True;col.objects.link(obj)
    for p in mesh.polygons:p.use_smooth=True
    return obj,_ground_bvh(obj),xyz


def _instance(name,source,collection,point,height,yaw,embed=.012,scale_xy=1):
    assert name not in bpy.data.objects, ('Object collision',name)
    obj=bpy.data.objects.new(name,source.data);collection.objects.link(obj);obj['v04_generated']=True
    key=source.data.as_pointer()
    if key not in _Z_BOUNDS:
        _Z_BOUNDS[key]=(min(v.co.z for v in source.data.vertices),max(v.co.z for v in source.data.vertices))
    lo,hi=_Z_BOUNDS[key]
    scale=height/(hi-lo)
    obj.scale=(scale*scale_xy,scale*scale_xy,scale);obj.rotation_euler=(0,0,yaw)
    obj.location=(point[0],point[1],point[2]-lo*scale-embed)
    return obj


def _clear_generated(scene):
    for obj in list(scene.objects):
        if obj.get('v04_generated'):
            data=obj.data;bpy.data.objects.remove(obj,do_unlink=True)
            if data and data.users==0 and data.get('v04_owned'):bpy.data.meshes.remove(data)


def apply_v04(scene,P,ROOT):
    """Apply the granted environment without changing global RNG or v03 sources."""
    rng_before=random.getstate();rng=random.Random(13704);root=Path(ROOT).resolve();spec=P['landscape_v04']
    assert spec['seed']==13704 and scene.camera.name==P['camera']['name']
    terrain=scene.objects['SITE_terrain_proxy'];bed=scene.objects['BED_entry']
    # Precompute support before any material assignment; no terrain vertex writes.
    ground=_ground_bvh(terrain);_clear_generated(scene)
    parent=_collection('95_LANDSCAPE_V04',scene.collection)
    cols={k:_collection('V04_'+k.upper(),parent) for k in ['hills','forest','young','orchard','planting','edge_grass']}
    masters=_masters(spec,root)
    for prefix,count in PROXY_COUNTS.items():
        objects=[o for o in scene.objects if o.name.startswith(prefix)];assert len(objects)==count,(prefix,len(objects))
        for o in objects:o.hide_render=True;o.hide_viewport=True
    g=spec['ground']
    lawn=_ground_material('MAT_V04_LAWN',g['lawn_colors'],.94,.003)
    soil=_ground_material('MAT_V04_SOIL',g['soil_colors'],.96,.005)
    hillmat=_ground_material('MAT_V04_MEADOW',g['meadow_colors'],.96,.004)
    for name in ('MAT_GRASS','MAT_SOIL'):
        original=bpy.data.materials.get(name)
        if original:original.use_fake_user=True
    terrain.data.materials.clear();terrain.data.materials.append(lawn)
    bed.data.materials.clear();bed.data.materials.append(soil)
    hills=[_hill(scene,r,i,spec,ground,hillmat,cols['hills']) for i,r in enumerate(spec['hills'])]
    forest_count=0;species={'MARIANA':0,'ABIES':0};spacing_min=999
    for layer,(record,(_,support,xyz)) in enumerate(zip(spec['hills'],hills)):
        accepted=[];tries=0;target=record['forest_count'];dlo,dhi=record['scatter_depth_m']
        while len(accepted)<target:
            tries+=1;assert tries<target*1000,('Scatter packing failed',layer,len(accepted))
            u=rng.uniform(*record['scatter_u']);d=rng.uniform(dlo,dhi);xy=xyz(u,d)
            # Narrow irregular meadow strips preserve 15% of sub-ridge surface.
            glade=math.sin(u*19+layer*1.3)+.55*math.sin(d*.13-u*11)
            if glade>record['glade_threshold']:continue
            spacing=record['spacing_m']
            if any((xy.x-x)**2+(xy.y-y)**2<spacing**2 for x,y in accepted):continue
            if accepted:spacing_min=min(spacing_min,min(math.hypot(xy.x-x,xy.y-y) for x,y in accepted))
            accepted.append((xy.x,xy.y));z=_height(support,xy.x,xy.y)
            black=record['black_spruce_count'];i=len(accepted)-1
            kind='MARIANA' if (i*black//target)!=((i+1)*black//target) else 'ABIES'
            # Shared high LOD along occasional visible stand edges, compact LOD elsewhere.
            lod='LOD0' if len(accepted)%record['high_lod_every']==0 else 'LOD1'
            source=masters['V04_MASTER_'+kind+'_'+lod]
            height=rng.uniform(*record['height_m']);yaw=rng.uniform(-math.pi,math.pi)
            obj=_instance(f'V04_FOREST_{forest_count:04d}',source,cols['forest'],(xy.x,xy.y,z),height,yaw)
            obj['v04_species']=kind;obj['v04_lod']=lod;obj['v04_hill']=layer+1
            species[kind]+=1;forest_count+=1
    for i,row in enumerate(spec['young_spruces']):
        x,y=row['xy'];z=_height(ground,x,y)
        _instance(f'V04_YOUNG_{i:02d}',masters['V04_MASTER_ABIES_YOUNG'],cols['young'],(x,y,z),row['height_m'],rng.uniform(-math.pi,math.pi))
    orchard=spec['orchard'];x,y=orchard['xy'];z=_height(ground,x,y)
    tree=_instance('V04_ORCHARD',masters['V04_MASTER_ORCHARD'],cols['orchard'],(x,y,z),orchard['height_m'],orchard['rotation_z_rad'],embed=.04)
    bpy.context.view_layer.update()
    fruit=masters['V04_MASTER_FOOD_APPLE_01_0'];coords=[v.co for v in fruit.data.vertices]
    diameter=max(max(v.x for v in coords)-min(v.x for v in coords),max(v.y for v in coords)-min(v.y for v in coords));top=max(v.z for v in coords)
    for i,anchor in enumerate(orchard['fruit_anchors']):
        point=tree.matrix_world@Vector(anchor['twig']);scale=anchor['diameter_m']/diameter
        obj=bpy.data.objects.new(f'V04_APPLE_{i:02d}',fruit.data);cols['orchard'].objects.link(obj);obj['v04_generated']=True
        obj.scale=(scale,scale,scale);obj.rotation_euler=(0,0,rng.uniform(-math.pi,math.pi));obj.location=point-Vector((0,0,top*scale))
        obj['v04_twig_anchor_world']=list(point)
    bed_top=bed.location.z+bed.dimensions.z/2
    for role,prefix in [('shrubs','SHRUB_01'),('grasses','GRASS_MEDIUM_01'),('flowers','PERIWINKLE_PLANT')]:
        settings=spec['planting'][role];positions=[]
        for i in range(settings['count']):
            group=rng.choices(spec['planting']['x_groups'],weights=spec['planting']['group_weights'],k=1)[0]
            x=rng.uniform(group[0]+.2,group[1]-.2);y=rng.uniform(-1.37,-1.05)
            for member in range(settings['members']):
                angle=rng.random()*math.tau;radius=.08*math.sqrt(rng.random())
                source=masters[f'V04_MASTER_{prefix}_{(i+member)%3}']
                _instance(f'V04_BED_{role.upper()}_{i:02d}_{member}',source,cols['planting'],(x+math.cos(angle)*radius,y+math.sin(angle)*radius,bed_top),rng.uniform(*settings['height_m']),rng.uniform(-math.pi,math.pi))
    fence=P['foreground_fence'];a=Vector((*fence['polyline_xy'][0],0));b=Vector((*fence['polyline_xy'][-1],0));direction=(b-a).normalized();normal=Vector((-direction.y,direction.x,0))
    posts=[o.location.copy() for o in scene.objects if o.name.startswith('FENCE_post_proxy')]
    placed=0
    while placed<spec['edge_grass_count']:
        i=placed
        if i<spec['edge_grass_count']*.75:
            point=a+(b-a)*rng.random()+normal*rng.choice([-1,1])*rng.uniform(.18,.65)
        else:point=Vector((rng.uniform(1.8,15.3),rng.uniform(-3.5,-1.9),0))
        if 6.5<point.x<9.2 and point.y>-3.7:continue
        if any((point.xy-p.xy).length<.15 for p in posts):continue
        point.z=_height(ground,point.x,point.y)
        for member in range(spec['edge_grass_members']):
            offset=Vector((rng.uniform(-.05,.05),rng.uniform(-.05,.05),0));p=point+offset;p.z=_height(ground,p.x,p.y)
            _instance(f'V04_EDGE_GRASS_{i:03d}_{member}',masters[f'V04_MASTER_GRASS_MEDIUM_01_{(i+member)%3}'],cols['edge_grass'],p,rng.uniform(.16,.38),rng.uniform(-math.pi,math.pi))
        placed+=1
    bpy.context.view_layer.update()
    assert random.getstate()==rng_before,'v04 altered global RNG'
    result={'forest_instances':forest_count,'forest_species':species,'minimum_within_layer_spacing_m':spacing_min,
        'young_spruces':len(spec['young_spruces']),'fruit_instances':len(orchard['fruit_anchors']),'bed_clump_groups':sum(spec['planting'][r]['count'] for r in ['shrubs','grasses','flowers']),
        'bed_instances':sum(spec['planting'][r]['count']*spec['planting'][r]['members'] for r in ['shrubs','grasses','flowers']),
        'edge_grass_groups':placed,'edge_grass_instances':placed*spec['edge_grass_members'],'hidden_original_proxies':263,'global_rng_unchanged':True}
    scene['landscape_v04_revision']='v04';return result

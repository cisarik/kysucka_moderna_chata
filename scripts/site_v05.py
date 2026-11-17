"""Deterministic v05 world-space site, enclosure and instanced ground cover.

Explicitly invoked by the granted MCP route and the source builder. Importing
does not alter Blender, perform I/O, or download assets. All distances are metres.
"""
import bisect
import hashlib
import json
import math
import random
from pathlib import Path

import bpy
from mathutils import Vector, Matrix, Quaternion, Euler
from mathutils.bvhtree import BVHTree
from mathutils.geometry import delaunay_2d_cdt
from timber_fence_v03 import _stake, _rail, _metric_uv

_SURFACE = None


def _enum(owner, key, value):
    prop = owner.bl_rna.properties[key]
    choices = {i.identifier for i in prop.enum_items}
    assert value in choices, (key, value, choices)
    setattr(owner, key, value)


def _smooth(a, b, x):
    t = max(0.0, min(1.0, (x-a)/(b-a)))
    return t*t*(3-2*t)


def _segment(x, y, a, b):
    dx, dy = b[0]-a[0], b[1]-a[1]
    t = max(0., min(1., ((x-a[0])*dx+(y-a[1])*dy)/(dx*dx+dy*dy)))
    return math.hypot(x-a[0]-t*dx, y-a[1]-t*dy), t


def inside_polygon(x, y, polygon):
    return all((b[0]-a[0])*(y-a[1])-(b[1]-a[1])*(x-a[0]) >= -1e-7
               for a, b in zip(polygon, polygon[1:]+polygon[:1]))


def polygon_distance(x, y, polygon):
    return min(_segment(x,y,a,b)[0] for a,b in zip(polygon,polygon[1:]+polygon[:1]))


def analytic_height(x, y, spec):
    x0,x1,y0,y1=spec['protected_terrace'];datum=spec['ground_z']
    local=datum+.04*max(y-y1,0)+.02*max(x0-x,0)
    drect=math.hypot(max(x0-x,0,x-x1),max(y0-y,0,y-y1))
    poly=spec['garden_polygon'];dg=0 if inside_polygon(x,y,poly) else polygon_distance(x,y,poly)
    blend=_smooth(0,spec['valley']['terrace_blend_m'],min(drect,dg))
    if blend==0:return local
    ridge=0.
    for chain in spec['ridge_chains']:
        nearest=min((_segment(x,y,a,b)+(a,b) for a,b in zip(chain['points'],chain['points'][1:])),key=lambda q:q[0])
        dist,t,a,b=nearest
        h=a[2]+t*(b[2]-a[2])
        ridge=max(ridge,(h-datum)*math.exp(-(dist/chain['width_m'])**2))
    for cx,cy,h,sx,sy in spec['gaussian_hills']:
        ridge=max(ridge,h*math.exp(-((x-cx)/sx)**2-((y-cy)/sy)**2))
    v=spec['valley'];width=v['width_m']+v['widen_per_m']*max(x-v['start_x'],0)
    corridor=_smooth(20,35,x)*(1-_smooth(width,width+v['side_blend_m'],abs(y-v['axis_y'])))
    profile=v.get('far_ridge_height_profile',{'base':1,'waves':[]})
    amplitude=profile['base']+sum(a*math.sin(f*(y-v['axis_y'])+p) for a,f,p in profile['waves'])
    valley=datum-v['depth_m']*_smooth(v['start_x'],v['floor_x'],x)+v['far_ridge_height_m']*amplitude*math.exp(-((x-v['far_ridge_x'])/v['far_ridge_width_m'])**2)
    world=(1-corridor)*(datum+ridge)+corridor*valley
    return (1-blend)*local+blend*world


def _owned_collection(name, parent=None):
    col=bpy.data.collections.get(name)
    if col is None:
        col=bpy.data.collections.new(name);col['v05_owned']=True
    assert col.get('v05_owned'), ('Unowned collection collision',name)
    if parent and name not in parent.children:parent.children.link(col)
    if parent is None:col.use_fake_user=True
    return col


def _mesh(name, vertices, faces, materials=()):
    mesh=bpy.data.meshes.get(name)
    if mesh is None:
        mesh=bpy.data.meshes.new(name);mesh['v05_owned']=True
    assert mesh.get('v05_owned'), ('Unowned mesh collision',name)
    mesh.clear_geometry()
    for layer in list(mesh.uv_layers):mesh.uv_layers.remove(layer)
    for attr in list(mesh.attributes):
        if not getattr(attr,'is_required',False):
            try:mesh.attributes.remove(attr)
            except RuntimeError:pass
    mesh.from_pydata(vertices,[],faces);mesh.update()
    mesh.materials.clear()
    for mat in materials:mesh.materials.append(mat)
    return mesh


def _object(name, data, collection):
    assert name not in bpy.data.objects, ('Object collision',name)
    obj=bpy.data.objects.new(name,data);obj['v05_generated']=True;collection.objects.link(obj)
    return obj


def _tag(obj):
    obj['v05_generated']=True
    if obj.data:obj.data['v05_owned']=True
    return obj


def _clear(scene):
    for obj in list(scene.objects):
        if obj.get('v05_generated'):
            bpy.data.objects.remove(obj,do_unlink=True)
    # Reuse explicitly owned meshes/materials/node groups by stable names.
    for data in list(bpy.data.meshes):
        if data.get('v05_owned') and data.users==0 and not data.use_fake_user:
            bpy.data.meshes.remove(data)
    for data in list(bpy.data.cameras):
        if data.get('v05_owned') and data.users==0:bpy.data.cameras.remove(data)


def _material(name):
    mat=bpy.data.materials.get(name)
    if mat is None:mat=bpy.data.materials.new(name);mat['v05_owned']=True
    assert mat.get('v05_owned'), ('Unowned material collision',name)
    mat.use_nodes=True;mat.node_tree.nodes.clear()
    return mat,mat.node_tree.nodes,mat.node_tree.links


def _plain(name, color, roughness=.86):
    mat,n,l=_material(name);bs=n.new('ShaderNodeBsdfPrincipled');bs.inputs['Base Color'].default_value=(*color,1)
    bs.inputs['Roughness'].default_value=roughness
    out=n.new('ShaderNodeOutputMaterial');l.new(bs.outputs[0],out.inputs[0]);return mat


def _ground_materials(spec, root, textured):
    mats=[]
    for meadow in (False,True):
        name='MAT_V05_MEADOW_BASE' if meadow else 'MAT_V05_LAWN_BASE'
        if not textured:
            mats.append(_plain(name,(.11,.18,.045) if meadow else (.09,.17,.035)));continue
        mat,n,l=_material(name)
        uv=n.new('ShaderNodeUVMap');uv.uv_map='UVMap'
        add=n.new('ShaderNodeVectorMath');_enum(add,'operation','ADD');add.inputs[1].default_value=(*spec['grass']['phase_offset'],0)
        l.new(uv.outputs['UV'],add.inputs[0])
        noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=.27;noise.inputs['Detail'].default_value=2
        l.new(uv.outputs['UV'],noise.inputs['Vector'])
        samples={}
        for role,relative in spec['grass']['maps'].items():
            path=root/relative;assert path.is_file() and not path.is_symlink(),path
            image=bpy.data.images.get(path.name)
            if image is None:image=bpy.data.images.load(str(path),check_existing=True)
            assert Path(image.filepath).name==path.name
            image['v05_owned']=True
            image.colorspace_settings.name='sRGB' if role=='color' else 'Non-Color'
            if not image.packed_file:image.pack()
            image.filepath='//../'+relative
            ts=[]
            for vector in (uv.outputs['UV'],add.outputs[0]):
                tex=n.new('ShaderNodeTexImage');tex.image=image;_enum(tex,'extension','REPEAT');l.new(vector,tex.inputs['Vector']);ts.append(tex)
            mix=n.new('ShaderNodeMixRGB');l.new(noise.outputs['Fac'],mix.inputs[0]);l.new(ts[0].outputs['Color'],mix.inputs[1]);l.new(ts[1].outputs['Color'],mix.inputs[2]);samples[role]=mix.outputs[0]
        grade=n.new('ShaderNodeHueSaturation');grade.inputs['Saturation'].default_value=.74 if meadow else .85
        grade.inputs['Value'].default_value=.82 if meadow else .92;l.new(samples['color'],grade.inputs['Color'])
        rough=n.new('ShaderNodeMapRange');rough.inputs['To Min'].default_value=.80;rough.inputs['To Max'].default_value=.98;l.new(samples['roughness'],rough.inputs['Value'])
        normal=n.new('ShaderNodeNormalMap');normal.uv_map='UVMap';normal.inputs['Strength'].default_value=spec['grass']['normal_strength'];l.new(samples['normal'],normal.inputs['Color'])
        bs=n.new('ShaderNodeBsdfPrincipled');l.new(grade.outputs['Color'],bs.inputs['Base Color']);l.new(rough.outputs['Result'],bs.inputs['Roughness']);l.new(normal.outputs['Normal'],bs.inputs['Normal'])
        out=n.new('ShaderNodeOutputMaterial');l.new(bs.outputs[0],out.inputs[0]);mat['tile_m']=spec['grass']['tile_m'];mats.append(mat)
    return mats


def _axis(values):
    out=[]
    for value in sorted(values):
        if not out or abs(value-out[-1])>1e-5:out.append(value)
    return out


class TerrainSurface:
    def __init__(self, vertices, faces):
        self.vertices=vertices;self.faces=faces
        self.bvh=BVHTree.FromPolygons(vertices,faces,all_triangles=True)

    def sample(self,x,y):
        hit,normal,index,_=self.bvh.ray_cast(Vector((x,y,85)),Vector((0,0,-1)),200)
        assert hit is not None, ('Terrain query outside surface',x,y)
        a,b,c=(self.vertices[i] for i in self.faces[index])
        den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
        u=((b[1]-c[1])*(x-c[0])+(c[0]-b[0])*(y-c[1]))/den
        v=((c[1]-a[1])*(x-c[0])+(a[0]-c[0])*(y-c[1]))/den
        return a[2]*u+b[2]*v+c[2]*(1-u-v),normal


def terrain_height_v05(x,y):
    assert _SURFACE is not None, 'Initialize v05 terrain surface before querying'
    return _SURFACE.sample(x,y)[0]


def bind_saved_surface(scene):
    """Read-only height-query initialization for a cold-reopened candidate."""
    global _SURFACE
    verts=[];faces=[]
    for name in ['SITE_terrain_proxy','V05_TERRAIN']:
        obj=scene.objects[name];offset=len(verts)
        verts.extend([tuple(obj.matrix_world@v.co) for v in obj.data.vertices])
        faces.extend(tuple(offset+i for i in p.vertices) for p in obj.data.polygons if not obj.data.attributes.get('V05_shell') or not obj.data.attributes['V05_shell'].data[p.index].value)
    _SURFACE=TerrainSurface(verts,faces)
    return _SURFACE


def _terrain(scene,spec,collection,materials):
    global _SURFACE
    obj=scene.objects['SITE_terrain_proxy'];snapshot=bpy.data.meshes.get('V05_SNAPSHOT_SITE_terrain_proxy')
    if snapshot is None:
        snapshot=obj.data.copy();snapshot.name='V05_SNAPSHOT_SITE_terrain_proxy';snapshot['v05_owned']=True;snapshot.use_fake_user=True
    assert snapshot.get('v05_owned') and len(snapshot.vertices)==2340
    old=[tuple(v.co) for v in snapshot.vertices]
    ox=sorted(set(v[0] for v in old));oy=sorted(set(v[1] for v in old));xmin,xmax,ymin,ymax=spec['terrain_extent']
    xs=_axis(ox+list(range(xmin,xmax+1,5))+[-15,19]+[spec['fine_x'][0]+i*.5 for i in range(round((spec['fine_x'][1]-spec['fine_x'][0])*2)+1)])
    ys=_axis(oy+list(range(ymin,ymax+1,5))+[-10,11.5]+[spec['fine_y'][0]+i*.5 for i in range(round((spec['fine_y'][1]-spec['fine_y'][0])*2)+1)])
    coords=[Vector((x,y)) for y in ys for x in xs];nx=len(xs);ny=len(ys)
    edges=[]
    for j in range(ny):
        for i in range(nx):
            k=j*nx+i
            if i+1<nx:edges.append((k,k+1))
            if j+1<ny:edges.append((k,k+nx))
    first=len(coords);coords.extend(Vector(p) for p in spec['garden_polygon'])
    edges.extend((first+i,first+(i+1)%5) for i in range(5))
    points,_,triangles,_,_,_=delaunay_2d_cdt(coords,edges,[],0,1e-6,False)
    protected={(round(x,6),round(y,6)):(x,y,z) for x,y,z in old if -15<=x<=19 and -10<=y<=11.5}
    world=[]
    for q in points:
        key=(round(q.x,6),round(q.y,6))
        world.append(protected[key] if key in protected else (q.x,q.y,analytic_height(q.x,q.y,spec)))
    inner_vertices=list(old);inner_map={(round(v[0],6),round(v[1],6)):i for i,v in enumerate(old)}
    outer_vertices=[];outer_map={};inner_faces=[];outer_faces=[];inner_mats=[];outer_mats=[]
    def indices(points,lookup,vertices):
        out=[]
        for p in points:
            key=(round(p[0],6),round(p[1],6))
            if key not in lookup:lookup[key]=len(vertices);vertices.append(p)
            else:vertices[lookup[key]]=p
            out.append(lookup[key])
        return tuple(out)
    for tri in triangles:
        pts=[world[k] for k in tri];cx=sum(p[0] for p in pts)/3;cy=sum(p[1] for p in pts)/3
        if (pts[1][0]-pts[0][0])*(pts[2][1]-pts[0][1])-(pts[1][1]-pts[0][1])*(pts[2][0]-pts[0][0])<0:pts.reverse()
        if ox[0]-1e-5<=cx<=ox[-1]+1e-5 and oy[0]-1e-5<=cy<=oy[-1]+1e-5:
            inner_faces.append(indices(pts,inner_map,inner_vertices));inner_mats.append(0 if inside_polygon(cx,cy,spec['garden_polygon']) else 1)
        else:
            outer_faces.append(indices(pts,outer_map,outer_vertices));outer_mats.append(1)
    top_count=len(outer_faces)
    border=[p for p in outer_vertices if abs(p[0]-xmin)<1e-5 or abs(p[0]-xmax)<1e-5 or abs(p[1]-ymin)<1e-5 or abs(p[1]-ymax)<1e-5]
    border.sort(key=lambda p:math.atan2(p[1]-(ymin+ymax)/2,p[0]-(xmin+xmax)/2))
    bottom=[]
    for p in border:
        bottom.append(len(outer_vertices));outer_vertices.append((p[0],p[1],spec['shell_bottom_z']))
    center=len(outer_vertices);outer_vertices.append(((xmin+xmax)/2,(ymin+ymax)/2,spec['shell_bottom_z']))
    for k,p in enumerate(border):
        j=(k+1)%len(border);a=outer_map[(round(p[0],6),round(p[1],6))];q=border[j];b=outer_map[(round(q[0],6),round(q[1],6))]
        outer_faces.extend([(a,b,bottom[j]),(a,bottom[j],bottom[k]),(center,bottom[j],bottom[k])]);outer_mats.extend([1,1,1])
    im=_mesh('V05_SITE_TOP',inner_vertices,inner_faces,materials);obj.data=im
    om=_mesh('V05_WORLD_TERRAIN',outer_vertices,outer_faces,materials);_object('V05_TERRAIN',om,collection)
    for mesh,slots,shell_start in [(im,inner_mats,len(inner_faces)),(om,outer_mats,top_count)]:
        uv=mesh.uv_layers.new(name='UVMap');shell=mesh.attributes.new('V05_shell','BOOLEAN','FACE')
        for face,slot in zip(mesh.polygons,slots):
            face.material_index=slot;face.use_smooth=face.index<shell_start;shell.data[face.index].value=face.index>=shell_start
            for li in face.loop_indices:
                co=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=(co.x/spec['grass']['tile_m'],co.y/spec['grass']['tile_m'])
    # Compute one shared top normal field before splitting the shell into objects.
    # This avoids a lighting seam along the retained inner rectangle.
    shared={}
    for mesh,limit in [(im,len(inner_faces)),(om,top_count)]:
        for face in mesh.polygons[:limit]:
            a,b,c=[mesh.vertices[i].co for i in face.vertices];normal=(b-a).cross(c-a)
            for i in face.vertices:
                co=mesh.vertices[i].co;key=(round(co.x,6),round(co.y,6))
                if key not in shared:shared[key]=Vector((0,0,0))
                shared[key]+=normal
    for key in shared:shared[key].normalize()
    for mesh,limit in [(im,len(inner_faces)),(om,top_count)]:
        normals=[]
        for face in mesh.polygons:
            for li in face.loop_indices:
                co=mesh.vertices[mesh.loops[li].vertex_index].co
                normals.append(shared[(round(co.x,6),round(co.y,6))] if face.index<limit else face.normal)
        mesh.normals_split_custom_set(normals)
    # Cache actual stored float32 coordinates so replay and grounding agree exactly.
    bind_saved_surface(scene)
    assert all(tuple(im.vertices[i].co)==tuple(v) for i,v in enumerate(old) if -15<=v[0]<=19 and -10<=v[1]<=11.5)
    return {'grid':[nx,ny],'top_triangles':len(inner_faces)+top_count,'protected_vertices':len(protected),'terrain_triangles':len(inner_faces)+len(outer_faces)}


def _re_ground(scene):
    lows={};count=0
    for obj in scene.objects:
        if obj.name.startswith('V04_FOREST_') or obj.name in ('V04_YOUNG_02','V04_YOUNG_03'):
            key=obj.data.as_pointer()
            if key not in lows:lows[key]=min(v.co.z for v in obj.data.vertices)
            obj.location.z=terrain_height_v05(obj.location.x,obj.location.y)-lows[key]*obj.scale.z-.012;count+=1
        if obj.name.startswith('LANDSCAPE_hills_v04_'):obj.hide_render=True;obj.hide_viewport=True
    assert count==1202


def _fence(scene,P,spec,col,rng):
    poly=spec['garden_polygon'];mat=bpy.data.materials['MAT_TIMBER_FENCE'];wood=P['fence_timber'];base=P['foreground_fence']
    post_points=[];rail_count=0;stake_count=0
    def stake(p,tangent,anchor=False,gate=False):
        nonlocal stake_count
        z=terrain_height_v05(*p);settings=dict(base);settings['foot_z']=z-.02
        w,d=base['anchor_section_m'] if anchor else (base['stake_width_m']+rng.uniform(-.015,.015),base['stake_depth_m']+rng.uniform(-.01,.01))
        top=z+(.78 if gate else .675 if anchor else .635+rng.uniform(-.04,.04))
        prefix='V05_GATE_POST_' if gate else 'V05_FENCE_POST_'
        obj=_tag(_stake(prefix+f'{stake_count:04d}',Vector((*p,0)),tangent,w,d,top,0 if anchor else rng.uniform(-2,2),rng,settings,mat,col))
        _metric_uv(obj,wood,'fence');post_points.append((p[0],p[1],math.hypot(w,d)/2));stake_count+=1;return obj
    def rail(a,b,height,prefix='V05_FENCE_RAIL_',endpoint_a=None,endpoint_b=None):
        nonlocal rail_count
        t=Vector((b[0]-a[0],b[1]-a[1],0)).normalized();off=Vector((t.y,-t.x,0))*.02
        start=Vector((a[0],a[1],terrain_height_v05(*a)+height))+off
        end=Vector((b[0],b[1],terrain_height_v05(*b)+height))+off
        if endpoint_a is not None:start=Vector(endpoint_a)
        if endpoint_b is not None:end=Vector(endpoint_b)
        o=_tag(_rail(prefix+f'{rail_count:04d}',start,end,mat,col,base));_metric_uv(o,wood,'fence');rail_count+=1
    gate=spec['gate'];a=poly[4];b=poly[0]
    def gatepoint(x):return (x,a[1]+(b[1]-a[1])*(x-a[0])/(b[0]-a[0]))
    left,right=[gatepoint(x) for x in gate['clear_x']];t=Vector((b[0]-a[0],b[1]-a[1],0)).normalized()
    left_center=tuple(Vector((*left,0))-t*.08)[:2];right_center=tuple(Vector((*right,0))+t*.08)[:2]
    runs=[(poly[1],poly[2],True,False),(poly[2],poly[3],False,False),(poly[3],poly[4],False,False),(poly[4],left_center,False,False),(right_center,poly[0],False,True)]
    used=set()
    for edge,(a,b,old_start,old_end) in enumerate(runs):
        length=math.dist(a,b);t=Vector((b[0]-a[0],b[1]-a[1],0)).normalized();breaks=[0.,length]
        if old_start:breaks.append(.45)
        if old_end:breaks.append(length-.45)
        if abs(b[1]-a[1])>1e-8 and min(a[1],b[1])<11.5<max(a[1],b[1]):breaks.append(length*(11.5-a[1])/(b[1]-a[1]))
        breaks=sorted(breaks);anchors=[breaks[0]]
        for lo,hi in zip(breaks,breaks[1:]):
            n=max(1,math.ceil((hi-lo)/2.4));anchors.extend(lo+(hi-lo)*i/n for i in range(1,n+1))
        points=[(a[0]+t.x*d,a[1]+t.y*d) for d in anchors]
        points[0]=tuple(a);points[-1]=tuple(b)
        for j,p in enumerate(points):
            key=tuple(round(v,4) for v in p)
            if key not in used and not(j==0 and old_start) and not(j==len(points)-1 and old_end):
                isgate=math.dist(p,left_center)<1e-5 or math.dist(p,right_center)<1e-5
                stake(p,t,True,isgate);used.add(key)
        for j,(pa,pb) in enumerate(zip(points,points[1:])):
            span=math.dist(pa,pb);n=max(1,math.ceil(span/.39))
            for k in range(1,n):
                d=span*k/n+rng.uniform(-.025,.025);p=(pa[0]+t.x*d,pa[1]+t.y*d);stake(p,t)
            for h in (.245,.485):
                ea=eb=None
                if old_start and j==0:
                    z=.19 if h<.3 else .43;legacy=scene.objects['FENCE_rail_proxy' if h<.3 else 'FENCE_rail_proxy.001']
                    ea=legacy.matrix_world@Vector((0,0,max(v.co.z for v in legacy.data.vertices)))
                if old_end and j==len(points)-2:
                    legacy=scene.objects['FENCE_rail_proxy' if h<.3 else 'FENCE_rail_proxy.001'];eb=legacy.matrix_world@Vector((0,0,min(v.co.z for v in legacy.data.vertices)))
                rail(pa,pb,h,endpoint_a=ea,endpoint_b=eb)
    # Gate inner faces, closed leaf and diagonal brace.
    gap=gate['leaf_end_gap_m'];ga=tuple(Vector((*left,0))+t*gap)[:2];gb=tuple(Vector((*right,0))-t*gap)[:2]
    for h in (.245,.485):rail(ga,gb,h,'V05_GATE_RAIL_')
    length=math.dist(ga,gb);n=math.ceil((length-.075)/.16)
    for i in range(n+1):
        distance=.0375+(length-.075)*i/n
        q=(ga[0]+t.x*distance,ga[1]+t.y*distance);z=terrain_height_v05(*q);settings=dict(base);settings['foot_z']=z+.06
        o=_tag(_stake(f'V05_GATE_PALING_{i:03d}',Vector((*q,0)),t,.075,.045,z+.635,0,rng,settings,mat,col));_metric_uv(o,wood,'fence')
    start=Vector((*ga,terrain_height_v05(*ga)+.245));end=Vector((*gb,terrain_height_v05(*gb)+.485))
    o=_tag(_rail('V05_GATE_DIAGONAL',start,end,mat,col,base));_metric_uv(o,wood,'fence')
    metal=bpy.data.materials['MAT_FRAME'];metal_spec=dict(base);metal_spec['rail_section_m']=[.025,.015];metal_spec['bevel_m']=.001
    for i,height in enumerate((.245,.485)):
        a=Vector((*left_center,terrain_height_v05(*left_center)+height));b=Vector((*ga,terrain_height_v05(*ga)+height))+t*.16
        _tag(_rail(f'V05_GATE_HINGE_{i:02d}',a,b,metal,col,metal_spec))
    _tag(_rail('V05_GATE_LATCH',Vector((*gb,terrain_height_v05(*gb)+.485))-t*.06,Vector((*right_center,terrain_height_v05(*right_center)+.485)),metal,col,metal_spec))
    for o in scene.objects:
        if o.name.startswith('FENCE_post_proxy'):post_points.append((o.location.x,o.location.y,math.hypot(o.dimensions.x,o.dimensions.y)/2))
    settings=spec['path_extension']
    for i,y in enumerate(settings['ys']):
        dx,dy,dz=settings['dimensions'];verts=[(x*dx/2,yy*dy/2,z*dz/2) for z in (-1,1) for yy in (-1,1) for x in (-1,1)]
        faces=[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]
        mesh=_mesh(f'V05_PATH_MESH_{i:02d}',verts,faces,[bpy.data.materials['MAT_CONCRETE']]);o=_object(f'V05_PATH_slab_{i:02d}',mesh,col);o.location=(settings['x'],y,settings['z'])
    return {'stakes':stake_count,'rails':rail_count,'post_points':post_points,'gate_hinge':left,'gate_tangent':[t.x,t.y]}


def _cameras(spec,col):
    for name,row in spec['review_cameras'].items():
        data=bpy.data.cameras.new(name);data['v05_owned']=True;data.lens=row['lens'];data.sensor_width=36;data.shift_x=0;data.shift_y=0;data.clip_end=1000
        obj=_object(name,data,col);obj.location=row['location'];obj.rotation_euler=(Vector(row['target'])-obj.location).to_track_quat('-Z','Y').to_euler()


def _apply(scene,P,ROOT,phase):
    global _SURFACE
    state=random.getstate();rng=random.Random(13705);spec=P['site_v05'];root=Path(ROOT).resolve();assert spec['seed']==13705
    assert scene.camera.name==P['camera']['name'];_clear(scene)
    parent=_owned_collection('96_SITE_V05',scene.collection)
    cols={k:_owned_collection('V05_'+k.upper(),parent) for k in ['terrain','fence','forest','lawn','meadow','cameras']}
    for name in ['MAT_GRASS','MAT_SOIL','MAT_V04_LAWN','MAT_V04_MEADOW']:
        if name in bpy.data.materials:bpy.data.materials[name].use_fake_user=True
    materials=_ground_materials(spec,root,phase!='structure');terrain=_terrain(scene,spec,cols['terrain'],materials)
    _re_ground(scene);fence=_fence(scene,P,spec,cols['fence'],rng);_cameras(spec,cols['cameras'])
    bpy.context.view_layer.update()
    population={}
    if phase!='structure':population=_population(scene,P,spec,cols,rng,fence,phase)
    current_images={Path(p).name for p in spec['grass']['maps'].values()}
    for image in list(bpy.data.images):
        if image.get('v05_owned') and image.users==0 and image.name not in current_images:
            bpy.data.images.remove(image)
    for image in bpy.data.images:
        if image.source=='FILE' and Path(image.filepath).is_absolute():
            path=Path(image.filepath).resolve()
            if path.is_relative_to(root):image.filepath='//../'+path.relative_to(root).as_posix()
    scene.camera=scene.objects[P['camera']['name']];scene['site_v05_revision']='v05';scene['site_v05_phase']=phase
    bpy.context.view_layer.update();assert random.getstate()==state,'v05 altered global RNG'
    result={'terrain':terrain,'fence':{k:v for k,v in fence.items() if k!='post_points'},'population':population,'phase':phase,'global_rng_unchanged':True}
    scene['site_v05_summary']=json.dumps(result,sort_keys=True)
    return result


def apply_v05(scene,P,ROOT):
    """Apply the complete owned v05 refinement, preserving unrelated scene data."""
    return _apply(scene,P,ROOT,'full')


def apply_structure_v05(scene,P,ROOT):
    """Granted first milestone: terrain/enclosure/cameras, before population."""
    return _apply(scene,P,ROOT,'structure')


def apply_pilot_v05(scene,P,ROOT):
    """Granted measured sectors before full population; same geometry helpers."""
    return _apply(scene,P,ROOT,'pilot')


class SpatialPoints:
    def __init__(self,points=(),cell=4.):
        self.cell=cell;self.buckets={}
        for p in points:self.add(p)

    def add(self,p):
        key=(math.floor(p[0]/self.cell),math.floor(p[1]/self.cell))
        self.buckets.setdefault(key,[]).append(p)

    def nearest(self,x,y,radius):
        ix=math.floor(x/self.cell);iy=math.floor(y/self.cell);n=math.ceil(radius/self.cell);best=radius*radius
        for j in range(iy-n,iy+n+1):
            for i in range(ix-n,ix+n+1):
                for p in self.buckets.get((i,j),()):best=min(best,(x-p[0])**2+(y-p[1])**2)
        return math.sqrt(best)


def _forest(scene,spec,col,rng,pilot=False):
    existing=[(o.location.x,o.location.y) for o in scene.objects if o.name.startswith('V04_FOREST_')]
    spatial=SpatialPoints(existing,3.);records=[];counts=[0]*4;species={'MARIANA':0,'ABIES':0}
    ranges=[(-210,-35,-100,90),(-130,170,-175,-45),(35,230,70,210),None]
    poly=spec['garden_polygon'];limit=100 if pilot else sum(spec['forest']['counts']);sources={};bounds={}
    for kind in ('MARIANA','ABIES'):
        for lod in ('LOD0','LOD1'):
            source=next(iter(bpy.data.collections[f'V04_MASTER_{kind}_{lod}'].objects));sources[(kind,lod)]=source
            bounds[(kind,lod)]=(min(v.co.z for v in source.data.vertices),max(v.co.z for v in source.data.vertices))
    for sector,target in enumerate(spec['forest']['counts']):
        tries=0
        while counts[sector]<target and len(records)<limit:
            tries+=1;assert tries<target*1000,('Forest packing failed',sector)
            if sector<3:
                x0,x1,y0,y1=ranges[sector];x=rng.uniform(x0,x1);y=rng.uniform(y0,y1)
            else:
                x=rng.uniform(35,210);w=22+.15*(x-20);y=3+rng.choice([-1,1])*rng.uniform(w+18,w+55)
            if inside_polygon(x,y,poly) or polygon_distance(x,y,poly)<8:continue
            w=22+.15*max(x-20,0)
            if 20<x<220 and abs(y-3)<w+10:continue
            if math.sin(.075*x+.8*math.sin(.031*y))+.55*math.sin(.061*y-.027*x)>.9:continue
            if spatial.nearest(x,y,3)<3:continue
            z,normal=_SURFACE.sample(x,y)
            if normal.z<math.cos(math.radians(40)):continue
            i=len(records);kind='MARIANA' if i*780//1200!=(i+1)*780//1200 else 'ABIES'
            lod='LOD0' if (i+1)%12==0 and math.hypot(x-7.2,y-4.2)<60 else 'LOD1'
            lo,hi=bounds[(kind,lod)];height=rng.uniform(*spec['forest']['height_m']);scale=height/(hi-lo)
            obj=_object(f'V05_FOREST_{i:04d}',sources[(kind,lod)].data,col);obj.location=(x,y,z-lo*scale-.012)
            obj.scale=(scale,)*3;obj.rotation_euler=(0,0,rng.uniform(-math.pi,math.pi))
            obj['v05_species']=kind;obj['v05_lod']=lod;obj['v05_sector']=sector;obj['v05_support_z']=z
            spatial.add((x,y));records.append((x,y));counts[sector]+=1;species[kind]+=1
    assert len(records)==limit
    return {'count':len(records),'sectors':counts,'species':species},SpatialPoints(existing+records)


class GrassMask:
    def __init__(self,scene,spec,fence,forest):
        self.spec=spec;self.poly=spec['garden_polygon'];self.forest=forest;self.fence=fence;self.rectangles=[]
        for o in scene.objects:
            if o.name=='BASE_slab' or o.name=='BED_entry' or o.name.startswith(('PORCH_paving','ENTRY_step_','PATH_slab','V05_PATH_slab_')):
                pts=[o.matrix_world@Vector(v) for v in o.bound_box]
                self.rectangles.append((min(p.x for p in pts)-.1,max(p.x for p in pts)+.1,min(p.y for p in pts)-.1,max(p.y for p in pts)+.1))
        self.posts=SpatialPoints(fence['post_points'],1.)
        self.trunks=[(o.location.x,o.location.y) for o in scene.objects if o.name in ('V04_ORCHARD','V04_YOUNG_00','V04_YOUNG_01','V04_YOUNG_02','V04_YOUNG_03')]

    def clear(self,x,y,radius):
        for x0,x1,y0,y1 in self.rectangles:
            if x0-radius<=x<=x1+radius and y0-radius<=y<=y1+radius:return False
        if self.posts.nearest(x,y,radius+.30)<radius+.30:return False
        if any(math.hypot(x-a,y-b)<radius+.25 for a,b in self.trunks):return False
        hx,hy=self.fence['gate_hinge'];tx,ty=self.fence['gate_tangent'];dx=x-hx;dy=y-hy;u=dx*tx+dy*ty;v=-dx*ty+dy*tx
        if u>=-radius-.10 and v>=-radius-.10 and math.hypot(dx,dy)<self.spec['gate']['swing_radius_m']+radius:return False
        if 6.6-radius<x<9.1+radius and -9.4-radius<y<-7.1+radius:return False
        return True

    def lawn(self,x,y,radius):
        return inside_polygon(x,y,self.poly) and polygon_distance(x,y,self.poly)>=radius and self.clear(x,y,radius)

    def meadow(self,x,y,radius):
        if inside_polygon(x,y,self.poly) or polygon_distance(x,y,self.poly)<radius:return False
        if not self.clear(x,y,radius):return False
        nearest=self.forest.nearest(x,y,12)
        if nearest<1.5+radius:return False
        return polygon_distance(x,y,self.poly)<=18 or (20<x<140 and abs(y-3)<22+.15*max(x-20,0)+12) or nearest<12


def _master(name,mesh,col):
    obj=bpy.data.objects.get(name)
    if obj is None:
        obj=bpy.data.objects.new(name,mesh);obj['v05_generated']=True;col.objects.link(obj)
    else:
        assert obj.get('v05_generated') and obj.name in col.objects;obj.data=mesh
    return obj


def _lawn_masters(spec,rng):
    col=_owned_collection('V05_MASTER_LAWN_PATCHES')
    mats=[_plain('MAT_V05_LAWN_GREEN',(.065,.175,.022),.72),_plain('MAT_V05_LAWN_OLIVE',(.135,.205,.045),.79),_plain('MAT_V05_LAWN_THATCH',(.245,.19,.075),.86)]
    for index in range(16):
        lod=index//4;size=.5 if lod<3 else .125;count=spec['grass']['lawn_blades'][lod] if lod<3 else 25
        verts=[];faces=[];slots=[]
        for blade in range(count):
            margin=min(.022,size*.17);x=rng.uniform(-size/2+margin,size/2-margin);y=rng.uniform(-size/2+margin,size/2-margin)
            height=rng.uniform(*spec['grass']['lawn_height_m']);width=rng.uniform(*spec['grass']['lawn_blade_width_m']);angle=rng.random()*math.tau;ux=math.cos(angle);uy=math.sin(angle)
            bend=rng.uniform(.004,.020);direction=angle+rng.uniform(-1,1);bx=math.cos(direction)*bend;by=math.sin(direction)*bend
            start=len(verts)
            verts.extend([(x-ux*width/2,y-uy*width/2,0),(x+ux*width/2,y+uy*width/2,0),
                          (x+bx*.3-ux*width*.32,y+by*.3-uy*width*.32,height*.55),(x+bx*.3+ux*width*.32,y+by*.3+uy*width*.32,height*.55),(x+bx,y+by,height)])
            faces.extend([(start,start+1,start+3),(start,start+3,start+2),(start+2,start+3,start+4)])
            slot=rng.choices([0,1,2],[.72,.23,.05])[0];slots.extend([slot]*3)
        mesh=_mesh(f'V05_LAWN_MASTER_MESH_{index:02d}',verts,faces,mats)
        for p,slot in zip(mesh.polygons,slots):p.material_index=slot
        _master(f'V05_MASTER_LAWN_PATCH_{index:02d}',mesh,col)
    return col


def _meadow_material(name,original,dry=False):
    mat=bpy.data.materials.get(name)
    if mat is not None:
        assert mat.get('v05_owned');return mat
    mat=original.copy();mat.name=name;mat['v05_owned']=True
    n=mat.node_tree.nodes;l=mat.node_tree.links;bs=next(n for n in n if n.type=='BSDF_PRINCIPLED')
    color=next(iter(bs.inputs['Base Color'].links)).from_socket
    grade=n.new('ShaderNodeHueSaturation');grade.name='V05 color grade';grade.inputs['Saturation'].default_value=.45 if dry else .88;grade.inputs['Value'].default_value=1.1 if dry else .90
    l.new(color,grade.inputs['Color'])
    if dry:
        tint=n.new('ShaderNodeMixRGB');tint.name='V05 dry straw';tint.inputs[0].default_value=.30;tint.inputs[2].default_value=(.30,.22,.085,1);l.new(grade.outputs['Color'],tint.inputs[1]);color=tint.outputs[0]
    else:color=grade.outputs['Color']
    l.new(color,bs.inputs['Base Color']);return mat


def _meadow_masters(spec,rng):
    col=_owned_collection('V05_MASTER_MEADOW_CLUSTERS')
    sources=[next(iter(bpy.data.collections[f'V04_MASTER_GRASS_MEDIUM_01_{i}'].objects)) for i in (0,1,2)]
    original=sources[0].data.materials[0]
    mats=[_meadow_material('MAT_V05_MEADOW_GREEN',original),_meadow_material('MAT_V05_MEADOW_DRY',original,True)]
    stemmat=_plain('MAT_V05_MEADOW_SEED',(.28,.205,.075),.9);mats.append(stemmat)
    for variant in range(4):
        verts=[];faces=[];slots=[];uvs=[];parts=[]
        members=spec['grass']['meadow_cluster_members'][variant]
        for member in range(members):
            source=sources[0 if variant<2 and member<2 else 1+(member+variant)%2];mesh=source.data;low=min(v.co.z for v in mesh.vertices);high=max(v.co.z for v in mesh.vertices)
            height=rng.uniform(spec['grass']['meadow_height_m'][0]+.03,spec['grass']['meadow_height_m'][1]-.08);sz=height/(high-low);sxy=rng.uniform(.85,1.1);yaw=rng.random()*math.tau;cs=math.cos(yaw);sn=math.sin(yaw)
            angle=member*math.tau/members+rng.uniform(-.3,.3);radius=rng.uniform(.05,.14);x=math.cos(angle)*radius;y=math.sin(angle)*radius;offset=len(verts)
            first_face=len(faces)
            for v in mesh.vertices:verts.append((x+(v.co.x*cs-v.co.y*sn)*sxy,y+(v.co.x*sn+v.co.y*cs)*sxy,(v.co.z-low)*sz))
            layer=mesh.uv_layers.active
            slot=1 if rng.random()<.3 else 0
            for p in mesh.polygons:
                faces.append(tuple(offset+i for i in p.vertices));slots.append(slot);uvs.append([tuple(layer.data[i].uv) for i in p.loop_indices] if layer else [(0,0)]*len(p.vertices))
            parts.append({'vertices':[offset,len(verts)],'faces':[first_face,len(faces)],'anchor':[x,y,0]})
        for i in range(9):
            x=rng.uniform(-.20,.20);y=rng.uniform(-.20,.20);height=rng.uniform(spec['grass']['meadow_height_m'][0]+.10,spec['grass']['meadow_height_m'][1]);off=len(verts);w=.0012
            first_face=len(faces)
            verts.extend([(x-w,y,0),(x+w,y,0),(x+.025,y+.01,height-.015),(x+.024,y+.009,height),(x+.027,y+.012,height-.007)])
            faces.extend([(off,off+1,off+2),(off+2,off+3,off+4)]);slots.extend([2,2]);uvs.extend([[(0,0)]*3]*2)
            parts.append({'vertices':[off,len(verts)],'faces':[first_face,len(faces)],'anchor':[x,y,0]})
        mesh=_mesh(f'V05_MEADOW_MASTER_MESH_{variant:02d}',verts,faces,mats);layer=mesh.uv_layers.new(name='UVMap')
        for p,slot,uv in zip(mesh.polygons,slots,uvs):
            p.material_index=slot
            for li,co in zip(p.loop_indices,uv):layer.data[li].uv=co
        mesh['v05_parts']=json.dumps(parts,separators=(',',':'))
        _master(f'V05_MASTER_MEADOW_CLUSTER_{variant:02d}',mesh,col)
    return col


def _meadow_part_masters(cluster_collection):
    """Shared constituent meshes for locally curved support, not full realization."""
    col=_owned_collection('V05_MASTER_MEADOW_PARTS');descriptors=[];index=0
    for source in sorted(cluster_collection.objects,key=lambda o:o.name):
        mesh=source.data;rows=[]
        for part in json.loads(mesh['v05_parts']):
            lo,hi=part['vertices'];fa,fb=part['faces'];anchor=Vector(part['anchor'])
            vertices=[tuple(v.co-anchor) for v in mesh.vertices[lo:hi]]
            faces=[tuple(i-lo for i in p.vertices) for p in mesh.polygons[fa:fb]]
            child=_mesh(f'V05_MEADOW_PART_MESH_{index:03d}',vertices,faces,list(mesh.materials));uv=child.uv_layers.new(name='UVMap')
            for cp,sp in zip(child.polygons,mesh.polygons[fa:fb]):
                cp.material_index=sp.material_index
                for cli,sli in zip(cp.loop_indices,sp.loop_indices):uv.data[cli].uv=mesh.uv_layers['UVMap'].data[sli].uv
            _master(f'V05_MASTER_MEADOW_PART_{index:03d}',child,col)
            minimum=min(v.co.z for v in child.vertices)
            roots={tuple(round(x,7) for x in v.co) for v in child.vertices if v.co.z<minimum+.0005}
            rows.append({'prototype':index,'anchor':anchor,'roots':[Vector(q) for q in sorted(roots)]});index+=1
        descriptors.append(rows)
    return col,descriptors


def _instance_group(name,collection):
    group=bpy.data.node_groups.get(name)
    if group is None:
        group=bpy.data.node_groups.new(name,'GeometryNodeTree');group['v05_owned']=True
        group.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry')
        group.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
    assert group.get('v05_owned');n=group.nodes;l=group.links;n.clear()
    inp=n.new('NodeGroupInput');out=n.new('NodeGroupOutput');info=n.new('GeometryNodeCollectionInfo');info.inputs['Collection'].default_value=collection
    info.inputs['Separate Children'].default_value=True;info.inputs['Reset Children'].default_value=True
    inst=n.new('GeometryNodeInstanceOnPoints');inst.inputs['Pick Instance'].default_value=True
    l.new(inp.outputs['Geometry'],inst.inputs['Points']);l.new(info.outputs['Instances'],inst.inputs['Instance'])
    for attr_name,kind,socket in [('prototype','INT','Instance Index'),('rotation','FLOAT_VECTOR','Rotation'),('scale','FLOAT_VECTOR','Scale')]:
        attr=n.new('GeometryNodeInputNamedAttribute');_enum(attr,'data_type',kind);attr.inputs['Name'].default_value=attr_name;l.new(attr.outputs['Attribute'],inst.inputs[socket])
    l.new(inst.outputs['Instances'],out.inputs['Geometry']);return group


def _scatter_chunks(prefix,records,col,master_collection,chunk_m=8):
    group=_instance_group(prefix+'_INSTANCER',master_collection);chunks={}
    for point,prototype,rotation,scale in records:
        key=(math.floor(point[0]/chunk_m),math.floor(point[1]/chunk_m));chunks.setdefault(key,[]).append((point,prototype,rotation,scale))
    for (ix,iy),rows in sorted(chunks.items()):
        name=f'{prefix}_CHUNK_{ix:+04d}_{iy:+04d}';mesh=_mesh(name+'_POINTS',[r[0] for r in rows],[])
        for key,kind,idx in [('prototype','INT',1),('rotation','FLOAT_VECTOR',2),('scale','FLOAT_VECTOR',3)]:
            attr=mesh.attributes.new(key,kind,'POINT')
            for item,row in zip(attr.data,rows):
                if kind=='INT':item.value=row[idx]
                else:item.vector=row[idx]
        obj=_object(name,mesh,col);mod=obj.modifiers.new('Linked grass patches','NODES');mod.node_group=group
        obj['v05_instances']=len(rows)
    return len(chunks)


def _pose(normal,yaw):
    return tuple((normal.to_track_quat('Z','Y')@Quaternion((0,0,1),yaw)).to_euler())


def _lawn(spec,mask,col,masters,rng,pilot):
    poly=spec['garden_polygon'];step=.5;records=[];accepted=set();lod_counts=[0]*4
    x0,x1,y0,y1=(-14,-6,5,13) if pilot else (min(p[0] for p in poly),max(p[0] for p in poly),min(p[1] for p in poly),max(p[1] for p in poly))
    for iy in range(math.floor(y0/step),math.ceil(y1/step)):
        for ix in range(math.floor(x0/step),math.ceil(x1/step)):
            x=(ix+.5)*step;y=(iy+.5)*step
            if not mask.lawn(x,y,.355):continue
            h,normal=_SURFACE.sample(x,y);d=math.hypot(x-21.5,y+10)
            path_distance=math.hypot(x-7.875,y-max(-8.4,min(0,y)))
            terrace_distance=math.hypot(max(-x,0,x-14.4),max(-.65-y,0,y))
            lod=0 if pilot or d<18 or min(path_distance,terrace_distance)<3 else 1 if d<30 else 2
            prototype=lod*4+rng.randrange(4);rotation=_pose(normal,rng.randrange(4)*math.pi/2)
            records.append(((x,y,h-.003),prototype,rotation,(1,1,1)));accepted.add((ix,iy));lod_counts[lod]+=1
    step=.125
    for iy in range(math.floor(y0/step),math.ceil(y1/step)):
        for ix in range(math.floor(x0/step),math.ceil(x1/step)):
            x=(ix+.5)*step;y=(iy+.5)*step
            if (math.floor(x/.5),math.floor(y/.5)) in accepted:continue
            if not mask.lawn(x,y,.09):continue
            h,normal=_SURFACE.sample(x,y);records.append(((x,y,h-.003),12+rng.randrange(4),_pose(normal,rng.randrange(4)*math.pi/2),(1,1,1)));lod_counts[3]+=1
    chunks=_scatter_chunks('V05_LAWN',records,col,masters,spec['grass']['chunk_m'])
    return {'patches':len(records),'lod_patches':lod_counts,'chunks':chunks},records


def _meadow(spec,mask,col,masters,rng,pilot,part_collection,part_descriptors):
    records=[];zones=[]
    if pilot:zones=[(2,0,0,(20,40,-25,-5))]
    else:
        for density,lo,hi in zip([2,.5,.12],[0,40,100],[40,100,180]):
            zones.append((density,lo,hi,(7.2-hi,7.2+hi,4.2-hi,4.2+hi)))
    for density,lo,hi,bounds in zones:
        spacing=1/math.sqrt(density);x0,x1,y0,y1=bounds
        for iy in range(math.floor(y0/spacing),math.ceil(y1/spacing)):
            for ix in range(math.floor(x0/spacing),math.ceil(x1/spacing)):
                x=(ix+.5+rng.uniform(-.32,.32))*spacing;y=(iy+.5+rng.uniform(-.32,.32))*spacing
                if not(x0<=x<=x1 and y0<=y<=y1):continue
                if not pilot and not(lo<=math.hypot(x-7.2,y-4.2)<hi):continue
                if not mask.meadow(x,y,.39):continue
                z,normal=_SURFACE.sample(x,y)
                if normal.z<math.cos(math.radians(35)):continue
                prototype=rng.randrange(2) if math.hypot(x-7.2,y-4.2)<=spec['grass']['meadow_near_detail_m'] else 2+rng.randrange(2)
                s=rng.uniform(.85,1.08);records.append(((x,y,z-.012),prototype,_pose(normal,rng.random()*math.tau),(s,s,rng.uniform(.85,1))))
    if len(records)>spec['grass']['meadow_max_clusters']:
        # Stable evenly spaced selection retains all radial/sector coverage.
        n=spec['grass']['meadow_max_clusters'];records=[records[i*len(records)//n] for i in range(n)]
    # Thin after the cap so the measured resource lever reduces actual placements.
    far_scale=spec['grass'].get('meadow_density_scale_far',1)
    records=[r for r in records if math.hypot(r[0][0]-7.2,r[0][1]-4.2)<40 or rng.random()<far_scale]
    intact=[];parts=[];projected=0;maximum_shift=0.
    for point,prototype,rotation,scale in records:
        origin=Vector(point);sc=Vector(scale);matrix=Euler(rotation).to_matrix();rows=[];requires_projection=False
        for desc in part_descriptors[prototype]:
            anchor=desc['anchor'];offset=matrix@Vector((anchor.x*sc.x,anchor.y*sc.y,anchor.z*sc.z));world_origin=origin+offset
            samples=[]
            for q in desc['roots']:
                root_offset=matrix@Vector((q.x*sc.x,q.y*sc.y,q.z*sc.z));world_root=world_origin+root_offset
                delta=_SURFACE.sample(world_root.x,world_root.y)[0]-world_root.z
                if abs(delta-.012)>spec['grass']['meadow_projection_threshold_m']:requires_projection=True
                samples.append(delta)
            rows.append((world_origin,desc,min(samples)-.012))
        if not requires_projection:
            intact.append((point,prototype,rotation,scale));continue
        projected+=1
        for world_origin,desc,shift in rows:
            world_origin.z+=shift;maximum_shift=max(maximum_shift,abs(shift))
            parts.append((tuple(world_origin),desc['prototype'],rotation,scale))
    compound_chunks=_scatter_chunks('V05_MEADOW',intact,col,masters,spec['grass']['meadow_chunk_m'])
    part_chunks=_scatter_chunks('V05_MEADOW_PART',parts,col,part_collection,spec['grass']['meadow_chunk_m'])
    return {'clusters':len(records),'intact_cluster_instances':len(intact),'projected_clusters':projected,
            'projected_part_instances':len(parts),'maximum_part_vertical_shift_m':maximum_shift,
            'chunks':compound_chunks+part_chunks,'compound_chunks':compound_chunks,'part_chunks':part_chunks},records


def _population(scene,P,spec,cols,rng,fence,phase):
    pilot=phase=='pilot';forest,spatial=_forest(scene,spec,cols['forest'],rng,pilot)
    mask=GrassMask(scene,spec,fence,spatial)
    lawn_masters=_lawn_masters(spec,rng);meadow_masters=_meadow_masters(spec,rng);part_collection,part_descriptors=_meadow_part_masters(meadow_masters)
    lawn,lawn_records=_lawn(spec,mask,cols['lawn'],lawn_masters,rng,pilot)
    meadow,meadow_records=_meadow(spec,mask,cols['meadow'],meadow_masters,rng,pilot,part_collection,part_descriptors)
    hidden=0
    for obj in scene.objects:
        if obj.name.startswith('V04_EDGE_GRASS_'):
            x,y=obj.location.x,obj.location.y;hide=inside_polygon(x,y,spec['garden_polygon']) or not mask.clear(x,y,.18)
            obj.hide_viewport=hide;obj.hide_render=hide;hidden+=hide
    assert all(mask.lawn(p[0],p[1],.09 if i>=12 else .355) for p,i,_,_ in lawn_records)
    assert all(mask.meadow(p[0],p[1],.39) for p,_,_,_ in meadow_records)
    return {'forest':forest,'lawn':lawn,'meadow':meadow,'legacy_edge_tufts_hidden':hidden,'clearance_violations':0}

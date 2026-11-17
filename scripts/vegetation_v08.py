"""Owned V08 vegetation: deterministic thinning, bounded heights and cheap viewport.

Explicit invocation only. Older scenes, meshes, node groups and generators are
immutable inputs. Render and viewport branches retain linked instances.
"""
import array
from collections import defaultdict, Counter
import hashlib
import json
import math
from pathlib import Path
import random
import time

import bpy
import bmesh
import numpy as np
from mathutils import Vector, Euler


def key(seed, value):
    return hashlib.blake2b(f'{seed}:{value}'.encode(), digest_size=16).digest()


def owned_collection(name, parent=None):
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        col['v08_owned'] = True
    assert col.get('v08_owned'), name
    if parent is not None and col.name not in parent.children:
        parent.children.link(col)
    if parent is None:
        col.use_fake_user = True
    return col


def owned_object(name, mesh, col):
    ob = bpy.data.objects.get(name)
    if ob is None:
        ob = bpy.data.objects.new(name, mesh)
        ob['v08_owned'] = True
    assert ob.get('v08_owned'), name
    ob.data = mesh
    if ob.name not in col.objects:
        col.objects.link(ob)
    return ob


def triangles(mesh):
    return sum(len(p.vertices)-2 for p in mesh.polygons)


def bounds(mesh):
    xyz = np.empty(len(mesh.vertices)*3, dtype=np.float32)
    mesh.vertices.foreach_get('co', xyz)
    xyz = xyz.reshape((-1, 3))
    return [[float(xyz[:, k].min()), float(xyz[:, k].max())] for k in range(3)]


def simplified_mesh(scene, source, name, ratio):
    existing = bpy.data.meshes.get(name)
    if existing:
        assert existing.get('v08_owned')
        return existing
    mesh = source.copy()
    mesh.name = name
    mesh['v08_owned'] = True
    mesh['v08_original_triangles'] = triangles(source)
    temp = bpy.data.objects.new('V08_TEMP_DECIMATE', mesh)
    scene.collection.objects.link(temp)
    try:
        modifier = temp.modifiers.new('V08 derived simplification', 'DECIMATE')
        modifier.ratio = ratio
        modifier.use_collapse_triangulate = True
        # Prefer preserving the basal sections of grass; roots never expand.
        if mesh.attributes.get('v06_t'):
            weights = temp.vertex_groups.new(name='V08_upper_detail')
            lower, upper = [], []
            for vertex in mesh.vertices:
                (lower if vertex.co.z <= .002 else upper).append(vertex.index)
            if lower:
                weights.add(lower, 0., 'REPLACE')
            if upper:
                weights.add(upper, 1., 'REPLACE')
            modifier.vertex_group = weights.name
            modifier.vertex_group_factor = 1.
        with bpy.context.temp_override(object=temp, active_object=temp, selected_objects=[temp],
                                       selected_editable_objects=[temp]):
            bpy.ops.object.modifier_apply(modifier=modifier.name)
        mesh = temp.data
        mesh['v08_owned'] = True
        mesh['v08_source_mesh'] = source.name
        mesh['v08_triangle_ratio'] = triangles(mesh)/max(1, triangles(source))
    finally:
        bpy.data.objects.remove(temp, do_unlink=True)
    return mesh


def plain_material(name, color):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
        mat['v08_owned'] = True
        mat.use_nodes = True
        bsdf = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
        bsdf.inputs['Base Color'].default_value = (*color, 1.)
        bsdf.inputs['Roughness'].default_value = .88
        mat.diffuse_color = (*color, 1.)
    return mat


def coarse_proxy_tree(source, name, col, index, cfg):
    existing = bpy.data.meshes.get(name)
    if existing:
        return owned_object(name.replace('_MESH', ''), existing, col)
    b = bounds(source)
    height = b[2][1]-b[2][0]
    radius = max(abs(q) for axis in b[:2] for q in axis)
    sides = cfg['viewport_radial_segments']
    vertices, faces = [], []
    for j, (z, width) in enumerate([(0., .035), (.12, .035), (.12, .62), (.29, 1.),
                                   (.43, .72), (.59, .79), (.73, .44), (.86, .34), (1., .015)]):
        for i in range(sides):
            a = math.tau*i/sides
            r = radius*width*(1+.08*math.sin(i*2.31+j*1.7+index))
            vertices.append((r*math.cos(a), r*math.sin(a), b[2][0]+height*z))
        if j:
            for i in range(sides):
                faces.append(((j-1)*sides+i, (j-1)*sides+(i+1)%sides,
                              j*sides+(i+1)%sides, j*sides+i))
    mesh = bpy.data.meshes.new(name)
    mesh['v08_owned'] = True
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.append(plain_material('MAT_V08_VIEW_TREE_'+str(index),
                                        (.04+.003*index, .10+.004*index, .038)))
    for p in mesh.polygons:
        p.use_smooth = True
    return owned_object(name.replace('_MESH', ''), mesh, col)


def proxy_tree(scene, source, name, col, index, cfg):
    if cfg.get('viewport_model', 'coarse') == 'coarse':
        return coarse_proxy_tree(source, name, col, index, cfg)
    assert cfg['viewport_model'] == 'source_branches'
    branch_name = name.replace('_MESH', '_BRANCH_MESH')
    mesh = bpy.data.meshes.get(branch_name)
    if mesh is None:
        # Use the asset's existing branch/foliage LOD, with its metric UVs and
        # alpha materials. Smooth closed crown substitutes discard its silhouette.
        lod_index = 1 if index in (0, 1, 4) else 3
        original = bpy.data.objects['V06_TREE_MASTER_'+str(lod_index)].data
        mesh = simplified_mesh(scene, original, branch_name,
                               cfg['viewport_source_triangle_ratio'])
        bm = bmesh.new()
        try:
            bm.from_mesh(mesh)
            loose = [v for v in bm.verts if not v.link_faces]
            bmesh.ops.delete(bm, geom=loose, context='VERTS')
            bm.to_mesh(mesh)
        finally:
            bm.free()
        # Keep the selected prototype's envelope, including the narrower young
        # spruce. Forest roots, transforms, height limits and render stay fixed.
        old, target = bounds(mesh), bounds(source)
        for vertex in mesh.vertices:
            for k in range(3):
                vertex.co[k] = (target[k][0] +
                    (vertex.co[k]-old[k][0]) / (old[k][1]-old[k][0]) *
                    (target[k][1]-target[k][0]))
        mesh['v08_viewport_model'] = 'source_branches'
        mesh['v08_viewport_source'] = original.name
        mesh['v08_viewport_source_triangle_ratio'] = cfg['viewport_source_triangle_ratio']
        mesh.update()
    assert mesh.get('v08_owned') and mesh.get('v08_viewport_model') == 'source_branches'
    previous = bpy.data.objects.get(name.replace('_MESH', ''))
    if previous is not None and previous.data != mesh:
        previous.data.use_fake_user = True
    return owned_object(name.replace('_MESH', ''), mesh, col)


def tree_libraries(scene, cfg):
    render = owned_collection('V08_MASTER_FOREST_RENDER')
    view = owned_collection('V08_MASTER_FOREST_VIEW')
    stats = []
    for i in range(5):
        source = bpy.data.objects['V06_TREE_MASTER_'+str(i)].data
        mesh = simplified_mesh(scene, source, f'V08_TREE_{i:03d}_MESH', cfg['render_triangle_ratio'])
        owned_object(f'V08_TREE_RENDER_{i:03d}', mesh, render)
        view_object = proxy_tree(scene, source, f'V08_TREE_VIEW_{i:03d}_MESH', view, i, cfg)
        stats.append({'index': i, 'source': source.name, 'source_triangles': triangles(source),
                      'render_triangles': triangles(mesh), 'view_triangles': triangles(view_object.data)})
    return render, view, stats


def apply_viewport_forest(scene, P):
    """Replace only the five working tree meshes; preserve all scene placements."""
    cfg = P['vegetation_v08']['forest']
    _, _, library = tree_libraries(scene, cfg)
    result = json.loads(scene['vegetation_v08_summary'])
    result['forest']['library'] = library
    counts = result['forest']['prototype_counts']
    result['forest']['viewport_weighted_triangles'] = sum(
        int(counts.get(str(row['index']), counts.get(row['index'], 0))) * row['view_triangles']
        for row in library)
    result['viewport_branch'] = ('Is Viewport, linked original branch/alpha-foliage LODs '
                                 'and 1/128 grass points; render branch remains linked')
    scene['vegetation_v08_summary'] = json.dumps(result, sort_keys=True)
    return {'library': library,
            'viewport_weighted_triangles': result['forest']['viewport_weighted_triangles']}


def instancer(name, render_masters, view_masters, grass=False):
    group = bpy.data.node_groups.get(name)
    if group:
        assert group.get('v08_owned')
        return group
    group = bpy.data.node_groups.new(name, 'GeometryNodeTree')
    group['v08_owned'] = True
    group.interface.new_socket(name='Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
    group.interface.new_socket(name='Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    nodes, links = group.nodes, group.links
    inp, out = nodes.new('NodeGroupInput'), nodes.new('NodeGroupOutput')
    context = nodes.new('GeometryNodeIsViewport')
    switch = nodes.new('GeometryNodeSwitch')
    switch.input_type = 'GEOMETRY'
    links.new(context.outputs[0], switch.inputs['Switch'])
    links.new(switch.outputs[0], out.inputs[0])
    def attribute(name, kind):
        node = nodes.new('GeometryNodeInputNamedAttribute')
        node.data_type = kind
        node.inputs['Name'].default_value = name
        return node.outputs['Attribute']
    rotation = attribute('rotation', 'FLOAT_VECTOR')
    scale = attribute('scale', 'FLOAT_VECTOR')
    prototype = attribute('v08_prototype' if grass else 'prototype', 'INT')
    geometry = inp.outputs[0]
    if grass:
        delete = nodes.new('GeometryNodeDeleteGeometry'); delete.domain = 'POINT'
        links.new(geometry, delete.inputs['Geometry'])
        links.new(attribute('v07_remove', 'BOOLEAN'), delete.inputs['Selection'])
        geometry = delete.outputs[0]
    for viewport, masters, socket in [(False, render_masters, 'False'), (True, view_masters, 'True')]:
        points = geometry
        if viewport and grass:
            delete = nodes.new('GeometryNodeDeleteGeometry'); delete.domain = 'POINT'
            inverse = nodes.new('FunctionNodeBooleanMath'); inverse.operation = 'NOT'
            links.new(attribute('v08_view_keep', 'BOOLEAN'), inverse.inputs[0])
            links.new(inverse.outputs[0], delete.inputs['Selection'])
            links.new(points, delete.inputs['Geometry']); points = delete.outputs[0]
        collection = nodes.new('GeometryNodeCollectionInfo')
        collection.inputs['Collection'].default_value = masters
        collection.inputs['Separate Children'].default_value = True
        collection.inputs['Reset Children'].default_value = True
        instance = nodes.new('GeometryNodeInstanceOnPoints')
        instance.inputs['Pick Instance'].default_value = True
        links.new(points, instance.inputs['Points'])
        links.new(collection.outputs['Instances'], instance.inputs['Instance'])
        for source, port in [(prototype, 'Instance Index'), (rotation, 'Rotation'), (scale, 'Scale')]:
            links.new(source, instance.inputs[port])
        links.new(instance.outputs['Instances'], switch.inputs[socket])
    return group


def point_object(name, rows, col, group):
    mesh = bpy.data.meshes.get(name+'_POINTS')
    if mesh is None:
        mesh = bpy.data.meshes.new(name+'_POINTS'); mesh['v08_owned'] = True
    mesh.clear_geometry()
    mesh.from_pydata([r['position'] for r in rows], [], [])
    for field, kind in [('prototype', 'INT'), ('rotation', 'FLOAT_VECTOR'), ('scale', 'FLOAT_VECTOR')]:
        attr = mesh.attributes.get(field) or mesh.attributes.new(field, kind, 'POINT')
        data = array.array('i' if kind == 'INT' else 'f')
        for row in rows:
            data.extend([int(row[field])] if kind == 'INT' else row[field])
        attr.data.foreach_set('value' if kind == 'INT' else 'vector', data)
    ob = owned_object(name, mesh, col)
    modifier = next((m for m in ob.modifiers if m.type == 'NODES'), None)
    if modifier is None:
        modifier = ob.modifiers.new('V08 linked viewport/render vegetation', 'NODES')
    modifier.node_group = group
    return ob


def select_trees(records, cfg, seed):
    target = cfg['target_count']
    protect = {r['id'] for r in records if r['id'].startswith('V07_CREST') or r.get('xy_adjustment_m', 0)>0}
    # Keep the top visible root/crown in every angular sector at three review poses.
    for eye in [(21.5,-10.,1.25),(-36,34,54),(44,-38,35)]:
        contour = {}
        for row in records:
            x,y,z = row['position']; distance = max(1., math.hypot(x-eye[0],y-eye[1]))
            sector = int((math.atan2(y-eye[1],x-eye[0])+math.pi)/math.tau*360)%360
            score = (z+row['_height']-eye[2])/distance
            if sector not in contour or score>contour[sector][0]:
                contour[sector] = (score,row['id'])
        protect.update(value[1] for value in contour.values())
    assert len(protect)<target
    groups = defaultdict(list)
    cell = cfg['strata_grid_m']
    for row in records:
        if row['id'] not in protect:
            x,y = row['position'][:2]
            groups[(math.floor(x/cell),math.floor(y/cell),bool(row.get('legacy_young') or row.get('half')))].append(row)
    remaining = target-len(protect); total = sum(map(len,groups.values()))
    quota = {g:math.floor(len(rows)*remaining/total) for g,rows in groups.items()}
    remainder = remaining-sum(quota.values())
    ranking = sorted(groups, key=lambda g:(-(len(groups[g])*remaining/total-quota[g]),g))
    for g in ranking[:remainder]:
        quota[g]+=1
    selected = set(protect)
    for g, rows in groups.items():
        selected.update(r['id'] for r in sorted(rows,key=lambda r:key(seed,r['id']))[:quota[g]])
    assert len(selected)==target
    return selected, protect


def apply_forest(scene, cfg, seed, root):
    import forest_trail_v07 as v07
    original = json.loads(bpy.data.texts['V07_FOREST_REGISTRY.json'].as_string())
    descriptors = v07.tree_descriptors()
    for row in original:
        row['_height'] = descriptors[row['prototype']]['height']*row['scale'][2]
    selected, protected = select_trees(original,cfg,seed)
    render, view, library = tree_libraries(scene,cfg)
    # Derive the actual new root envelopes for reseating after simplification.
    new_descriptors = []
    for i in range(5):
        mesh = bpy.data.objects[f'V08_TREE_RENDER_{i:03d}'].data
        bark = {v for p in mesh.polygons if p.material_index==0 for v in p.vertices}
        low = min(mesh.vertices[i].co.z for i in bark)
        roots = [mesh.vertices[i].co for i in bark if mesh.vertices[i].co.z<=low+.04]
        b = bounds(mesh)
        new_descriptors.append({'root_bounds':[[min(v[k] for v in roots),max(v[k] for v in roots)] for k in range(3)],
                                'height':b[2][1]-b[2][0]})
    surface = v07.mapped_surface(scene,final=True)
    final=[]
    for row in original:
        if row['id'] not in selected:
            continue
        proto = row['prototype'];x,y = row['position'][:2]
        u = int.from_bytes(key(seed,'height:'+row['id'])[:8],'big')/2**64
        field = .5+.5*math.sin(x/21)*math.cos(y/27)
        factor = 1+cfg['height_variation_fraction']*(2*(.65*u+.35*field)-1)
        height = min(cfg['maximum_height_m'],max(cfg['minimum_height_m'],row['_height']*factor))
        scale = list(row['scale']);scale[2]=height/new_descriptors[proto]['height']
        position, support = v07.seated_tree(row,proto,scale,[x,y],new_descriptors,surface,.006)
        final.append({'id':row['id'],'position':position,'prototype':proto,'rotation':row['rotation'],
                      'scale':scale,'height_m':height,'source_height_m':row['_height'],
                      'legacy_young':row['legacy_young'],'half':row['half'],'support':support})
    group = instancer('V08_FOREST_GN',render,view)
    col = owned_collection('V08_FOREST',root)
    chunks=defaultdict(list)
    for row in final:
        chunks[(math.floor(row['position'][0]/32),math.floor(row['position'][1]/32))].append(row)
    for (ix,iy),rows in sorted(chunks.items()):
        point_object(f'V08_FOREST_{ix:+04d}_{iy:+04d}',rows,col,group)
    for ob in scene.objects:
        if ob.name.startswith(('V07_FOREST_','V07_CREST_')):
            ob.hide_render=True;ob.hide_viewport=True
    text=bpy.data.texts.get('V08_FOREST_REGISTRY.json') or bpy.data.texts.new('V08_FOREST_REGISTRY.json')
    text.clear();text.write('[\n')
    for i,row in enumerate(final):
        text.write(json.dumps(row,sort_keys=True)+(',' if i<len(final)-1 else '')+'\n')
    text.write(']\n')
    heights=np.array([r['height_m'] for r in final]); counts=Counter(r['prototype'] for r in final)
    return {'count':len(final),'removed':len(original)-len(final),'contour_and_route_protected':len(protected),
            'minimum_height_m':float(heights.min()),'maximum_height_m':float(heights.max()),
            'height_quantiles_m':np.quantile(heights,[0,.1,.25,.5,.75,.9,1]).tolist(),
            'height_classes':{'below_3m':int((heights<3).sum()),'3_to_5m':int(((heights>=3)&(heights<5)).sum()),'5_to_9m':int((heights>=5).sum())},
            'prototype_counts':dict(counts),'library':library,
            'source_weighted_triangles':sum(library[r['prototype']]['source_triangles'] for r in original),
            'render_weighted_triangles':sum(counts[i]*library[i]['render_triangles'] for i in counts),
            'viewport_weighted_triangles':sum(counts[i]*library[i]['view_triangles'] for i in counts),
            'selection_sha256':hashlib.sha256('\n'.join(sorted(selected)).encode()).hexdigest()}


def derived_material(source, cfg):
    name='MAT_V08_'+source.name
    mat=bpy.data.materials.get(name)
    if mat:
        return mat
    mat=source.copy();mat.name=name;mat['v08_owned']=True
    if mat.node_tree:
        for node in mat.node_tree.nodes:
            if node.type=='VALTORGB':
                for stop in node.color_ramp.elements:
                    color=list(stop.color)
                    stop.color=(*[min(1.,max(.012,c*cfg['foliage_value_factor'])) for c in color[:3]],color[3])
            if node.type=='HUE_SAT':
                node.inputs['Value'].default_value*=cfg['foliage_value_factor']
    return mat


def grass_proxy(source, name, collection, material):
    mesh=bpy.data.meshes.get(name+'_MESH')
    if mesh is None:
        b=bounds(source);size=max(.01,min(b[0][1]-b[0][0],b[1][1]-b[1][0]))
        height=min(.18,max(.035,b[2][1]*.75));vertices=[];faces=[]
        for i in range(6):
            angle=i*2.399963; x=math.cos(angle)*size*.2; y=math.sin(angle)*size*.2
            dx=math.cos(angle+1.57)*size*.045;dy=math.sin(angle+1.57)*size*.045
            off=len(vertices);vertices.extend([(x-dx,y-dy,0),(x+dx,y+dy,0),(x+size*.06,y,height)])
            faces.append((off,off+1,off+2))
        mesh=bpy.data.meshes.new(name+'_MESH');mesh['v08_owned']=True;mesh.from_pydata(vertices,[],faces);mesh.materials.append(material)
    return owned_object(name,mesh,collection)


def grass_libraries(scene, kind, cfg):
    source_collection=bpy.data.collections['V06_MASTER_'+kind]
    render=owned_collection('V08_MASTER_'+kind+'_RENDER');view=owned_collection('V08_MASTER_'+kind+'_VIEW')
    stats=[];viewmat=plain_material('MAT_V08_VIEW_GRASS',(.11,.19,.046))
    for proto,source in enumerate(source_collection.objects):
        original=source.data
        base=simplified_mesh(scene,original,f'V08_{kind}_BASE_{proto:03d}',cfg['render_triangle_ratio'])
        material_indices=np.empty(len(base.polygons),dtype=np.int32)
        base.polygons.foreach_get('material_index',material_indices)
        base.materials.clear()
        for mat in original.materials:base.materials.append(derived_material(mat,cfg))
        base.polygons.foreach_set('material_index',material_indices)
        base['v08_owned']=True
        variant_triangles=[]
        for variant,factor in enumerate(cfg['height_factors']):
            if kind=='MEADOW':factor*=cfg['ecological_height_factors'][proto%4]
            index=proto*4+variant;name=f'V08_{kind}_RENDER_{index:03d}'
            ob=bpy.data.objects.get(name)
            if ob is None:
                mesh=base.copy();mesh.name=name+'_MESH';mesh['v08_owned']=True
                xyz=np.empty(len(mesh.vertices)*3,dtype=np.float32);mesh.vertices.foreach_get('co',xyz);xyz=xyz.reshape((-1,3))
                root=cfg['root_preserve_z_m'];z=xyz[:,2];z[:]=np.where(z<=root,z,root+(z-root)*factor)
                # Shorten atlas middle/upper forms, retaining every basal vertex.
                card={i for p in mesh.polygons if p.material_index==3 for i in p.vertices}
                if card:
                    ids=np.array(sorted(card));old=xyz[ids,2];xyz[ids,2]=np.where(old<=root,old,root+(old-root)*cfg['dark_card_height_factor'])
                mesh.vertices.foreach_set('co',xyz.ravel());mesh.update()
                # Keep every low component; thin only disconnected tall accents.
                bm=bmesh.new();bm.from_mesh(mesh);bm.verts.ensure_lookup_table()
                seen=set();remove=[];component=0
                for vertex in bm.verts:
                    if vertex in seen:continue
                    stack=[vertex];seen.add(vertex);part=[]
                    while stack:
                        v=stack.pop();part.append(v)
                        for edge in v.link_edges:
                            other=edge.other_vert(v)
                            if other not in seen:seen.add(other);stack.append(other)
                    component+=1
                    priority=int.from_bytes(key(13708,f'{kind}:{proto}:{component}')[:8],'big')/2**64
                    if max(v.co.z for v in part)>.20 and priority>cfg['upper_density_factors'][variant]:
                        remove.extend(part)
                if remove:bmesh.ops.delete(bm,geom=remove,context='VERTS')
                bm.to_mesh(mesh);bm.free();mesh.update()
                owned_object(name,mesh,render)
            grass_proxy(original,f'V08_{kind}_VIEW_{index:03d}',view,viewmat)
            variant_triangles.append(triangles(bpy.data.objects[name].data))
        stats.append({'prototype':proto,'source_triangles':triangles(original),'render_triangles':triangles(base),
                      'render_triangles_by_variant':variant_triangles,
                      'source_bounds':bounds(original),'source_root_bounds':json.loads(original['v06_descriptor'])['root_bounds']})
    return render,view,stats


def point_arrays(mesh):
    n=len(mesh.vertices);xyz=np.empty(n*3,dtype=np.float32);mesh.vertices.foreach_get('co',xyz)
    p=np.empty(n,dtype=np.int32);mesh.attributes['prototype'].data.foreach_get('value',p)
    return xyz.reshape((-1,3)),p


def apply_grass(scene,cfg,seed,root):
    sources=[o for o in scene.objects if o.type=='MESH' and o.name.startswith(('V06_LAWN_','V06_MEADOW_','V07_MASK_','V07_SHOULDER_'))
             and not o.hide_render and any(m.type=='NODES' for m in o.modifiers)]
    # On reapplication, source ownership is recorded on the retained predecessor.
    sources.extend(o for o in scene.objects if o.get('v08_grass_predecessor') and o not in sources)
    stats={'point_count':0,'visible_render_instances':0,'viewport_instances':0,'source_weighted_triangles':0,
           'render_weighted_triangles':0,'libraries':{},'chunks':[]}
    col=owned_collection('V08_GRASS',root)
    for kind in ['LAWN','MEADOW']:
        render,view,library=grass_libraries(scene,kind,cfg);stats['libraries'][kind]=library
        group=instancer('V08_'+kind+'_GN',render,view,grass=True)
        for source in sorted(sources,key=lambda o:o.name):
            source_kind='LAWN' if 'LAWN' in source.name else 'MEADOW'
            if source_kind!=kind:continue
            name='V08_GRASS_'+source.name;n=len(source.data.vertices)
            ob=bpy.data.objects.get(name)
            if ob is None:
                mesh=source.data.copy();mesh.name=name+'_POINTS';mesh['v08_owned']=True
                ob=owned_object(name,mesh,col)
                mod=ob.modifiers.new('V08 linked grass render/work', 'NODES');mod.node_group=group
            mesh=ob.data;xyz,prototypes=point_arrays(mesh)
            x,y=xyz[:,0],xyz[:,1]
            field=.5+.18*np.sin(x/3.5)*np.cos(y/4.7)+.17*np.sin((x+y)/11)+.10*np.cos((x-2*y)/29)
            variant=np.clip((field*4).astype(np.int32),0,3)
            attr=mesh.attributes.get('v08_prototype') or mesh.attributes.new('v08_prototype','INT','POINT')
            attr.data.foreach_set('value',prototypes*4+variant)
            ids=np.arange(n,dtype=np.uint64)
            hashed=(ids*np.uint64(2654435761)+np.uint64(int.from_bytes(key(seed,source.name)[:4],'big')))
            keep=(hashed%cfg['viewport_stride'])==0
            mask=np.zeros(n,dtype=np.bool_)
            if mesh.attributes.get('v07_remove'):mesh.attributes['v07_remove'].data.foreach_get('value',mask)
            keep &= ~mask
            attr=mesh.attributes.get('v08_view_keep') or mesh.attributes.new('v08_view_keep','BOOLEAN','POINT')
            attr.data.foreach_set('value',keep)
            counts=np.bincount(prototypes[~mask],minlength=len(library))
            original_cost=sum(int(counts[i])*library[i]['source_triangles'] for i in range(len(library)))
            detailed_counts=np.bincount((prototypes*4+variant)[~mask],minlength=len(library)*4)
            new_cost=sum(int(detailed_counts[i*4+j])*library[i]['render_triangles_by_variant'][j]
                         for i in range(len(library)) for j in range(4))
            stats['point_count']+=n;stats['visible_render_instances']+=int((~mask).sum());stats['viewport_instances']+=int(keep.sum())
            stats['source_weighted_triangles']+=original_cost;stats['render_weighted_triangles']+=new_cost
            stats['chunks'].append({'source':source.name,'owned':ob.name,'points':n,'masked':int(mask.sum()),'viewport':int(keep.sum())})
            source['v08_grass_predecessor']=True;source.hide_render=True;source.hide_viewport=True
    return stats


def ground_materials(scene,cfg):
    changed=[]
    for name in ['V07_TERRAIN_NEAR','V07_TERRAIN_FAR','SITE_terrain_proxy']:
        ob=scene.objects.get(name)
        if ob is None:continue
        for i,source in enumerate(list(ob.data.materials)):
            if source is None or source.name.startswith('MAT_V08_GROUND_'):continue
            if 'LAWN_BASE' not in source.name and 'MEADOW_BASE' not in source.name:continue
            name='MAT_V08_GROUND_'+source.name
            mat=bpy.data.materials.get(name)
            if mat is None:
                mat=source.copy();mat.name=name;mat['v08_owned']=True
                for node in mat.node_tree.nodes:
                    if node.type=='HUE_SAT':node.inputs['Value'].default_value*=cfg['ground_value_factor']
            # Own the terrain data before changing its slots; geometry stays exact.
            if not ob.data.get('v08_owned'):
                ob.data.use_fake_user=True
                ob.data=ob.data.copy();ob.data.name='V08_GROUND_'+ob.name;ob.data['v08_owned']=True
            ob.data.materials[i]=mat;changed.append([ob.name,i,source.name,mat.name])
    return changed


def refill_removed_tree_clearings(scene,P,root):
    """Restore only the small grass exclusions exposed by forest thinning."""
    import forest_trail_v07 as v07
    cfg=P['vegetation_v08'];spec=cfg['refill'];seed=cfg['seed']
    original=json.loads(bpy.data.texts['V07_FOREST_REGISTRY.json'].as_string())
    final=json.loads(bpy.data.texts['V08_FOREST_REGISTRY.json'].as_string())
    selected={r['id'] for r in final};removed=[r for r in original if r['id'] not in selected]
    surface=v07.mapped_surface(scene,final=True)
    route=v07.Route(surface,P);kd=v07.tree_kd(final)
    descriptors=[]
    for i in range(96):
        mesh=bpy.data.objects[f'V08_MEADOW_RENDER_{i:03d}'].data
        xyz=np.empty(len(mesh.vertices)*3,dtype=np.float32);mesh.vertices.foreach_get('co',xyz);xyz=xyz.reshape((-1,3))
        t=np.empty(len(mesh.vertices),dtype=np.float32);mesh.attributes['v06_t'].data.foreach_get('value',t)
        basal=xyz[t<=.002001];rb=[[float(basal[:,k].min()),float(basal[:,k].max())] for k in range(3)]
        bm=bmesh.new()
        for v in xyz:bm.verts.new(v)
        convex=bmesh.ops.convex_hull(bm,input=list(bm.verts),use_existing_faces=False)
        vs={v for item in convex['geom'] if isinstance(item,bmesh.types.BMFace) for v in item.verts}
        hull=sorted(tuple(v.co) for v in vs);bm.free()
        descriptors.append({'root_bounds':rb,'hull':hull,'radius_3d':max(sum(c*c for c in v)**.5 for v in hull)})
    hard,posts,trunks=v07.hard_obstacles(scene)
    post_kd=v07.tree_kd([{'position':[x,y,0]} for x,y in posts])
    hard_boxes=[(p,(min(v[0] for v in p),max(v[0] for v in p),min(v[1] for v in p),max(v[1] for v in p))) for p in hard]
    rows=[];covered=set();duplicates=set()
    stats={'removed_root_targets':len(removed),'instances':0,'viewport_instances':0,'refinements':0,
           'support_rejected':0,'obstacle_rejected':0,'extent_rejected':0,'maximum_exposure_m':-1e20,
           'maximum_burial_m':0.,'covered_root_targets':0,'render_weighted_triangles':0,
           'centre_repairs':0,'retained_root_excluded_centres':[]}
    def place(x,y,identity,tier=1):
        tag=(round(x,5),round(y,5),tier)
        if tag in duplicates:return
        duplicates.add(tag)
        extent=surface.extent
        if not(extent[0]<=x<=extent[1] and extent[2]<=y<=extent[3]):
            stats['extent_rejected']+=1;return
        z,normal,face=v07.sample(surface,x,y)
        if normal.z<math.cos(math.radians(68)):
            stats['support_rejected']+=1;return
        rr=v07.rng(seed,'root-refill',identity,tier)
        proto=tier*4+(0 if 'centre-repair' in identity else rr.randrange(2))+(12 if normal.z<.5 else 0)
        field=.5+.18*math.sin(x/3.5)*math.cos(y/4.7)+.17*math.sin((x+y)/11)+.10*math.cos((x-2*y)/29)
        detail=proto*4+max(0,min(3,int(field*4)))
        desc=descriptors[detail]
        rotation=[v07.f32(v) for v in v07.pose(normal,rr.random()*math.tau)]
        hull=v07.projected_hull(desc['hull'],rotation,(x,y,z));extent=surface.extent
        if any(not(extent[0]<=a<=extent[1] and extent[2]<=b<=extent[3]) for a,b in hull):
            if tier<2:
                stats['refinements']+=1
                for dx in [-.03125,.03125]:
                    for dy in [-.03125,.03125]:place(v07.f32(x+dx),v07.f32(y+dy),identity+f':{dx}:{dy}',2)
                return
            stats['extent_rejected']+=1;return
        radius=desc['radius_3d']
        nearby_hard=[p for p,b in hard_boxes if x+radius>=b[0] and x-radius<=b[1] and y+radius>=b[2] and y-radius<=b[3]]
        if v07.footprint_hits_core(route,hull) or any(v07.polygon_intersects(hull,p) for p in nearby_hard):
            if tier<2:
                stats['refinements']+=1
                for dx in [-.03125,.03125]:
                    for dy in [-.03125,.03125]:place(v07.f32(x+dx),v07.f32(y+dy),identity+f':{dx}:{dy}',2)
                return
            stats['obstacle_rejected']+=1;return
        near=kd.find_range(Vector((x,y,0)),radius+.25001)
        near_posts=post_kd.find_range(Vector((x,y,0)),radius+.20001)
        if (any(v07.circle_intersects(hull,co.x,co.y,.25) for co,_,_ in near)
            or any(v07.circle_intersects(hull,co.x,co.y,.20) for co,_,_ in near_posts)
            or any(v07.circle_intersects(hull,a,b,.25) for a,b in trunks if math.hypot(x-a,y-b)<=radius+.25)):
            if tier<2:
                stats['refinements']+=1
                for dx in [-.03125,.03125]:
                    for dy in [-.03125,.03125]:place(v07.f32(x+dx),v07.f32(y+dy),identity+f':{dx}:{dy}',2)
                return
            stats['obstacle_rejected']+=1;return
        matrix=Euler(rotation).to_matrix()
        basal=[matrix@Vector(v) for v in v07.bounds_corners(desc['root_bounds'])]
        box=[x+min(v.x for v in basal),x+max(v.x for v in basal),y+min(v.y for v in basal),y+max(v.y for v in basal)]
        if box[0]<extent[0] or box[1]>extent[1] or box[2]<extent[2] or box[3]>extent[3]:
            stats['extent_rejected']+=1;return
        lo,hi,pieces=surface.range_over_box(box,(x,y,z),normal)
        span=hi-lo;headroom=max(0,desc['root_bounds'][2][1])/normal.z
        if span>.005 and tier<2:
            stats['refinements']+=1
            for dx in [-.03125,.03125]:
                for dy in [-.03125,.03125]:place(v07.f32(x+dx),v07.f32(y+dy),identity+f':{dx}:{dy}',2)
            return
        if span+headroom>.017:
            stats['support_rejected']+=1;return
        embed=.002+headroom
        rows.append({'position':[v07.f32(x),v07.f32(y),v07.f32(z+lo-embed)],
                     'prototype':proto,'rotation':rotation,'scale':[1.,1.,1.], 'root_id':identity.split('|')[0],
                     'v08_prototype':detail})
        covered.add(identity.split('|')[0])
        stats['maximum_exposure_m']=max(stats['maximum_exposure_m'],-.002)
        stats['maximum_burial_m']=max(stats['maximum_burial_m'],span+embed)
    step=spec['grid_m'];radius=spec['radius_m'];limit=math.ceil(radius/step)
    for root_index,row in enumerate(removed):
        if root_index%256==0:print('V08_REFILL_PROGRESS',root_index,len(removed),len(rows),flush=True)
        x,y=row['position'][:2]
        start_index=len(rows)
        for iy in range(-limit,limit+1):
            for ix in range(-limit,limit+1):
                dx=(ix+.5*(iy%2))*step;dy=iy*step*.8660254037844386
                if dx*dx+dy*dy>radius*radius:continue
                place(v07.f32(x+dx),v07.f32(y+dy),row['id']+f'|{ix}:{iy}')
        near_centre=any(math.hypot(r['position'][0]-x,r['position'][1]-y)<=.09 for r in rows[start_index:])
        if not near_centre:
            co,index,distance=kd.find(Vector((x,y,0)))
            if distance<=.25:
                stats['retained_root_excluded_centres'].append(row['id'])
            else:
                angle=math.atan2(y-co.y,x-co.x)
                for offset in [.06,.075,.085]:
                    for turn in [0.,math.pi/8,-math.pi/8]:
                        old_count=len(rows)
                        place(v07.f32(x+offset*math.cos(angle+turn)),v07.f32(y+offset*math.sin(angle+turn)),
                              row['id']+f'|centre-repair:{offset}:{turn}',2)
                        if len(rows)>old_count:
                            stats['centre_repairs']+=1;break
                    if len(rows)>old_count:break
    col=owned_collection('V08_ROOT_REFILL',root);group=bpy.data.node_groups['V08_MEADOW_GN']
    chunks=defaultdict(list)
    for row in rows:chunks[(math.floor(row['position'][0]/32),math.floor(row['position'][1]/32))].append(row)
    for (ix,iy),records in sorted(chunks.items()):
        ob=point_object(f'V08_GRASS_REFILL_{ix:+04d}_{iy:+04d}',records,col,group)
        ob['v08_refill']=True
        xyz,prototypes=point_arrays(ob.data);x,y=xyz[:,0],xyz[:,1]
        full=np.array([r['v08_prototype'] for r in records],dtype=np.int32)
        attr=ob.data.attributes.get('v08_prototype') or ob.data.attributes.new('v08_prototype','INT','POINT')
        attr.data.foreach_set('value',full)
        ids=np.arange(len(records),dtype=np.uint64);keep=(ids*np.uint64(2654435761))%cfg['grass']['viewport_stride']==0
        attr=ob.data.attributes.get('v08_view_keep') or ob.data.attributes.new('v08_view_keep','BOOLEAN','POINT')
        attr.data.foreach_set('value',keep)
        stats['viewport_instances']+=int(keep.sum())
        counts=np.bincount(full,minlength=96)
        for i,n in enumerate(counts):
            if n:stats['render_weighted_triangles']+=int(n)*triangles(bpy.data.objects[f'V08_MEADOW_RENDER_{i:03d}'].data)
    stats['instances']=len(rows);stats['covered_root_targets']=len(covered)
    stats['targets_without_refill']=sorted({r['id'] for r in removed}-covered)
    return stats


def apply_v08(scene,P,ROOT):
    started=time.time();before=random.getstate();cfg=P['vegetation_v08']
    assert not bpy.app.is_job_running('RENDER')
    assert bpy.data.texts.get('V07_FOREST_REGISTRY.json')
    root=owned_collection('98_VEGETATION_V08',scene.collection)
    forest=apply_forest(scene,cfg['forest'],cfg['seed'],root)
    grass=apply_grass(scene,cfg['grass'],cfg['seed'],root)
    refill=refill_removed_tree_clearings(scene,P,root)
    ground=ground_materials(scene,cfg['grass'])
    for group in bpy.data.node_groups:
        if group.get('v08_owned'):
            assert not any(n.bl_idname=='GeometryNodeRealizeInstances' for n in group.nodes)
    source_cost=forest['source_weighted_triangles']+grass['source_weighted_triangles']
    new_cost=forest['render_weighted_triangles']+grass['render_weighted_triangles']+refill['render_weighted_triangles']
    result={'forest':forest,'grass':grass,'refill':refill,'total_grass_instances':grass['visible_render_instances']+refill['instances'],
            'total_viewport_grass_instances':grass['viewport_instances']+refill['viewport_instances'],
            'ground_slots':ground,'source_weighted_triangles':source_cost,
            'render_weighted_triangles':new_cost,'render_geometry_ratio':new_cost/source_cost,
            'shoulder_disposition':cfg['shoulder_disposition'],'global_rng_unchanged':before==random.getstate(),
            'seconds':time.time()-started,'viewport_branch':'Is Viewport, linked '+cfg['forest'].get('viewport_model','coarse')+' trees and 1/128 grass points; render branch remains linked'}
    assert before==random.getstate()
    scene['vegetation_v08_summary']=json.dumps(result,sort_keys=True)
    return result

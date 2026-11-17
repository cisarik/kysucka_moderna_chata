"""Bounded V09 environment study derived explicitly from saved V08_view.

No operation runs on import. Existing geometry, point transforms, supported
roots, alpha/UVs and old datablocks are retained. New linked grass uses a
subset of the old points and derived upper forms; no full-scene regeneration.
"""
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import random

import bpy
import numpy as np
from mathutils import Vector


def _config_hash(cfg):
    return hashlib.sha256(json.dumps(cfg, sort_keys=True).encode()).hexdigest()


def _collection(name, parent=None):
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        col['v09_owned'] = True
    assert col.get('v09_owned'), name
    if parent is not None and col.name not in parent.children:
        parent.children.link(col)
    if parent is None:
        col.use_fake_user = True
    return col


def _object(name, data, col):
    ob = bpy.data.objects.get(name)
    if ob is None:
        ob = bpy.data.objects.new(name, data)
        ob['v09_owned'] = True
    assert ob.get('v09_owned'), name
    ob.data = data
    if ob.name not in col.objects:
        col.objects.link(ob)
    return ob


def _array(mesh, field, width=1, kind=np.float32):
    if field == 'position':
        data = np.empty(len(mesh.vertices)*3, dtype=np.float32)
        mesh.vertices.foreach_get('co', data)
        return data.reshape((-1, 3))
    attr = mesh.attributes[field]
    data = np.empty(len(attr.data)*width, dtype=kind)
    attr.data.foreach_get('vector' if width == 3 else 'value', data)
    return data.reshape((-1, width)) if width > 1 else data


def _triangles(mesh):
    return sum(len(p.vertices)-2 for p in mesh.polygons)


def _ramp_color(socket, nodes, links, cfg, label):
    """Grade only color. Alpha, shader mixing and material slots are untouched."""
    if socket.is_linked:
        incoming = socket.links[0].from_socket
    else:
        rgb = nodes.new('ShaderNodeRGB')
        rgb.outputs[0].default_value = socket.default_value
        incoming = rgb.outputs[0]
    hue = nodes.new('ShaderNodeHueSaturation')
    hue.label = label+' subtle leaf grade'
    hue.inputs['Saturation'].default_value = cfg['blade_saturation']
    hue.inputs['Value'].default_value = cfg['blade_value_factor']
    links.new(incoming, hue.inputs['Color'])
    mix = nodes.new('ShaderNodeMixRGB')
    mix.label = label+' narrow low-cover palette'
    mix.inputs[0].default_value = cfg['palette_mix']
    mix.inputs[2].default_value = (*cfg['palette_color_linear'], 1.)
    links.new(hue.outputs['Color'], mix.inputs[1])
    links.new(mix.outputs['Color'], socket)


def _leaf_material(source, cfg):
    name = 'MAT_V09_'+source.name
    mat = bpy.data.materials.get(name)
    if mat is not None:
        assert mat.get('v09_owned')
        return mat
    mat = source.copy()
    mat.name = name
    mat['v09_owned'] = True
    mat['v09_source'] = source.name
    assert mat.surface_render_method == source.surface_render_method
    assert mat.use_transparent_shadow == source.use_transparent_shadow
    if mat.node_tree:
        nodes, links = mat.node_tree.nodes, mat.node_tree.links
        for node in list(nodes):
            field = 'Base Color' if node.type == 'BSDF_PRINCIPLED' else 'Color' if node.type == 'BSDF_TRANSLUCENT' else None
            if field:
                _ramp_color(node.inputs[field], nodes, links, cfg, source.name)
    return mat


def _components(mesh):
    adjacency = [[] for _ in mesh.vertices]
    for e in mesh.edges:
        a, b = e.vertices
        adjacency[a].append(b)
        adjacency[b].append(a)
    seen = set()
    for i in range(len(adjacency)):
        if i in seen:
            continue
        stack = [i]
        seen.add(i)
        ids = []
        while stack:
            a = stack.pop()
            ids.append(a)
            for b in adjacency[a]:
                if b not in seen:
                    seen.add(b)
                    stack.append(b)
        yield np.array(ids, dtype=np.int32)


def _master(source, collection, cfg, seed):
    name = source.name.replace('V08_', 'V09_', 1)
    mesh = bpy.data.meshes.get(name+'_MESH')
    if mesh is None:
        old = source.data
        mesh = old.copy()
        mesh.name = name+'_MESH'
        mesh['v09_owned'] = True
        mesh['v09_source'] = old.name
        # Indexed assignment preserves polygon slot IDs, including atlas slot 3.
        for i, material in enumerate(old.materials):
            mesh.materials[i] = _leaf_material(material, cfg)
        xyz = _array(mesh, 'position')
        original = xyz.copy()
        t = _array(mesh, 'v06_t')
        roots = t <= cfg['root_preserve_t']
        atlas = np.zeros(len(xyz), dtype=np.bool_)
        for p in mesh.polygons:
            if p.material_index == 3:
                atlas[list(p.vertices)] = True
        entropy = int.from_bytes(hashlib.blake2b(f'{seed}:{name}'.encode(), digest_size=8).digest(), 'little')
        rng = np.random.default_rng(entropy)
        lawn = 'LAWN' in name
        for ids in _components(mesh):
            basal = ids[roots[ids]]
            if not len(basal):
                # Disconnected simplified upper fragments retain their old XY.
                basal = ids[np.argmin(original[ids, 2]):np.argmin(original[ids, 2])+1]
            centre = original[basal].mean(axis=0)
            upper = ids[~roots[ids] & (original[ids, 2] > cfg['root_preserve_z_m'])]
            if not len(upper):
                continue
            factor = (cfg['atlas_height_factor'] if atlas[ids].any() else
                      cfg['tall_height_factor'] if original[ids, 2].max() > .20 else cfg['low_height_factor'])
            if lawn:
                factor = max(.84, factor)
            factor = min(cfg['component_contraction_cap'], factor*rng.uniform(*cfg['height_random_range']))
            assert 0 < factor <= 1
            # A segment to a centroid of old vertices lies in the old convex
            # hull. Retaining exact basal vertices transfers support and masks
            # through every inherited rotation and scale, including slopes.
            xyz[upper] = centre+(original[upper]-centre)*factor
        assert np.array_equal(xyz[roots], original[roots])
        mesh['v09_envelope_method'] = 'Component upper vertices are convex combinations of their original vertex and an original basal centroid; exact roots retained'
        mesh.vertices.foreach_set('co', xyz.ravel())
        mesh.update()
    assert mesh.get('v09_owned')
    return _object(name, mesh, collection)


def _instancer(kind, render_collection, view_collection):
    name = 'V09_'+kind+'_GN'
    group = bpy.data.node_groups.get(name)
    if group is not None:
        assert group.get('v09_owned')
        return group
    group = bpy.data.node_groups.new(name, 'GeometryNodeTree')
    group['v09_owned'] = True
    group.interface.new_socket(name='Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
    group.interface.new_socket(name='Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    nodes, links = group.nodes, group.links
    inp, out = nodes.new('NodeGroupInput'), nodes.new('NodeGroupOutput')
    viewport = nodes.new('GeometryNodeIsViewport')
    switch = nodes.new('GeometryNodeSwitch')
    switch.input_type = 'GEOMETRY'
    links.new(viewport.outputs[0], switch.inputs['Switch'])
    links.new(switch.outputs[0], out.inputs[0])
    def attribute(name, dtype):
        node = nodes.new('GeometryNodeInputNamedAttribute')
        node.data_type = dtype
        node.inputs['Name'].default_value = name
        return node.outputs['Attribute']
    detail = attribute('v08_prototype', 'INT')
    rotation = attribute('rotation', 'FLOAT_VECTOR')
    scale = attribute('scale', 'FLOAT_VECTOR')
    for view, col, port in [(False, render_collection, 'False'), (True, view_collection, 'True')]:
        geo = inp.outputs[0]
        if view:
            delete = nodes.new('GeometryNodeDeleteGeometry')
            delete.domain = 'POINT'
            invert = nodes.new('FunctionNodeBooleanMath')
            invert.operation = 'NOT'
            links.new(attribute('v09_view_keep', 'BOOLEAN'), invert.inputs[0])
            links.new(invert.outputs[0], delete.inputs['Selection'])
            links.new(geo, delete.inputs['Geometry'])
            geo = delete.outputs[0]
        lib = nodes.new('GeometryNodeCollectionInfo')
        lib.inputs['Collection'].default_value = col
        lib.inputs['Separate Children'].default_value = True
        lib.inputs['Reset Children'].default_value = True
        instance = nodes.new('GeometryNodeInstanceOnPoints')
        instance.inputs['Pick Instance'].default_value = True
        links.new(geo, instance.inputs['Points'])
        links.new(lib.outputs['Instances'], instance.inputs['Instance'])
        for value, target in [(detail, 'Instance Index'), (rotation, 'Rotation'), (scale, 'Scale')]:
            links.new(value, instance.inputs[target])
        links.new(instance.outputs[0], switch.inputs[port])
    return group


def _smooth(a, b, x):
    q = np.clip((x-a)/(b-a), 0., 1.)
    return q*q*(3-2*q)


def _sample_points(source, cfg, camera, seed):
    mesh = source.data
    xyz = _array(mesh, 'position')
    camera_xy = np.array(camera['location'][:2])
    distance = np.linalg.norm(xyz[:, :2]-camera_xy, axis=1)
    house_distance = np.linalg.norm(xyz[:, :2]-[7.2, 4.2], axis=1)
    far = _smooth(cfg['distance_near_m'], cfg['distance_far_m'], distance)
    probability = 1-far*(1-cfg['far_keep_fraction'])
    house = 1-_smooth(cfg['house_keep_radius_m'], cfg['house_fade_radius_m'], house_distance)
    probability = np.maximum(probability, house)
    entropy = int.from_bytes(hashlib.blake2b(f'{seed}:{source.name}'.encode(), digest_size=8).digest(), 'little')
    rng = np.random.default_rng(entropy)
    keep = rng.random(len(xyz)) < probability
    mask = _array(mesh, 'v07_remove', kind=np.bool_) if mesh.attributes.get('v07_remove') else np.zeros(len(xyz), dtype=np.bool_)
    ids = np.flatnonzero(keep & ~mask)
    zones = np.where(distance < cfg['distance_near_m'], 0, np.where(distance < cfg['distance_far_m'], 1, 2))
    return xyz, ids, zones, mask


def _grass(scene, cfg, camera, seed, root):
    col = _collection('V09_GRASS', root)
    libraries, groups, cost = {}, {}, {}
    for kind in ['LAWN', 'MEADOW']:
        lib = _collection('V09_MASTER_'+kind+'_RENDER')
        sources = sorted(bpy.data.collections['V08_MASTER_'+kind+'_RENDER'].objects, key=lambda o:o.name)
        masters = [_master(o, lib, cfg, seed) for o in sources]
        libraries[kind] = [{'name':o.name, 'source':s.name, 'triangles':_triangles(o.data)} for o,s in zip(masters,sources)]
        cost[kind] = np.array([_triangles(o.data) for o in masters], dtype=np.int64)
        groups[kind] = _instancer(kind, lib, bpy.data.collections['V08_MASTER_'+kind+'_VIEW'])
    stats = {'zones':{zone:{'inherited_available':0,'active':0,'weighted_triangles':0} for zone in ['near','mid','far']},
             'chunks':[], 'libraries':libraries, 'active_points':0, 'inherited_visible_points':0,
             'weighted_triangles':0, 'unique_render_triangles':sum(r['triangles'] for rows in libraries.values() for r in rows),
             'retained_cloud_is_hidden':True, 'point_transform_changes':0, 'new_roots':0, 'support':'Exact inherited positions/rotations/scales/detail prototypes; basal vertices byte-identical; thinning is a subset.'}
    sources = sorted([o for o in scene.objects if o.type=='MESH' and o.name.startswith('V08_GRASS_')], key=lambda o:o.name)
    for source in sources:
        kind = 'LAWN' if 'LAWN' in source.name else 'MEADOW'
        xyz, ids, zones, mask = _sample_points(source, cfg, camera, seed)
        name = source.name.replace('V08_GRASS_', 'V09_GRASS_', 1)
        data = bpy.data.meshes.get(name+'_POINTS')
        if data is None:
            data = bpy.data.meshes.new(name+'_POINTS')
            data['v09_owned'] = True
            data['v09_source'] = source.data.name
            data.from_pydata(xyz[ids].tolist(), [], [])
            for field, dtype, width in [('prototype','INT',1), ('v08_prototype','INT',1), ('rotation','FLOAT_VECTOR',3), ('scale','FLOAT_VECTOR',3)]:
                attr = data.attributes.new(field, dtype, 'POINT')
                values = _array(source.data, field, width, np.int32 if dtype=='INT' else np.float32)[ids]
                attr.data.foreach_set('vector' if width==3 else 'value', values.ravel())
            attr = data.attributes.new('v09_source_index','INT','POINT')
            attr.data.foreach_set('value', ids.astype(np.int32))
            attr = data.attributes.new('v09_view_keep','BOOLEAN','POINT')
            attr.data.foreach_set('value', ids % cfg['viewport_stride'] == 0)
        assert data.get('v09_owned') and len(data.vertices)==len(ids)
        ob = _object(name, data, col)
        ob.matrix_world = source.matrix_world.copy()
        modifier = next((m for m in ob.modifiers if m.type=='NODES'), None)
        if modifier is None:
            modifier = ob.modifiers.new('V09 linked natural low cover', 'NODES')
        modifier.node_group = groups[kind]
        detail = _array(data, 'v08_prototype', kind=np.int32)
        weighted = int(cost[kind][detail].sum())
        for i, zone in enumerate(['near','mid','far']):
            row = stats['zones'][zone]
            row['inherited_available'] += int(((zones==i)&~mask).sum())
            row['active'] += int((zones[ids]==i).sum())
            row['weighted_triangles'] += int(cost[kind][detail[zones[ids]==i]].sum())
        stats['active_points'] += len(ids)
        stats['inherited_visible_points'] += int((~mask).sum())
        stats['weighted_triangles'] += weighted
        stats['chunks'].append({'source':source.name,'owned':name,'inherited':len(xyz),'active':len(ids),'weighted_triangles':weighted})
        source.hide_render = True
        source.hide_viewport = True
    return stats


def _ground_material(source, cfg):
    name = 'MAT_V09_SUBSTRATE_'+source.name
    mat = bpy.data.materials.get(name)
    if mat is not None:
        assert mat.get('v09_owned')
        return mat
    mat = source.copy()
    mat.name = name
    mat['v09_owned'] = True
    mat['v09_source'] = source.name
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    for node in list(nodes):
        if node.type == 'NORMAL_MAP':
            node.inputs['Strength'].default_value = cfg['normal_strength']
    coords = nodes.new('ShaderNodeTexCoord')
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 1/cfg['spatial_scale_m']
    noise.inputs['Detail'].default_value = 2.
    noise.inputs['Roughness'].default_value = .6
    links.new(coords.outputs['Object'], noise.inputs['Vector'])
    field = nodes.new('ShaderNodeMath')
    field.operation = 'MULTIPLY_ADD'
    field.inputs[1].default_value = cfg['variation_fraction']
    field.inputs[2].default_value = cfg['color_mix']-cfg['variation_fraction']/2
    links.new(noise.outputs['Fac'], field.inputs[0])
    for node in list(nodes):
        if node.type != 'BSDF_PRINCIPLED':
            continue
        base = node.inputs['Base Color']
        incoming = base.links[0].from_socket
        mix = nodes.new('ShaderNodeMixRGB')
        mix.label = 'V09 continuous subtle substrate'
        mix.inputs[2].default_value = (*cfg['color_linear'], 1.)
        links.new(field.outputs[0], mix.inputs[0])
        links.new(incoming, mix.inputs[1])
        links.new(mix.outputs[0], base)
        for link in list(node.inputs['Roughness'].links):
            links.remove(link)
        node.inputs['Roughness'].default_value = cfg['roughness']
    return mat


def _substrate(scene, cfg):
    changes = []
    for name in ['V07_TERRAIN_NEAR', 'V07_TERRAIN_FAR', 'SITE_terrain_proxy']:
        ob = scene.objects.get(name)
        if ob is None:
            continue
        if not ob.data.get('v09_owned'):
            original = ob.data
            original.use_fake_user = True
            ob.data = original.copy()
            ob.data.name = 'V09_SUBSTRATE_'+name
            ob.data['v09_owned'] = True
            ob.data['v09_source'] = original.name
        for index, mat in enumerate(list(ob.data.materials)):
            if mat.name.startswith('MAT_V09_SUBSTRATE_'):
                changes.append([name,index,mat['v09_source'],mat.name])
            elif 'LAWN_BASE' in mat.name or 'MEADOW_BASE' in mat.name:
                new = _ground_material(mat, cfg)
                ob.data.materials[index] = new
                changes.append([name,index,mat.name,new.name])
    return changes


def _lighting(scene, cfg, root):
    assert cfg['atmosphere_density'] == 0., 'No volume in this bounded pilot'
    original = bpy.data.worlds.get('V09_ENVIRONMENT_WORLD')
    if original is None:
        scene.world.use_fake_user = True
        world = scene.world.copy()
        world.name = 'V09_ENVIRONMENT_WORLD'
        world['v09_owned'] = True
        world['v09_source'] = scene.world.name
        world['v09_original_world'] = scene.world.name
        nodes, links = world.node_tree.nodes, world.node_tree.links
        source = Vector(cfg['sun_direction_to_source']).normalized()
        for node in nodes:
            if node.type == 'TEX_SKY':
                node.sun_elevation = math.asin(source.z)
                node.sun_rotation = math.atan2(source.y, source.x) % math.tau
            if node.type == 'BACKGROUND':
                node.inputs['Strength'].default_value = cfg['world_strength']
                if node.inputs['Color'].is_linked:
                    incoming = node.inputs['Color'].links[0].from_socket
                    tint = nodes.new('ShaderNodeMixRGB')
                    tint.blend_type = 'MULTIPLY'
                    tint.inputs[0].default_value = .12
                    tint.inputs[2].default_value = (*cfg['world_color_linear'],1.)
                    links.new(incoming,tint.inputs[1])
                    links.new(tint.outputs[0],node.inputs['Color'])
                else:
                    node.inputs['Color'].default_value = (*cfg['world_color_linear'],1.)
    else:
        world = original
    assert world.get('v09_owned')
    scene.world = world
    switched = []
    for name in ['SUN_key','FILL_front']:
        ob = scene.objects.get(name)
        if ob:
            ob.hide_render = True
            switched.append(name)
    name = cfg['sun_name']
    ob = bpy.data.objects.get(name)
    if ob is None:
        data = bpy.data.lights.new(name,'SUN')
        data['v09_owned'] = True
        ob = _object(name,data,root)
    assert ob.get('v09_owned')
    ob.data.energy = cfg['sun_energy']
    ob.data.color = cfg['sun_color_linear']
    ob.data.angle = math.radians(cfg['sun_angle_degrees'])
    direction = -Vector(cfg['sun_direction_to_source']).normalized()
    ob.rotation_euler = direction.to_track_quat('-Z','Y').to_euler()
    return {'world':world.name,'retained_original_world':world['v09_source'],'hidden_exterior_lights':switched,'sun':name,'volume':False}


def configure_review(scene, P):
    """Owned review camera/profile only; existing camera datablocks stay exact."""
    cfg = P['nature_study_v09']
    camera = cfg['camera']
    name = camera['name']
    ob = bpy.data.objects.get(name)
    if ob is None:
        data = bpy.data.cameras.new(name)
        data['v09_owned'] = True
        ob = _object(name,data,scene.collection)
    assert ob.get('v09_owned')
    ob.location = camera['location']
    ob.rotation_euler = (Vector(camera['target'])-ob.location).to_track_quat('-Z','Y').to_euler()
    ob.data.lens = camera['lens_mm']
    ob.data.sensor_width = camera['sensor_width_mm']
    ob.data.sensor_fit = 'HORIZONTAL'
    ob.data.shift_x = camera['shift_x']
    ob.data.shift_y = camera['shift_y']
    ob.data.clip_end = camera['clip_end_m']
    scene.camera = ob
    profile = cfg['render']
    scene.render.engine = 'CYCLES'
    scene.cycles.device = profile['device']
    scene.render.threads_mode = 'FIXED'
    scene.render.threads = profile['threads']
    scene.cycles.samples = profile['samples']
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = profile['denoiser']
    scene.cycles.denoising_use_gpu = False
    scene.cycles.denoising_prefilter = profile['prefilter']
    scene.cycles.denoising_quality = profile['quality']
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.adaptive_threshold = .01
    scene.cycles.adaptive_min_samples = 0
    scene.cycles.seed = profile['seed']
    scene.cycles.use_animated_seed = False
    scene.frame_set(profile['frame'])
    scene.render.resolution_x, scene.render.resolution_y = profile['resolution']
    scene.render.resolution_percentage = 100
    scene.render.use_border = False
    scene.render.use_crop_to_border = False
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.image_settings.color_depth = '8'
    scene.view_settings.view_transform = profile['view']
    scene.view_settings.look = profile['look']
    scene.view_settings.exposure = profile['exposure']
    scene.view_settings.gamma = profile['gamma']
    return ob


def apply_v09_study(scene, P, ROOT, *, lighting=True, grass=True):
    """Explicitly derive a study from the accepted V08_view, with local RNGs."""
    before = random.getstate()
    cfg = P['nature_study_v09']
    assert Path(ROOT).is_dir()
    assert bpy.data.texts.get('V08_FOREST_REGISTRY.json')
    assert not bpy.app.is_job_running('RENDER')
    digest = _config_hash(cfg)
    existing = scene.get('nature_study_v09_config')
    assert existing is None or existing == digest, 'Use a fresh accepted V08 input for changed study settings'
    root = _collection('99_NATURE_STUDY_V09',scene.collection)
    configure_review(scene,P)
    result = {'schema':1,'seed':cfg['seed'],'grass':None,'substrate':[], 'lighting':None,
              'camera':cfg['camera'],'config_sha256':digest,'source':'accepted saved V08_view only'}
    if grass:
        result['grass'] = _grass(scene,cfg['grass'],cfg['camera'],cfg['seed'],root)
        result['substrate'] = _substrate(scene,cfg['substrate'])
    if lighting:
        result['lighting'] = _lighting(scene,cfg['lighting'],root)
    assert before == random.getstate(), 'Global RNG changed'
    assert not any(n.bl_idname=='GeometryNodeRealizeInstances' for g in bpy.data.node_groups if g.get('v09_owned') for n in g.nodes)
    result['global_rng_unchanged'] = True
    scene['nature_study_v09_config'] = digest
    scene['nature_study_v09_summary'] = json.dumps(result,sort_keys=True)
    # Commit RNA transforms to matrices before readback or a second explicit
    # application; frame_set at the next call otherwise flushes the new sun.
    bpy.context.view_layer.update()
    return result

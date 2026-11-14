"""Bounded v03 timber/UV/fence refinement; import has no scene effects.

Called explicitly by the live MCP grant and the offline source builder.
Metres, local member axes, immutable CC0 image files, isolated local RNG.
"""
import hashlib
import math
import random
from pathlib import Path

import bpy
from mathutils import Matrix, Quaternion, Vector


EXTERIOR_COUNTS = {
    'CLADDING_front': 35, 'CLADDING_rear': 33, 'GABLE_timber': 16,
    'SOFFIT_wood': 2, 'WOOD_BAY_post': 2,
}


def exterior_objects(scene):
    objects = []
    for prefix, count in EXTERIOR_COUNTS.items():
        group = sorted((o for o in scene.objects if o.name.startswith(prefix)), key=lambda o: o.name)
        assert len(group) == count, (prefix, len(group), count)
        objects.extend(group)
    other = scene.objects.get('GABLE_other_proposed')
    assert other is not None and other.type == 'MESH'
    objects.append(other)
    assert len(objects) == 89 and len({o.name for o in objects}) == 89
    assert all(o.type == 'MESH' for o in objects)
    return sorted(objects, key=lambda o: o.name)


def configure_comparison_render(scene):
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.render.resolution_x = 1448
    scene.render.resolution_y = 1086
    scene.render.resolution_percentage = 100
    scene.render.pixel_aspect_x = 1.0
    scene.render.pixel_aspect_y = 1.0
    scene.cycles.samples = 96
    assert scene.cycles.denoiser == 'OPENIMAGEDENOISE', 'Required OIDN denoiser unavailable'
    scene.cycles.use_denoising = True
    for layer in scene.view_layers:
        if hasattr(layer.cycles, 'use_denoising'):
            layer.cycles.use_denoising = True
    scene.cycles.seed = 0
    scene.cycles.use_animated_seed = False
    scene.frame_set(0)
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'None'
    scene.view_settings.exposure = 0.0
    scene.view_settings.gamma = 1.0
    scene.render.film_transparent = False
    scene.render.image_settings.file_format = 'PNG'
    scene.render.threads_mode = 'FIXED'
    scene.render.threads = 8


def _node(nodes, kind, name):
    node = nodes.new(kind)
    node.name = name
    node.label = name
    return node


def _image(project_root, relative_path, color_space):
    path = Path(project_root) / relative_path
    assert path.is_file() and path.resolve() == path and not path.is_symlink(), path
    image = bpy.data.images.load(str(path), check_existing=True)
    image.name = path.name
    image.colorspace_settings.name = color_space
    # A fresh factory scene has no blend-relative base path until its first save.
    # Pack from the verified absolute source before retaining the portable path.
    if not image.packed_file:
        image.pack()
    image.filepath = '//../' + relative_path
    return image


def _material(name, spec, project_root, fence=False):
    material = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    material.use_nodes = True
    material['asset_origin'] = 'Poly Haven CC0: ' + spec['asset']
    material['physical_tile_m'] = spec['tile_m']
    material['native_grain_axis'] = spec['native_grain_axis']
    nodes, links = material.node_tree.nodes, material.node_tree.links
    nodes.clear()
    uv = _node(nodes, 'ShaderNodeUVMap', 'Metric UVMap')
    uv.uv_map = 'UVMap'
    maps = {}
    for role in ('diff', 'rough', 'nor_gl'):
        tex = _node(nodes, 'ShaderNodeTexImage', role)
        tex.image = _image(project_root, spec['maps'][role], 'sRGB' if role == 'diff' else 'Non-Color')
        tex.extension = 'REPEAT'
        tex.interpolation = 'Linear'
        links.new(uv.outputs['UV'], tex.inputs['Vector'])
        maps[role] = tex

    samples = {role: tex.outputs['Color'] for role, tex in maps.items()}
    if spec.get('dephase_tiles', False):
        phase_uv = _node(nodes, 'ShaderNodeVectorMath', 'Translated secondary texture phase')
        phase_uv.operation = 'ADD'
        phase_uv.inputs[1].default_value = (*spec['phase_offset_uv'], 0.0)
        links.new(uv.outputs['UV'], phase_uv.inputs[0])
        phase_noise = _node(nodes, 'ShaderNodeTexNoise', 'Slow aperiodic phase blend')
        phase_noise.inputs['Scale'].default_value = spec['phase_blend_scale']
        phase_noise.inputs['Detail'].default_value = 2.0
        links.new(uv.outputs['UV'], phase_noise.inputs['Vector'])
        phase_mask = _node(nodes, 'ShaderNodeMapRange', 'Phase blend mask')
        phase_mask.inputs['From Min'].default_value = 0.35
        phase_mask.inputs['From Max'].default_value = 0.65
        phase_mask.clamp = True
        links.new(phase_noise.outputs['Fac'], phase_mask.inputs['Value'])
        for role, tex in maps.items():
            secondary = _node(nodes, 'ShaderNodeTexImage', role + ' translated phase')
            secondary.image = tex.image
            secondary.extension = 'REPEAT'
            secondary.interpolation = 'Linear'
            links.new(phase_uv.outputs['Vector'], secondary.inputs['Vector'])
            blend = _node(nodes, 'ShaderNodeMixRGB', role + ' aperiodic blend')
            links.new(phase_mask.outputs['Result'], blend.inputs[0])
            links.new(tex.outputs['Color'], blend.inputs[1])
            links.new(secondary.outputs['Color'], blend.inputs[2])
            samples[role] = blend.outputs['Color']

    info = _node(nodes, 'ShaderNodeObjectInfo', 'Stable per-object variation')
    grade = _node(nodes, 'ShaderNodeHueSaturation', 'Timber color grade')
    grade.inputs['Saturation'].default_value = spec['saturation']
    grade.inputs['Value'].default_value = spec['value']
    links.new(samples['diff'], grade.inputs['Color'])
    brightness = _node(nodes, 'ShaderNodeMapRange', 'Brightness variation')
    brightness.inputs['From Min'].default_value = 0.0
    brightness.inputs['From Max'].default_value = 1.0
    brightness.inputs['To Min'].default_value = spec['brightness_range'][0]
    brightness.inputs['To Max'].default_value = spec['brightness_range'][1]
    links.new(info.outputs['Random'], brightness.inputs['Value'])
    color = _node(nodes, 'ShaderNodeMixRGB', 'Graded per-board color')
    color.blend_type = 'MULTIPLY'
    color.inputs[0].default_value = 1.0
    links.new(grade.outputs['Color'], color.inputs[1])
    links.new(brightness.outputs['Result'], color.inputs[2])
    base_color = color.outputs['Color']

    if fence:
        cap = _node(nodes, 'ShaderNodeAttribute', 'Local cap mask')
        cap.attribute_name = 'V03_endgrain'
        rings = _node(nodes, 'ShaderNodeTexWave', 'Subtle split end grain')
        rings.wave_type = 'RINGS'
        rings.rings_direction = 'Z'
        rings.inputs['Scale'].default_value = 35.0
        rings.inputs['Distortion'].default_value = 2.0
        rings.inputs['Detail Scale'].default_value = 1.5
        links.new(uv.outputs['UV'], rings.inputs['Vector'])
        end_tone = _node(nodes, 'ShaderNodeMapRange', 'End grain restrained tone')
        end_tone.inputs['To Min'].default_value = 0.65
        end_tone.inputs['To Max'].default_value = 1.0
        links.new(rings.outputs['Fac'], end_tone.inputs['Value'])
        end_color = _node(nodes, 'ShaderNodeMixRGB', 'End grain color')
        end_color.blend_type = 'MULTIPLY'
        end_color.inputs[0].default_value = 1.0
        links.new(base_color, end_color.inputs[1])
        links.new(end_tone.outputs['Result'], end_color.inputs[2])
        mix_cap = _node(nodes, 'ShaderNodeMixRGB', 'Caps only')
        links.new(cap.outputs['Fac'], mix_cap.inputs[0])
        links.new(base_color, mix_cap.inputs[1])
        links.new(end_color.outputs['Color'], mix_cap.inputs[2])
        base_color = mix_cap.outputs['Color']

    rough = _node(nodes, 'ShaderNodeMapRange', 'Exterior roughness range')
    rough.inputs['To Min'].default_value = spec['roughness_map_range'][0]
    rough.inputs['To Max'].default_value = spec['roughness_map_range'][1]
    links.new(samples['rough'], rough.inputs['Value'])
    variation = _node(nodes, 'ShaderNodeMath', 'Roughness variation scale')
    variation.operation = 'MULTIPLY_ADD'
    variation.inputs[1].default_value = 0.04
    variation.inputs[2].default_value = -0.02
    links.new(info.outputs['Random'], variation.inputs[0])
    add = _node(nodes, 'ShaderNodeMath', 'Map plus variation')
    add.operation = 'ADD'
    links.new(rough.outputs['Result'], add.inputs[0])
    links.new(variation.outputs[0], add.inputs[1])
    clamp = _node(nodes, 'ShaderNodeClamp', 'Finish roughness limits')
    clamp.inputs['Min'].default_value = spec['roughness_limits'][0]
    clamp.inputs['Max'].default_value = spec['roughness_limits'][1]
    links.new(add.outputs[0], clamp.inputs['Value'])

    normal = _node(nodes, 'ShaderNodeNormalMap', 'OpenGL tangent normal')
    normal.space = 'TANGENT'
    normal.uv_map = 'UVMap'
    normal.inputs['Strength'].default_value = spec['normal_strength']
    links.new(samples['nor_gl'], normal.inputs['Color'])
    micro = _node(nodes, 'ShaderNodeTexNoise', 'Subtle micro relief')
    micro.inputs['Scale'].default_value = 95.0 if fence else 250.0
    micro.inputs['Detail'].default_value = 2.0
    links.new(uv.outputs['UV'], micro.inputs['Vector'])
    bump = _node(nodes, 'ShaderNodeBump', 'Submillimetre relief')
    bump.inputs['Distance'].default_value = spec['bump_distance_m']
    bump.inputs['Strength'].default_value = spec['bump_strength']
    links.new(micro.outputs['Fac'], bump.inputs['Height'])
    links.new(normal.outputs['Normal'], bump.inputs['Normal'])

    bsdf = _node(nodes, 'ShaderNodeBsdfPrincipled', 'Timber BSDF')
    bsdf.inputs['Metallic'].default_value = 0.0
    bsdf.inputs['Coat Weight'].default_value = 0.0
    links.new(base_color, bsdf.inputs['Base Color'])
    links.new(clamp.outputs['Result'], bsdf.inputs['Roughness'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    output = _node(nodes, 'ShaderNodeOutputMaterial', 'Timber output')
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    for index, node in enumerate(nodes):
        node.location = ((index % 5) * 230, -(index // 5) * 210)
    return material


def _offset(name):
    digest = hashlib.sha256(name.encode()).digest()
    return tuple(int.from_bytes(digest[i:i+8], 'big') / 2**64 for i in (0, 8))


def _metric_uv(obj, spec, kind):
    mesh = obj.data
    mesh.update()
    layer = mesh.uv_layers.get('UVMap') or mesh.uv_layers.new(name='UVMap')
    mesh.uv_layers.active = layer
    layer.active_render = True
    du, dv = _offset(obj.name)
    tile = spec['tile_m']
    cap_attribute = None
    if kind == 'fence':
        cap_attribute = mesh.attributes.get('V03_endgrain') or mesh.attributes.new('V03_endgrain', 'FLOAT', 'FACE')
    for face in mesh.polygons:
        if kind == 'horizontal':
            axis_u = Vector((1, 0, 0))
            axis_v = Vector((0, 0, 1)) if abs(face.normal.y) >= abs(face.normal.z) else Vector((0, 1, 0))
        elif kind == 'soffit':
            sign = 1 if obj.name.endswith('_0') else -1
            axis_u, axis_v = Vector((1, 0, 0)), Vector((0, 1, sign)).normalized()
        elif kind == 'gable':
            axis_u, axis_v = Vector((0, 0, 1)), Vector((0, 1, 0))
        else:
            axis_u = Vector((0, 0, 1))
            axis_v = Vector((0, 1, 0)) if abs(face.normal.x) >= abs(face.normal.y) else Vector((1, 0, 0))
        is_cap = abs(face.normal.dot(axis_u)) > 0.85
        if is_cap:
            axis_u, axis_v = (Vector((0, 1, 0)), Vector((0, 0, 1))) if kind == 'horizontal' else (Vector((1, 0, 0)), Vector((0, 1, 0)))
        if cap_attribute is not None:
            cap_attribute.data[face.index].value = 1.0 if is_cap else 0.0
        for loop_index in face.loop_indices:
            co = mesh.vertices[mesh.loops[loop_index].vertex_index].co
            p = Vector(tuple(co[i] * abs(obj.scale[i]) for i in range(3)))
            u, v = p.dot(axis_u) / tile + du, p.dot(axis_v) / tile + dv
            layer.data[loop_index].uv = (v, u) if spec['native_grain_axis'] == 'V' else (u, v)
    assert uv_degenerate_faces(obj) == 0, obj.name


def uv_degenerate_faces(obj):
    layer = obj.data.uv_layers.get('UVMap')
    if layer is None:
        return len(obj.data.polygons)
    total = 0
    for face in obj.data.polygons:
        points = [layer.data[i].uv for i in face.loop_indices]
        area = sum(a.x*b.y-b.x*a.y for a, b in zip(points, points[1:]+points[:1]))
        total += abs(area) < 1e-12
    return total


def _mesh_object(name, vertices, faces, material, collection, bevel):
    mesh = bpy.data.meshes.new(name + '_mesh')
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    mesh.materials.append(material)
    if bevel:
        mod = obj.modifiers.new('Rustic edge wear', 'BEVEL')
        mod.width, mod.segments = bevel, 2
        obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj


def _stake(name, point, tangent, width, depth, top_z, lean_deg, rng, spec, material, collection):
    height = top_z - spec['foot_z']
    corners = [(-width/2, -depth/2), (width/2, -depth/2), (width/2, depth/2), (-width/2, depth/2)]
    vertices = []
    for level in (0.0, 0.72, 1.0):
        for j, (x, y) in enumerate(corners):
            dx = rng.uniform(-0.002, 0.002) if level else 0.0
            dy = rng.uniform(-0.002, 0.002) if level else 0.0
            chip = rng.uniform(0.006, 0.025) if level == 1.0 and j else 0.0
            vertices.append((x + dx, y + dy, level * height - chip))
    vertices.append((width*.06, -depth*.04, height-.018))
    faces = [(3, 2, 1, 0)]
    for ring in (0, 1):
        for j in range(4):
            faces.append((4*ring+j, 4*ring+(j+1)%4, 4*(ring+1)+(j+1)%4, 4*(ring+1)+j))
    faces.extend((8+j, 8+(j+1)%4, 12) for j in range(4))
    obj = _mesh_object(name, vertices, faces, material, collection, spec['bevel_m'])
    obj.location = (point.x, point.y, spec['foot_z'])
    up = Vector((0, 0, 1))
    cross = Vector((-tangent.y, tangent.x, 0))
    basis = Matrix((tangent, cross, up)).transposed().to_quaternion()
    azimuth = rng.uniform(0, math.tau)
    lean = Quaternion(Vector((math.cos(azimuth), math.sin(azimuth), 0)), math.radians(lean_deg))
    obj.rotation_mode = 'QUATERNION'
    obj.rotation_quaternion = basis @ lean
    return obj


def _rail(name, start, end, material, collection, spec):
    direction = end-start
    length = direction.length
    w, d = spec['rail_section_m']
    vertices = [(x*w/2, y*d/2, z*length/2) for z in (-1, 1) for y in (-1, 1) for x in (-1, 1)]
    faces = [(0, 2, 3, 1), (4, 5, 7, 6), (0, 1, 5, 4), (2, 6, 7, 3), (0, 4, 6, 2), (1, 3, 7, 5)]
    obj = _mesh_object(name, vertices, faces, material, collection, spec['bevel_m'])
    obj.location = (start+end)/2
    obj.rotation_mode = 'QUATERNION'
    obj.rotation_quaternion = direction.to_track_quat('Z', 'Y')
    return obj


def _foreground_fence(scene, spec, material, timber_spec):
    rng = random.Random(spec['seed'])
    points = [Vector((p[0], p[1], 0)) for p in spec['polyline_xy']]
    lengths = [(b-a).length for a, b in zip(points, points[1:])]
    length = sum(lengths)
    anchor_s = lengths[0]/length if len(points) == 3 else spec['anchor_s']
    def at(s):
        distance = s * length
        for a, b, segment_length in zip(points, points[1:], lengths):
            if distance <= segment_length + 1e-8:
                return a+(b-a)*min(1, distance/segment_length), (b-a).normalized()
            distance -= segment_length
        return points[-1], (points[-1]-points[-2]).normalized()
    for obj in list(scene.objects):
        if obj.name.startswith(('FENCE_post_proxy', 'FENCE_rail_proxy')):
            data = obj.data
            bpy.data.objects.remove(obj, do_unlink=True)
            if data.users == 0:
                bpy.data.meshes.remove(data)
    collection = bpy.data.collections['70_SITE']
    posts = []
    for index in range(spec['post_count']):
        anchor = index == spec['anchor_index']
        if index <= spec['anchor_index']:
            s = anchor_s * index / spec['anchor_index']
        else:
            s = anchor_s + (1-anchor_s) * (index-spec['anchor_index']) / (spec['post_count']-1-spec['anchor_index'])
        jitter = rng.uniform(-spec['spacing_jitter_m'], spec['spacing_jitter_m'])
        if index not in (0, spec['anchor_index'], spec['post_count']-1):
            s += jitter / length
        width = spec['stake_width_m'] + rng.uniform(-spec['width_jitter_m'], spec['width_jitter_m'])
        depth = spec['stake_depth_m'] + rng.uniform(-spec['depth_jitter_m'], spec['depth_jitter_m'])
        top = spec['top_z'] + rng.uniform(-spec['top_jitter_m'], spec['top_jitter_m'])
        lean = rng.uniform(-spec['max_lean_deg'], spec['max_lean_deg'])
        if anchor:
            width, depth = spec['anchor_section_m']
            top = spec['anchor_top_z']
        point, tangent = at(s)
        name = 'FENCE_post_proxy' + (f'.{index:03d}' if index else '')
        obj = _stake(name, point, tangent, width, depth, top, lean, rng, spec, material, collection)
        obj['v03_role'] = 'anchor' if anchor else 'split_stake'
        obj['v03_arclength_fraction'] = s
        _metric_uv(obj, timber_spec, 'fence')
        posts.append(obj)
    camera_xy = Vector((scene.camera.location.x, scene.camera.location.y, 0))
    rails = []
    for z in spec['rail_heights_z']:
        for a, b in zip(points, points[1:]):
            tangent = (b-a).normalized()
            normal = Vector((tangent.y, -tangent.x, 0))
            if normal.dot(camera_xy-(a+b)/2) < 0:
                normal.negate()
            offset = normal * spec['rail_camera_offset_m']
            start, end = a+offset+Vector((0, 0, z)), b+offset+Vector((0, 0, z))
            name = 'FENCE_rail_proxy' + (f'.{len(rails):03d}' if rails else '')
            obj = _rail(name, start, end, material, collection, spec)
            _metric_uv(obj, timber_spec, 'fence')
            rails.append(obj)
    return posts, rails


def apply_v03(scene, parameters, project_root):
    """Replace only authorized timber slots/UVs and fence; preserve global RNG."""
    before_random = random.getstate()
    targets = exterior_objects(scene)
    exterior = _material('MAT_TIMBER_EXTERIOR', parameters['exterior_timber'], project_root)
    fence = _material('MAT_TIMBER_FENCE', parameters['fence_timber'], project_root, fence=True)
    for obj in targets:
        if obj.data.users > 1:
            obj.data = obj.data.copy()
        obj.data.materials.clear()
        obj.data.materials.append(exterior)
        kind = ('horizontal' if obj.name.startswith('CLADDING_') else
                'soffit' if obj.name.startswith('SOFFIT_wood') else
                'gable' if obj.name.startswith('GABLE_') else 'upright')
        _metric_uv(obj, parameters['exterior_timber'], kind)
    posts, rails = _foreground_fence(scene, parameters['foreground_fence'], fence, parameters['fence_timber'])
    bpy.context.view_layer.update()
    assert random.getstate() == before_random, 'Refinement changed global random stream'
    return {'exterior_objects': len(targets), 'fence_posts': len(posts), 'fence_rails': len(rails),
            'global_rng_unchanged': True, 'trial': parameters['foreground_fence']['selected_trial']}

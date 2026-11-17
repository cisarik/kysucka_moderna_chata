"""Deterministic owned V07 forest, supported trail and local vegetation treatment.

Explicit invocation only. Import performs no scene mutation or network access.
The V06 point layers and terrain are immutable baselines, retained in the scene.
"""
import array
import bisect
import collections
import hashlib
import json
import math
from pathlib import Path
import random
from types import SimpleNamespace

import bpy
import bmesh
from mathutils import Vector, Euler
from mathutils.geometry import convex_hull_2d, delaunay_2d_cdt, tessellate_polygon
from mathutils.kdtree import KDTree

from vegetation_v06 import Surface, field, smooth, pose
from site_v05 import inside_polygon


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def order_key(seed, *keys):
    return hashlib.blake2b(':'.join(map(str, (seed,) + keys)).encode(), digest_size=16).digest()


def rng(seed, *keys):
    return random.Random(int.from_bytes(order_key(seed, *keys), 'big'))


def f32(value):
    return array.array('f', [value])[0]


def owned_collection(name, parent=None):
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        col['v07_owned'] = True
    assert col.get('v07_owned'), name
    if parent is not None and name not in parent.children:
        parent.children.link(col)
    if parent is None:
        col.use_fake_user = True
    return col


def owned_mesh(name, vertices, faces, materials=()):
    me = bpy.data.meshes.get(name)
    if me is None:
        me = bpy.data.meshes.new(name)
        me['v07_owned'] = True
    assert me.get('v07_owned'), name
    me.clear_geometry()
    me.from_pydata(vertices, [], faces)
    me.update()
    me.materials.clear()
    for mat in materials:
        me.materials.append(mat)
    return me


def owned_object(name, data, col):
    ob = bpy.data.objects.get(name)
    if ob is None:
        ob = bpy.data.objects.new(name, data)
        ob['v07_owned'] = True
        col.objects.link(ob)
    else:
        assert ob.get('v07_owned'), name
        ob.data = data
        if name not in col.objects:
            col.objects.link(ob)
    ob.hide_render = False
    ob.hide_viewport = False
    return ob


def mapped_surface(scene, final=False):
    names = ['V07_TERRAIN_NEAR', 'V07_TERRAIN_FAR'] if final else ['V06_TERRAIN_NEAR', 'V06_TERRAIN_FAR']
    assert all(name in scene.objects for name in names), names
    mapping = dict(zip(['V06_TERRAIN_NEAR', 'V06_TERRAIN_FAR'], (scene.objects[n] for n in names)))
    return Surface(SimpleNamespace(objects=mapping))


def sample(surface, x, y):
    x0, x1, y0, y1 = surface.extent
    assert x0-1e-5 <= x <= x1+1e-5 and y0-1e-5 <= y <= y1+1e-5, (x, y, surface.extent)
    xx = max(x0+.0001, min(x1-.0001, x))
    yy = max(y0+.0001, min(y1-.0001, y))
    z, normal, face = surface.sample(xx, yy)
    a, b, c = surface.planes[face]
    return a*x+b*y+c, normal, face


def baseline_forest(scene):
    records = []
    for ob in sorted(scene.objects, key=lambda o: o.name):
        if not ob.name.startswith('V06_FOREST_') or ob.type != 'MESH':
            continue
        assert all(abs(ob.matrix_world[r][c]-(1 if r == c else 0)) < 1e-8
                   for r in range(4) for c in range(4)), ob.name
        for index, point in enumerate(ob.data.vertices):
            records.append({'id': f'{ob.name}:{index}', 'position': list(point.co),
                            'prototype': ob.data.attributes['prototype'].data[index].value,
                            'rotation': list(ob.data.attributes['rotation'].data[index].vector),
                            'scale': list(ob.data.attributes['scale'].data[index].vector),
                            'source': 'saved-post-compression-v06'})
    assert len(records) == 12833, len(records)
    return records


def tree_descriptors():
    result = []
    for index in range(5):
        ob = bpy.data.objects[f'V06_TREE_MASTER_{index}']
        me = ob.data
        bounds = [[min(v.co[k] for v in me.vertices), max(v.co[k] for v in me.vertices)] for k in range(3)]
        bark = set()
        for face in me.polygons:
            if face.material_index == 0:
                bark.update(face.vertices)
        low = min(me.vertices[i].co.z for i in bark)
        roots = [me.vertices[i].co.copy() for i in bark if me.vertices[i].co.z <= low+.04]
        assert roots
        rb = [[min(v[k] for v in roots), max(v[k] for v in roots)] for k in range(3)]
        result.append({'mesh': me, 'bounds': bounds, 'height': bounds[2][1]-bounds[2][0],
                       'root_bounds': rb, 'root_count': len(roots)})
    return result


class Route:
    """Finite compressed-world centreline and a bounded cut/fill height field."""
    def __init__(self, surface, P):
        self.surface = surface
        self.cfg = P['forest_trail_v07']['route']
        self.threshold = P['forest_trail_v07']['threshold']
        self.garden = P['site_v05']['garden_polygon']
        points = self.cfg['controls_xy']
        times = [0.]
        for a, b in zip(points, points[1:]):
            times.append(times[-1]+math.dist(a, b))
        tangents = []
        for i, p in enumerate(points):
            if i == 0:
                v = Vector((0, -1))
            elif i == len(points)-1:
                v = Vector((0, 1))
            else:
                v = (Vector(points[i+1])-Vector(points[i-1]))/(times[i+1]-times[i-1])
            tangents.append(v*self.cfg['tangent_factor'])
        self.xy = []
        for i, (a, b) in enumerate(zip(points, points[1:])):
            dt = times[i+1]-times[i]
            count = max(2, math.ceil(dt/self.cfg['sample_m']))
            while True:
                segment = []
                for j in range(count+1):
                    t = j/count
                    p = ((2*t**3-3*t*t+1)*Vector(a)+(t**3-2*t*t+t)*dt*tangents[i]
                         +(-2*t**3+3*t*t)*Vector(b)+(t**3-t*t)*dt*tangents[i+1])
                    segment.append(tuple(p))
                maximum = max(math.dist(p, q) for p, q in zip(segment, segment[1:]))
                if maximum <= self.cfg['sample_m']:
                    break
                count = max(count+1, math.ceil(count*maximum/self.cfg['sample_m']))
            self.xy.extend(segment[:-1])
        self.xy.append(tuple(points[-1]))
        self.station = [0.]
        for a, b in zip(self.xy, self.xy[1:]):
            self.station.append(self.station[-1]+math.dist(a, b))
        self.length = self.station[-1]
        self.raw_z = [sample(surface, *p)[0] for p in self.xy]
        self.kd = KDTree(len(self.xy))
        for i, (x, y) in enumerate(self.xy):
            self.kd.insert(Vector((x, y, 0)), i)
        self.kd.balance()
        self.tangent = []
        for i in range(len(self.xy)):
            a = self.xy[max(0, i-1)]
            b = self.xy[min(len(self.xy)-1, i+1)]
            if i == 0:
                t = Vector((0, -1))
            elif i == len(self.xy)-1:
                t = Vector((0, 1))
            else:
                t = (Vector(b)-Vector(a)).normalized()
            self.tangent.append(tuple(t))
        ground = self.raw_z.copy()
        for i, s in enumerate(self.station):
            if s <= self.threshold['flat_outside_gate_m']:
                ground[i] = self.threshold['top_z']-self.cfg['gravel_thickness_m']
            elif s < 1.5:
                w = smooth(self.threshold['flat_outside_gate_m'], 1.5, s)
                ground[i] = (1-w)*(self.threshold['top_z']-self.cfg['gravel_thickness_m'])+w*ground[i]
        lower = ground.copy()
        upper = ground.copy()
        g = self.cfg['maximum_grade']
        for i in range(1, len(ground)):
            d = g*(self.station[i]-self.station[i-1])
            upper[i] = min(upper[i], upper[i-1]+d)
            lower[i] = max(lower[i], lower[i-1]-d)
        for i in range(len(ground)-2, -1, -1):
            d = g*(self.station[i+1]-self.station[i])
            upper[i] = min(upper[i], upper[i+1]+d)
            lower[i] = max(lower[i], lower[i+1]-d)
        self.z = [(a+b)/2 for a, b in zip(upper, lower)]
        self.profile_adjustment = max(abs(a-b) for a, b in zip(self.z, self.raw_z))
        assert self.profile_adjustment <= self.cfg['maximum_profile_grading_m']+1e-6, self.profile_adjustment
        self.threshold_end = bisect.bisect_left(self.station, self.threshold['flat_outside_gate_m'])
        self.core_quads = []
        self.core_grid = {}
        for i in range(len(self.xy)-1):
            quad = self.quad(i, inset=.08)
            self.core_quads.append(quad)
            x0, x1 = min(p[0] for p in quad), max(p[0] for p in quad)
            y0, y1 = min(p[1] for p in quad), max(p[1] for p in quad)
            for iy in range(math.floor(y0/4), math.floor(y1/4)+1):
                for ix in range(math.floor(x0/4), math.floor(x1/4)+1):
                    self.core_grid.setdefault((ix, iy), []).append(i)
        self.threshold_polygon = self.threshold_points_2d()

    def width(self, station):
        c = self.cfg
        normal = c['width_base_m']+c['width_wave_m']*math.sin(station/c['width_wave_length_m'])
        begin, end = c['woods_stations_m']
        blend = c['width_blend_m']
        wooded = smooth(begin-blend, begin, station)*(1-smooth(end, end+blend, station))
        width = (1-wooded)*normal+wooded*c['woods_width_m']
        return (1-smooth(.4, 2.5, station))*2.1+smooth(.4, 2.5, station)*width

    def gate_y(self, x):
        a, b = self.garden[4], self.garden[0]
        return a[1]+(b[1]-a[1])*(x-a[0])/(b[0]-a[0])

    def offset(self, index, lateral):
        x, y = self.xy[index]
        dx, dy = self.tangent[index]
        x0, x1, y0, y1 = self.surface.extent
        return (max(x0, min(x1, x-dy*lateral)), max(y0, min(y1, y+dx*lateral)))

    def quad(self, index, inset=0):
        a = self.width(self.station[index])/2-inset
        b = self.width(self.station[index+1])/2-inset
        return [self.offset(index, -a), self.offset(index+1, -b),
                self.offset(index+1, b), self.offset(index, a)]

    def closest(self, x, y):
        _, middle, _ = self.kd.find(Vector((x, y, 0)))
        best = None
        for i in range(max(0, middle-3), min(len(self.xy)-1, middle+3)):
            ax, ay = self.xy[i]
            bx, by = self.xy[i+1]
            dx, dy = bx-ax, by-ay
            den = dx*dx+dy*dy
            raw = ((x-ax)*dx+(y-ay)*dy)/den
            t = max(0, min(1, raw))
            cx, cy = ax+t*dx, ay+t*dy
            distance = math.hypot(x-cx, y-cy)
            if best is None or distance < best[0]:
                length = math.sqrt(den)
                lateral = (-(dy/length)*(x-cx)+(dx/length)*(y-cy))
                s = self.station[i]+t*(self.station[i+1]-self.station[i])
                z = self.z[i]+t*(self.z[i+1]-self.z[i])
                outside = (i == 0 and raw < 0) or (i == len(self.xy)-2 and raw > 1)
                best = (distance, s, lateral, z, i, t, outside)
        return best

    def threshold_top(self, x, y):
        t = self.threshold
        end = self.gate_y(x)+t['finish_inside_gate_m']
        return t['top_z']+(t['slab_top_z']-t['top_z'])*max(0, min(1, (y-end)/(t['slab_end_y']-end)))

    def threshold_points_2d(self):
        x0, x1 = self.threshold['x_span']
        y = self.threshold['slab_end_y']
        i = self.threshold_end
        return [(x0, y), (x1, y), self.offset(i, self.width(self.station[i])/2),
                self.offset(i, -self.width(self.station[i])/2)]

    def grade(self, x, y):
        original = sample(self.surface, x, y)[0]
        d, s, lateral, centre_z, i, t, outside = self.closest(x, y)
        half = self.width(s)/2
        value = original
        if not outside and d <= half+self.cfg['grading_beyond_edge_m']:
            crown = self.cfg['crown']*smooth(.5, 3, s)*smooth(0, 3, self.length-s)
            edge_z = centre_z-crown*min(abs(lateral), half)
            w = 1-smooth(half, half+self.cfg['grading_beyond_edge_m'], d)
            value = original+(edge_z-original)*w
        x0, x1 = self.threshold['x_span']
        y0 = self.gate_y(x)-.45
        y1 = self.threshold['slab_end_y']
        if x0-1 <= x <= x1+1 and y0 <= y <= y1+.12:
            wx = 1-smooth(0, 1, max(x0-x, 0, x-x1))
            wy = smooth(y0, y0+.15, y)*(1-smooth(y1, y1+.12, y))
            top = self.threshold_top(x, y)-self.cfg['gravel_thickness_m']
            value = value+(top-value)*wx*wy
        change = abs(value-original)
        assert change <= self.cfg['maximum_grading_m']+1e-5, ('Grading boundary', x, y, change)
        return value

    def point_at(self, station):
        i = min(len(self.xy)-2, max(0, bisect.bisect_right(self.station, station)-1))
        t = (station-self.station[i])/(self.station[i+1]-self.station[i])
        return (self.xy[i][0]+t*(self.xy[i+1][0]-self.xy[i][0]),
                self.xy[i][1]+t*(self.xy[i+1][1]-self.xy[i][1]))

    def summary(self):
        grades = [abs(self.z[i]-self.z[i-1])/(self.station[i]-self.station[i-1])
                  for i in range(1, len(self.z))]
        return {'controls_xy': self.cfg['controls_xy'], 'samples': len(self.xy),
                'maximum_sample_interval_m': max(b-a for a, b in zip(self.station, self.station[1:])),
                'length_xy_m': self.length,
                'length_3d_m': sum(math.hypot(self.station[i]-self.station[i-1], self.z[i]-self.z[i-1])
                                   for i in range(1, len(self.z))),
                'maximum_longitudinal_grade': max(grades),
                'maximum_profile_adjustment_m': self.profile_adjustment,
                'exit_ground_xyz': [*self.xy[-1], self.raw_z[-1]],
                'exit_gravel_xyz': [*self.xy[-1], self.z[-1]+self.cfg['gravel_thickness_m']],
                'boundary': 'V06_TERRAIN_FAR north outer edge, Y=138.25',
                'threshold_short_bevel_disclosed': True}


def make_crest(existing, descriptors, surface, cfg):
    c = cfg['crest']
    kd = KDTree(len(existing))
    for i, row in enumerate(existing):
        kd.insert(Vector((*row['position'][:2], 0)), i)
    kd.balance()
    rr = random.Random(cfg['seed'])
    candidates = []
    for j in range(*c['grid_j']):
        for i in range(*c['grid_i']):
            x = (i+rr.random())*c['grid_m']
            y = (j+rr.random())*c['grid_m']
            if inside_polygon(x, y, c['polygon']):
                candidates.append((rr.random(), x, y, i, j))
    accepted = []
    for priority, x, y, i, j in sorted(candidates):
        z, n, face = sample(surface, x, y)
        if n.z < math.cos(math.radians(c['max_slope_deg'])):
            continue
        if kd.find(Vector((x, y, 0)))[2] < c['existing_root_clearance_m']:
            continue
        if any(math.hypot(x-r['position'][0], y-r['position'][1]) < c['new_root_clearance_m'] for r in accepted):
            continue
        if any(((x-a)/rx)**2+((y-b)/ry)**2 < 1 for a, b, rx, ry in c['glades']):
            continue
        accepted.append({'id': f'V07_CREST:{i}:{j}', 'position': [f32(x), f32(y), z],
                         'source': 'deterministic-compressed-world-v07-crest', 'support_face': face})
        if len(accepted) == cfg['counts']['crest']:
            break
    assert len(accepted) == 144, len(accepted)
    abies = set(r['id'] for r in sorted(accepted, key=lambda r: order_key(cfg['seed'], 'crest-species', r['id']))[:c['abies_count']])
    for row in accepted:
        proto = 1 if row['id'] in abies else 3
        rr = rng(cfg['seed'], 'crest-form', row['id'])
        height = rr.uniform(*c['height_m'])
        sz = height/descriptors[proto]['height']
        width = rr.uniform(1.2, 1.45) if proto == 1 else rr.uniform(1.35, 1.5)
        row.update(prototype=proto, scale=[f32(sz*width), f32(sz*width), f32(sz)],
                   rotation=[0., 0., f32(rr.random()*math.tau)])
        row['position'][2] = f32(sample(surface, *row['position'][:2])[0]
                                 -descriptors[proto]['bounds'][2][0]*row['scale'][2]-.006)
    return accepted


def select_half(records, cfg):
    c = cfg['forest']
    selected = set(c['xy_overrides'])
    eligible = [r for r in records if r['prototype'] != c['legacy_prototype'] and r['id'] not in selected]
    assert len(records) == cfg['counts']['total']
    groups = collections.defaultdict(list)
    sectors = collections.defaultdict(list)
    cx, cy = c['selection_center']
    for row in eligible:
        x, y = row['position'][:2]
        angle = math.atan2(y-cy, x-cx) % math.tau
        sector = min(c['sectors']-1, int(angle/math.tau*c['sectors']))
        radius = math.hypot(x-cx, y-cy)
        band = sum(radius >= b for b in c['distance_bands_m'])
        groups[(sector, band)].append(row)
        sectors[sector].append(row)
    for sector, rows in sorted(sectors.items()):
        selected.add(min(rows, key=lambda r: order_key(cfg['seed'], 'sector-reservation', sector, r['id']))['id'])
    groups = {key: [r for r in rows if r['id'] not in selected] for key, rows in groups.items()}
    left = cfg['counts']['half_size']-len(selected)
    total = sum(map(len, groups.values()))
    quotas = {k: math.floor(left*len(rows)/total) for k, rows in groups.items()}
    remainders = sorted(groups, key=lambda k: (-(left*len(groups[k])/total-quotas[k]), order_key(cfg['seed'], 'quota', *k)))
    for k in remainders[:left-sum(quotas.values())]:
        quotas[k] += 1
    for key, rows in sorted(groups.items()):
        chosen = sorted(rows, key=lambda r: order_key(cfg['seed'], 'half-size', r['id']))[:quotas[key]]
        selected.update(r['id'] for r in chosen)
    assert len(selected) == 649
    assert all(r['prototype'] != 4 for r in records if r['id'] in selected)
    return selected, {str(k): quotas[k] for k in sorted(quotas)}


def prepare(scene, P):
    cfg = P['forest_trail_v07']
    assert cfg['seed'] == 13707
    original = mapped_surface(scene)
    route = Route(original, P)
    descriptors = tree_descriptors()
    existing = baseline_forest(scene)
    crest = make_crest(existing, descriptors, original, cfg)
    records = existing+crest
    selected, quotas = select_half(records, cfg)
    kd = KDTree(len(records))
    for i, row in enumerate(records):
        kd.insert(Vector((*row['position'][:2], 0)), i)
    kd.balance()
    swap_candidates = []
    f = cfg['forest']
    for row in records:
        if row['id'] in selected or row['prototype'] not in [2, 3] or row['source'] != 'saved-post-compression-v06':
            continue
        x, y = row['position'][:2]
        if route.closest(x, y)[0] < f['swap_route_clearance_m']:
            continue
        neighbours = len(kd.find_range(Vector((x, y, 0)), f['edge_radius_m']))-1
        if neighbours <= f['edge_max_other_roots']:
            swap_candidates.append(row['id'])
    swaps = set(sorted(swap_candidates, key=lambda ident: order_key(cfg['seed'], 'fuller-edge', ident))[:f['maximum_swaps']])
    return {'cfg': cfg, 'original': original, 'route': route, 'descriptors': descriptors,
            'existing': existing, 'crest': crest, 'records': records, 'selected': selected,
            'quotas': quotas, 'swaps': swaps}


def make_review_cameras(scene, P, prepared, surface=None):
    cfg = prepared['cfg']
    route = prepared['route']
    surface = surface or prepared['original']
    parent = owned_collection('V07_ROOT', scene.collection)
    col = owned_collection('V07_CAMERAS', parent)
    c = cfg['cameras']
    poses = {}
    for key in ['overview', 'gate']:
        row = c[key]
        location = list(row['location'])
        if row.get('ground_relative'):
            location[2] += sample(surface, *location[:2])[0]
        poses['V07_CAM_'+key.upper()] = dict(row, location=location)
    walk = c['walking']
    x, y = route.point_at(walk['station_m'])
    tx, ty = route.point_at(walk['station_m']+walk['lookahead_m'])
    poses['V07_CAM_WALKING'] = {'location': [x, y, sample(surface, x, y)[0]+walk['eye_m']],
                               'target': [tx, ty, sample(surface, tx, ty)[0]+1.1], 'lens': walk['lens']}
    age = c['age']
    source = next(r for r in prepared['records'] if r['id'] == age['reserved_id'])
    neighbours = [r for r in prepared['existing'] if r['id'] not in prepared['selected'] and r['prototype'] != 4
                  and age['neighbour_range_m'][0] <= math.dist(source['position'][:2], r['position'][:2]) <= age['neighbour_range_m'][1]]
    neighbour = min(neighbours, key=lambda r: (math.dist(source['position'][:2], r['position'][:2]), r['id']))
    target = [(source['position'][k]+neighbour['position'][k])/2 for k in range(3)]
    target[2] += .38*prepared['descriptors'][source['prototype']]['height']*source['scale'][2]
    ex, ey = age['eye_xy']
    poses['V07_CAM_AGE'] = {'location': [ex, ey, sample(prepared['original'], ex, ey)[0]+age['eye_height_m']],
                           'target': target, 'lens': age['lens'], 'pair_ids': [source['id'], neighbour['id']]}
    for name, row in poses.items():
        ob = bpy.data.objects.get(name)
        if ob is None:
            data = bpy.data.cameras.new(name+'_DATA')
            data['v07_owned'] = True
            ob = owned_object(name, data, col)
        assert ob.get('v07_owned')
        ob.location = row['location']
        ob.rotation_euler = (Vector(row['target'])-ob.location).to_track_quat('-Z', 'Y').to_euler()
        ob.data.lens = row['lens']
        ob.data.sensor_width = 36
        ob.data.sensor_fit = 'HORIZONTAL'
        ob.data.shift_x, ob.data.shift_y = row.get('shift', [0, 0])
        ob.data.clip_end = 1000
        ob.data.dof.use_dof = False
        ob['v07_pose'] = json.dumps(row, sort_keys=True)
    return poses


def polygon_intersects(a, b, epsilon=1e-9):
    """Convex projected footprints; touching counts as clearance intersection."""
    if (max(p[0] for p in a) < min(p[0] for p in b)-epsilon
            or min(p[0] for p in a) > max(p[0] for p in b)+epsilon
            or max(p[1] for p in a) < min(p[1] for p in b)-epsilon
            or min(p[1] for p in a) > max(p[1] for p in b)+epsilon):
        return False
    for poly in [a, b]:
        for p, q in zip(poly, poly[1:]+poly[:1]):
            nx, ny = -(q[1]-p[1]), q[0]-p[0]
            if abs(nx)+abs(ny) < 1e-12:
                continue
            aa = [nx*x+ny*y for x, y in a]
            bb = [nx*x+ny*y for x, y in b]
            if max(aa) < min(bb)-epsilon or max(bb) < min(aa)-epsilon:
                return False
    return True


def nearby_segments(route, polygon, extra=0):
    x0, x1 = min(p[0] for p in polygon)-extra, max(p[0] for p in polygon)+extra
    y0, y1 = min(p[1] for p in polygon)-extra, max(p[1] for p in polygon)+extra
    ids = set()
    for iy in range(math.floor(y0/4), math.floor(y1/4)+1):
        for ix in range(math.floor(x0/4), math.floor(x1/4)+1):
            ids.update(route.core_grid.get((ix, iy), ()))
    return ids


def footprint_hits_route(route, hull, extra=0):
    for i in nearby_segments(route, hull, abs(extra)+.1):
        if polygon_intersects(hull, route.quad(i, inset=-extra)):
            return True
    if extra > 0:
        xl, xr = route.threshold['x_span']
        low = min(route.gate_y(xl), route.gate_y(xr))-.45
        high = route.threshold['slab_end_y']+.12
        threshold = [(xl-extra, low), (xr+extra, low),
                     (xr+extra, high), (xl-extra, high)]
    else:
        threshold = route.threshold_polygon
    return polygon_intersects(hull, threshold)


def footprint_hits_core(route, hull):
    return (any(polygon_intersects(hull, route.core_quads[i]) for i in nearby_segments(route, hull, .1))
            or polygon_intersects(hull, route.threshold_polygon))


def barycentric_2d(point, triangle):
    x, y = point
    a, b, c = triangle
    den = (b[0]-a[0])*(c[1]-a[1])-(c[0]-a[0])*(b[1]-a[1])
    assert abs(den) > 1e-15, triangle
    v = ((x-a[0])*(c[1]-a[1])-(c[0]-a[0])*(y-a[1]))/den
    w = ((b[0]-a[0])*(y-a[1])-(x-a[0])*(b[1]-a[1]))/den
    return 1-v-w, v, w


def route_lattice(route):
    coords = []
    edges = []
    rows = []
    for i, station in enumerate(route.station):
        half = route.width(station)/2
        offsets = [-half-1, -half-.8, -half-.6, -half-.4, -half-.2,
                   -half, -half*.5, 0., half*.5, half,
                   half+.2, half+.4, half+.6, half+.8, half+1]
        row = []
        for off in offsets:
            row.append(len(coords))
            coords.append(route.offset(i, off))
        rows.append(row)
        edges.extend(zip(row, row[1:]))
        if i:
            edges.extend(zip(rows[i-1], row))
    t = route.threshold
    xl, xr = t['x_span']
    extra_rows = []
    # Connector lines and a 0.12 m support blend underneath the retained last slab.
    for mode in ['north_support', 'slab', 'bevel', 'gate']:
        row = []
        for x in [xl-1, xl-.8, xl-.6, xl-.4, xl-.2, xl, (xl+xr)/2,
                  xr, xr+.2, xr+.4, xr+.6, xr+.8, xr+1]:
            if mode == 'north_support':
                y = t['slab_end_y']+.12
            elif mode == 'slab':
                y = t['slab_end_y']
            elif mode == 'bevel':
                y = route.gate_y(x)+t['finish_inside_gate_m']
            else:
                y = route.gate_y(x)
            row.append(len(coords))
            coords.append((x, y))
        extra_rows.append(row)
        edges.extend(zip(row, row[1:]))
        if len(extra_rows) > 1:
            edges.extend(zip(extra_rows[-2], row))
    # Link the connector lattice to the route's first transverse row.
    for k in [0, 5, 6, 7, 12]:
        target = [0, 5, 7, 9, 14][[0, 5, 6, 7, 12].index(k)]
        edges.append((extra_rows[-1][k], rows[0][target]))
    return coords, [tuple(edge) for edge in edges]


def new_gravel_material(ROOT, cfg):
    name = 'MAT_V07_GRAVEL'
    material = bpy.data.materials.get(name)
    if material is None:
        material = bpy.data.materials.new(name)
        material['v07_owned'] = True
    assert material.get('v07_owned')
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    output = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Metallic'].default_value = 0
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    uv = nodes.new('ShaderNodeTexCoord')
    offset = nodes.new('ShaderNodeVectorMath')
    offset.operation = 'ADD'
    offset.inputs[1].default_value = (.317, .419, 0)
    links.new(uv.outputs['UV'], offset.inputs[0])
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = .16
    noise.inputs['Detail'].default_value = 2
    links.new(uv.outputs['Object'], noise.inputs['Vector'])
    mixed = {}
    for role, rel in cfg['material']['maps'].items():
        path = Path(ROOT)/rel
        image_name = 'V07_GRAVEL_'+role
        image = bpy.data.images.get(image_name)
        if image is None:
            image = bpy.data.images.load(str(path), check_existing=False)
            image.name = image_name
            image['v07_owned'] = True
        assert image.get('v07_owned')
        image.colorspace_settings.name = 'sRGB' if role == 'diffuse' else 'Non-Color'
        assert list(image.size) == [2048, 2048]
        image.pack()
        if bpy.data.filepath:
            image.filepath = '//'+__import__('os').path.relpath(path, Path(bpy.data.filepath).parent)
        else:
            image.filepath = '//../'+rel
        textures = [nodes.new('ShaderNodeTexImage'), nodes.new('ShaderNodeTexImage')]
        for texture in textures:
            texture.image = image
            texture.extension = 'REPEAT'
        links.new(uv.outputs['UV'], textures[0].inputs['Vector'])
        links.new(offset.outputs['Vector'], textures[1].inputs['Vector'])
        mix = nodes.new('ShaderNodeMixRGB')
        mix.blend_type = 'MIX'
        links.new(noise.outputs['Fac'], mix.inputs[0])
        links.new(textures[0].outputs['Color'], mix.inputs[1])
        links.new(textures[1].outputs['Color'], mix.inputs[2])
        mixed[role] = mix.outputs[0]
    hue = nodes.new('ShaderNodeHueSaturation')
    hue.inputs['Saturation'].default_value = cfg['material']['saturation']
    hue.inputs['Value'].default_value = cfg['material']['value']
    links.new(mixed['diffuse'], hue.inputs['Color'])
    links.new(hue.outputs['Color'], bsdf.inputs['Base Color'])
    rough = nodes.new('ShaderNodeMapRange')
    rough.inputs['To Min'].default_value, rough.inputs['To Max'].default_value = cfg['material']['roughness']
    links.new(mixed['roughness'], rough.inputs['Value'])
    links.new(rough.outputs['Result'], bsdf.inputs['Roughness'])
    normal = nodes.new('ShaderNodeNormalMap')
    normal.inputs['Strength'].default_value = cfg['material']['normal_strength']
    normal.uv_map = 'UVMap'
    links.new(mixed['NormalGL'], normal.inputs['Color'])
    links.new(normal.outputs['Normal'], bsdf.inputs['Normal'])
    material.diffuse_color = (.19, .16, .12, 1)
    material.roughness = .86
    return material


def shoulder_material():
    name = 'MAT_V07_SHOULDER'
    material = bpy.data.materials.get(name)
    if material is None:
        material = bpy.data.materials['MAT_V06_MEADOW_BASE'].copy()
        material.name = name
        material['v07_owned'] = True
        for node in material.node_tree.nodes:
            if node.type == 'HUE_SAT':
                node.inputs['Saturation'].default_value = .58
                node.inputs['Value'].default_value = .60
    return material


def terrain_derivative(source, name, route, lattice, parent):
    """Intersect only corridor triangles with a shared constrained lattice."""
    src = source.data
    shell = src.attributes.get('V05_shell')
    selected = []
    for face in src.polygons:
        if shell and shell.data[face.index].value:
            continue
        polygon = [tuple(src.vertices[k].co[:2]) for k in face.vertices]
        if footprint_hits_route(route, polygon, extra=1.05):
            selected.append(face.index)
    assert selected, source.name
    original_ids = sorted({i for fi in selected for i in src.polygons[fi].vertices})
    to_local = {index: i for i, index in enumerate(original_ids)}
    coords = [Vector(src.vertices[i].co[:2]) for i in original_ids]
    input_faces = []
    for fi in selected:
        indices = [to_local[k] for k in src.polygons[fi].vertices]
        a, b, c = [coords[k] for k in indices]
        if (b-a).cross(c-a) < 0:
            indices.reverse()
        input_faces.append(indices)
    grid_xy, grid_edges = lattice
    offset = len(coords)
    coords.extend(Vector(p) for p in grid_xy)
    edges = [(a+offset, b+offset) for a, b in grid_edges if grid_xy[a] != grid_xy[b]]
    result = delaunay_2d_cdt(coords, edges, input_faces, 1, 1e-7, True)
    out_xy, out_edges, out_faces, orig_vertices, orig_edges, orig_faces = result
    vertices = [tuple(v.co) for v in src.vertices]
    changed = 0
    max_change = 0.
    for i in original_ids:
        x, y, z = vertices[i]
        new_z = route.grade(x, y)
        if abs(new_z-z) > 1e-7:
            vertices[i] = (x, y, f32(new_z))
            max_change = max(max_change, abs(new_z-z))
            changed += 1
    mapped = {}
    for i, point in enumerate(out_xy):
        existing = [k for k in orig_vertices[i] if k < len(original_ids)]
        if existing:
            mapped[i] = original_ids[existing[0]]
        else:
            x, y = point
            # CDT contains lattice points outside this terrain component; only
            # vertices used by an inside-original-face triangle are kept below.
            mapped[i] = None
    kept_output = [j for j, ids in enumerate(orig_faces) if ids]
    used = {k for j in kept_output for k in out_faces[j]}
    for k in sorted(used):
        if mapped[k] is None:
            x, y = out_xy[k]
            mapped[k] = len(vertices)
            vertices.append((x, y, f32(route.grade(x, y))))
    faces = []
    provenance = []
    selected_set = set(selected)
    for face in src.polygons:
        if face.index not in selected_set:
            faces.append(tuple(face.vertices))
            provenance.append(face.index)
    for j in kept_output:
        ids = out_faces[j]
        if len(ids) != 3:
            raise AssertionError(('Non-triangle CDT output', name, len(ids)))
        face = tuple(mapped[k] for k in ids)
        a, b, c = [Vector(vertices[k]) for k in face]
        if abs((b-a).cross(c-a).z) < 1e-10:
            continue
        if (b-a).cross(c-a).z < 0:
            face = (face[0], face[2], face[1])
        faces.append(face)
        provenance.append(selected[orig_faces[j][0]])
    # Split retained north shell triangles at every newly introduced top-edge
    # point, so the finite exit is geometrically and topologically supported.
    ymax = route.surface.extent[3]
    boundary_points = [i for i in range(len(src.vertices), len(vertices)) if abs(vertices[i][1]-ymax) < 2e-5]
    if boundary_points and shell:
        new_faces, new_provenance = [], []
        for face, source_id in zip(faces, provenance):
            if not shell.data[source_id].value:
                new_faces.append(face); new_provenance.append(source_id)
                continue
            polygon = []
            for a, b in zip(face, face[1:]+face[:1]):
                polygon.append(a)
                va, vb = vertices[a], vertices[b]
                if (abs(va[1]-ymax) < 2e-5 and abs(vb[1]-ymax) < 2e-5
                        and abs(va[0]-vb[0]) > 1e-8 and min(va[2], vb[2]) > -40):
                    between = [k for k in boundary_points if min(va[0], vb[0])+1e-6 < vertices[k][0] < max(va[0], vb[0])-1e-6]
                    polygon.extend(sorted(between, key=lambda k: (vertices[k][0]-va[0])/(vb[0]-va[0])))
            if len(polygon) == 3:
                new_faces.append(face); new_provenance.append(source_id)
            else:
                vectors = [Vector(vertices[k]) for k in polygon]
                lookup = {tuple(v): k for v, k in zip(vectors, polygon)}
                for tri in tessellate_polygon([vectors]):
                    # Blender 5.3 returns flattened input indices; earlier
                    # Blender releases returned the input vectors themselves.
                    inds = (tuple(polygon[k] for k in tri) if isinstance(tri[0], int)
                            else tuple(lookup[tuple(v)] for v in tri))
                    tv = [Vector(vertices[k]) for k in inds]
                    if (tv[1]-tv[0]).cross(tv[2]-tv[0]).dot(src.polygons[source_id].normal) < 0:
                        inds = (inds[0], inds[2], inds[1])
                    new_faces.append(inds); new_provenance.append(source_id)
        faces, provenance = new_faces, new_provenance
    materials = list(src.materials)+[shoulder_material()]
    me = owned_mesh(name+'_MESH', vertices, faces, materials)
    at = me.attributes.get('V05_shell') or me.attributes.new('V05_shell', 'BOOLEAN', 'FACE')
    uv = me.uv_layers.get('UVMap') or me.uv_layers.new(name='UVMap')
    source_uv = src.uv_layers.active
    source_normals = [n.vector.copy() for n in src.corner_normals]
    normals = []
    graded_faces = 0
    for face, fi in zip(me.polygons, provenance):
        original = src.polygons[fi]
        is_shell = bool(shell and shell.data[fi].value)
        at.data[face.index].value = is_shell
        face.material_index = original.material_index
        face.use_smooth = original.use_smooth
        centroid = face.center
        d, station, lateral, z, i, t, outside = route.closest(centroid.x, centroid.y)
        if not is_shell and not outside and route.width(station)/2 < d < route.width(station)/2+.85:
            face.material_index = len(materials)-1
        if not is_shell and abs(route.grade(centroid.x, centroid.y)-sample(route.surface, centroid.x, centroid.y)[0]) > 1e-6:
            graded_faces += 1
        original_vertices = list(original.vertices)
        original_loops = list(original.loop_indices)
        drop = max(range(3), key=lambda k: abs(original.normal[k]))
        axes = [k for k in range(3) if k != drop]
        triangle = [tuple(src.vertices[k].co[a] for a in axes) for k in original_vertices]
        for li in face.loop_indices:
            index = me.loops[li].vertex_index
            point = me.vertices[index].co
            if index in original_vertices:
                old_li = original_loops[original_vertices.index(index)]
                uv.data[li].uv = source_uv.data[old_li].uv
                normal = source_normals[old_li]
            else:
                weights = barycentric_2d(tuple(point[a] for a in axes), triangle)
                uv.data[li].uv = sum((source_uv.data[l].uv*w for l, w in zip(original_loops, weights)), Vector((0, 0)))
                normal = sum((source_normals[l]*w for l, w in zip(original_loops, weights)), Vector((0, 0, 0))).normalized()
            if not is_shell:
                x, y = point[:2]
                if abs(route.grade(x, y)-sample(route.surface, x, y)[0]) > 1e-6:
                    normal = me.vertices[index].normal.copy()
            normals.append(tuple(normal))
    # Blender 5.3 free normals preserve the exact float vectors. The legacy
    # tangent-space INT16_2D encoding changes unchanged exterior corners.
    old_custom = me.attributes.get('custom_normal')
    if old_custom is not None:
        me.attributes.remove(old_custom)
    custom = me.attributes.new('custom_normal', 'FLOAT_VECTOR', 'CORNER')
    custom.data.foreach_set('vector', array.array('f', (c for n in normals for c in n)))
    me.update()
    me['v07_source_mesh'] = src.name
    me['v07_provenance'] = json.dumps(provenance)
    ob = owned_object(name, me, parent)
    source.hide_render = True
    source.hide_viewport = True
    return ob, {'source': source.name, 'selected_original_faces': len(selected),
                'original_vertices_changed': changed, 'maximum_original_vertex_change_m': max_change,
                'vertices': len(me.vertices), 'faces': len(me.polygons), 'graded_faces': graded_faces}


def build_trail(scene, prepared, ROOT):
    route, cfg = prepared['route'], prepared['cfg']
    col = owned_collection('V07_TERRAIN', owned_collection('V07_ROOT', scene.collection))
    lattice = route_lattice(route)
    terrain_stats = []
    for before, after in [('V06_TERRAIN_NEAR', 'V07_TERRAIN_NEAR'), ('V06_TERRAIN_FAR', 'V07_TERRAIN_FAR')]:
        ob, stats = terrain_derivative(scene.objects[before], after, route, lattice, col)
        terrain_stats.append(stats)
    surface = mapped_surface(scene, final=True)
    vertices, faces = [], []
    lookup = {}
    start_station = route.station[route.threshold_end]
    for name in ['V07_TERRAIN_NEAR', 'V07_TERRAIN_FAR']:
        terrain = scene.objects[name].data
        shell = terrain.attributes['V05_shell']
        for face in terrain.polygons:
            if shell.data[face.index].value:
                continue
            p = face.center
            d, s, lateral, z, i, t, outside = route.closest(p.x, p.y)
            if outside or s < start_station-1e-5 or d > route.width(s)/2+1e-5:
                continue
            row = []
            for k in face.vertices:
                q = terrain.vertices[k].co
                key = tuple(round(v, 6) for v in q)
                if key not in lookup:
                    lookup[key] = len(vertices)
                    vertices.append((q.x, q.y, q.z+cfg['route']['gravel_thickness_m']))
                row.append(lookup[key])
            faces.append(tuple(row))
    assert len(faces) > 1000, len(faces)
    top_vertices, top_faces = len(vertices), len(faces)
    uses = collections.Counter()
    directed = {}
    for face in faces:
        for a, b in zip(face, face[1:]+face[:1]):
            key = tuple(sorted((a, b)))
            uses[key] += 1
            directed[key] = (a, b)
    assert max(uses.values()) == 2, 'Non-manifold top gravel sheet'
    vertices += [(x, y, z-cfg['route']['gravel_thickness_m']-.002) for x, y, z in vertices[:top_vertices]]
    faces += [tuple(k+top_vertices for k in reversed(face)) for face in faces[:top_faces]]
    for key, count in uses.items():
        if count == 1:
            a, b = directed[key]
            faces.append((b, a, a+top_vertices, b+top_vertices))
    material = new_gravel_material(ROOT, cfg)
    me = owned_mesh('V07_TRAIL_MESH', vertices, faces, [material])
    uv = me.uv_layers.get('UVMap') or me.uv_layers.new(name='UVMap')
    for face in me.polygons:
        face.use_smooth = face.index < top_faces
        for li in face.loop_indices:
            v = me.vertices[me.loops[li].vertex_index].co
            d, station, lateral, z, i, t, outside = route.closest(v.x, v.y)
            second = lateral if face.index < 2*top_faces else v.z
            uv.data[li].uv = (station/cfg['material']['physical_width_m'], second/cfg['material']['physical_width_m'])
    me['v07_top_vertices'] = top_vertices
    me['v07_top_faces'] = top_faces
    owned_object('V07_TRAIL', me, col)
    xl, xr = route.threshold['x_span']
    y = route.threshold['slab_end_y']
    finish = route.threshold['finish_inside_gate_m']
    i = route.threshold_end
    half = route.width(route.station[i])/2
    top = [(xl, y, .11), (xr, y, .11),
           (xl, route.gate_y(xl)+finish, 0), (xr, route.gate_y(xr)+finish, 0),
           (*route.offset(i, -half), 0), (*route.offset(i, half), 0)]
    bottom = [(x, y, z-.045) for x, y, z in top]
    faces = [(0, 2, 3), (0, 3, 1), (2, 4, 5), (2, 5, 3),
             (6, 7, 9), (6, 9, 8), (8, 9, 11), (8, 11, 10)]
    boundary = [0, 1, 3, 5, 4, 2]
    for a, b in zip(boundary, boundary[1:]+boundary[:1]):
        faces.append((a, b, b+6, a+6))
    threshold = owned_mesh('V07_GATE_TRANSITION_MESH', top+bottom, faces, [bpy.data.materials['MAT_CONCRETE']])
    owned_object('V07_GATE_TRANSITION', threshold, col)
    return surface, {'terrain': terrain_stats, 'route': route.summary(),
                     'trail_faces': len(me.polygons), 'trail_vertices': len(me.vertices),
                     'threshold_leaf_clearance_m': .005, 'threshold_top_z': 0.0}


def instance_group(name, collection, source_group='V06_FOREST_GN', masters=None, mask=False):
    group = bpy.data.node_groups.get(name)
    if group is None:
        group = bpy.data.node_groups[source_group].copy()
        group.name = name
        group['v07_owned'] = True
        if 'v06_owned' in group:
            del group['v06_owned']
    assert group.get('v07_owned'), name
    if masters is not None:
        for node in group.nodes:
            if node.bl_idname == 'GeometryNodeCollectionInfo':
                node.inputs['Collection'].default_value = masters
    if mask and not any(n.name == 'V07_REMOVE_POINTS' for n in group.nodes):
        source = next(n for n in group.nodes if n.bl_idname == 'NodeGroupInput')
        instance = next(n for n in group.nodes if n.bl_idname == 'GeometryNodeInstanceOnPoints')
        for link in list(instance.inputs['Points'].links):
            group.links.remove(link)
        delete = group.nodes.new('GeometryNodeDeleteGeometry')
        delete.name = 'V07_REMOVE_POINTS'
        delete.domain = 'POINT'
        attribute = group.nodes.new('GeometryNodeInputNamedAttribute')
        attribute.data_type = 'BOOLEAN'
        attribute.inputs['Name'].default_value = 'v07_remove'
        group.links.new(source.outputs['Geometry'], delete.inputs['Geometry'])
        group.links.new(attribute.outputs['Attribute'], delete.inputs['Selection'])
        group.links.new(delete.outputs['Geometry'], instance.inputs['Points'])
    assert not any(n.bl_idname == 'GeometryNodeRealizeInstances' for n in group.nodes)
    return group


def put_points(name, rows, col, group):
    me = owned_mesh(name+'_POINTS', [r['position'] for r in rows], [])
    for key, kind, source in [('prototype', 'INT', 'prototype'),
                              ('rotation', 'FLOAT_VECTOR', 'rotation'),
                              ('scale', 'FLOAT_VECTOR', 'scale'),
                              ('v07_half', 'BOOLEAN', 'half')]:
        attribute = me.attributes.get(key) or me.attributes.new(key, kind, 'POINT')
        if kind == 'BOOLEAN':
            for item, row in zip(attribute.data, rows):
                item.value = bool(row.get(source, False))
            continue
        width = 3 if kind == 'FLOAT_VECTOR' else 1
        values = array.array('f' if width == 3 else 'i')
        for row in rows:
            value = row.get(source, False)
            if width == 3:
                values.extend(value)
            else:
                values.append(int(value))
        attribute.data.foreach_set('vector' if width == 3 else 'value', values)
    ob = owned_object(name, me, col)
    modifier = next((m for m in ob.modifiers if m.type == 'NODES'), None)
    if modifier is None:
        modifier = ob.modifiers.new('Linked V07 instances', 'NODES')
    modifier.node_group = group
    ob['v07_instances'] = len(rows)
    return ob


def forest_masters():
    col = owned_collection('V07_MASTER_FOREST')
    for index in range(5):
        owned_object(f'V07_TREE_MASTER_{index}', bpy.data.objects[f'V06_TREE_MASTER_{index}'].data, col)
    return col


def seated_tree(row, prototype, scale, position_xy, descriptors, surface, embed):
    x, y = map(f32, position_xy)
    centre_z, normal, face = sample(surface, x, y)
    matrix = Euler(row['rotation']).to_matrix()
    bounds = descriptors[prototype]['root_bounds']
    points = [matrix@Vector((a*scale[0], b*scale[1], c*scale[2]))
              for a in bounds[0] for b in bounds[1] for c in bounds[2]]
    box = [x+min(p.x for p in points), x+max(p.x for p in points),
           y+min(p.y for p in points), y+max(p.y for p in points)]
    lo, hi, pieces = surface.range_over_box(box, (x, y, centre_z), (0, 0, 1))
    top = max(p.z for p in points)
    bottom = min(p.z for p in points)
    origin_z = f32(centre_z+lo-top-embed)
    support = {'terrain_face': face, 'ground_z': centre_z, 'root_box': box,
               'embed_m': embed, 'maximum_exposure_m': -embed,
               'maximum_burial_m': hi-lo+top-bottom+embed,
               'triangle_pieces': pieces, 'root_definition': 'bark-material base, first 0.04 local metres'}
    return [x, y, origin_z], support


def final_forest_records(prepared, surface):
    cfg = prepared['cfg']
    f = cfg['forest']
    final = []
    for baseline in prepared['records']:
        half = baseline['id'] in prepared['selected']
        prototype = baseline['prototype']
        scale = list(baseline['scale'])
        height_factor = width_factor = 1.
        if half:
            scale = [f32(v*f['half_factor']) for v in scale]
        elif prototype != f['legacy_prototype']:
            rr = rng(cfg['seed'], 'mature-variation', baseline['id'])
            x, y = baseline['position'][:2]
            variation = .6*rr.random()+.4*field(x, y)
            if baseline['id'] in prepared['swaps']:
                old_height = prepared['descriptors'][prototype]['height']*baseline['scale'][2]
                prototype = 0 if prototype == 2 else 1
                sz = old_height/prepared['descriptors'][prototype]['height']
                width = rr.uniform(1.2, 1.45)
                scale = [sz*width, sz*width, sz]
            kind = 'abies' if prototype in [0, 1] else 'mariana'
            h0, h1 = f[kind+'_height_factor']
            w0, w1 = f[kind+'_horizontal_factor']
            height_factor = h0+(h1-h0)*variation
            width_factor = w0+(w1-w0)*(.65*rr.random()+.35*field(y+19, x-7))
            scale = [f32(scale[0]*width_factor), f32(scale[1]*width_factor), f32(scale[2]*height_factor)]
        xy = f['xy_overrides'].get(baseline['id'], baseline['position'][:2])
        position, support = seated_tree(baseline, prototype, scale, xy, prepared['descriptors'], surface, f['embed_m'])
        final.append({'id': baseline['id'], 'baseline': baseline, 'half': half,
                      'factor': .5 if half else 1., 'legacy_young': baseline['prototype'] == 4,
                      'prototype': prototype, 'rotation': baseline['rotation'], 'scale': scale,
                      'position': position, 'support': support,
                      'mature_height_factor': height_factor, 'mature_horizontal_factor': width_factor,
                      'prototype_swapped': baseline['id'] in prepared['swaps'],
                      'xy_adjustment_m': math.dist(xy, baseline['position'][:2])})
    assert len(final) == 12977 and sum(r['half'] for r in final) == 649
    assert sum(r['legacy_young'] for r in final) == 378
    return final


def write_forest_registry(final):
    """Keep each native Text insertion bounded; one huge line is prohibitively slow."""
    text = bpy.data.texts.get('V07_FOREST_REGISTRY.json')
    if text is None:
        text = bpy.data.texts.new('V07_FOREST_REGISTRY.json')
        text['v07_owned'] = True
        text.use_fake_user = True
    text.clear()
    text.write('[\n')
    for index, row in enumerate(final):
        text.write(json.dumps(row, separators=(',', ':'))+(',' if index+1 < len(final) else '')+'\n')
    text.write(']\n')
    text.use_module = False
    return text


def apply_forest_layers(scene, prepared, surface, components):
    parent = owned_collection('V07_ROOT', scene.collection)
    masters = forest_masters()
    group = instance_group('V07_FOREST_GN', parent, masters=masters)
    final = final_forest_records(prepared, surface)
    if 'forest' in components:
        col = owned_collection('V07_FOREST', parent)
        grouped = collections.defaultdict(list)
        for row in final:
            if row['baseline']['source'] == 'saved-post-compression-v06':
                grouped[row['id'].rsplit(':', 1)[0]].append(row)
        for source, rows in sorted(grouped.items()):
            ob = put_points(source.replace('V06_', 'V07_', 1), rows, col, group)
            ob['v07_source_chunk'] = source
            original = scene.objects[source]
            original.hide_render = True
            original.hide_viewport = True
    if 'crest' in components:
        col = owned_collection('V07_CREST', parent)
        rows = [r for r in final if r['baseline']['source'] != 'saved-post-compression-v06']
        ob = put_points('V07_CREST_POINTS', rows, col, group)
        ob['v07_ids'] = json.dumps([r['id'] for r in rows])
    write_forest_registry(final)
    return final, {'total': len(final), 'half_size': sum(r['half'] for r in final),
                   'fraction': 649/12977, 'legacy_young': sum(r['legacy_young'] for r in final),
                   'crest': 144, 'prototype_swaps': len(prepared['swaps']),
                   'selection_sha256': digest(sorted(prepared['selected'])),
                   'swap_sha256': digest(sorted(prepared['swaps'])), 'quotas': prepared['quotas'],
                   'maximum_root_burial_m': max(r['support']['maximum_burial_m'] for r in final),
                   'maximum_exposure_m': max(r['support']['maximum_exposure_m'] for r in final),
                   'xy_overrides': prepared['cfg']['forest']['xy_overrides']}


_HULLS = {}


def grass_descriptors(kind):
    collection = bpy.data.collections['V06_MASTER_'+kind]
    result = []
    for ob in collection.objects:
        me = ob.data
        if me.name not in _HULLS:
            bm = bmesh.new()
            for vertex in me.vertices:
                bm.verts.new(vertex.co)
            hull = bmesh.ops.convex_hull(bm, input=list(bm.verts), use_existing_faces=False)
            hull_vertices = {v for item in hull['geom'] if isinstance(item, bmesh.types.BMFace) for v in item.verts}
            assert hull_vertices, me.name
            _HULLS[me.name] = sorted(tuple(v.co) for v in hull_vertices)
            bm.free()
        desc = json.loads(me['v06_descriptor'])
        desc['hull'] = _HULLS[me.name]
        desc['radius_3d'] = max(math.sqrt(sum(c*c for c in v)) for v in desc['hull'])
        result.append(desc)
    assert len(result) == (12 if kind == 'LAWN' else 24), (kind, len(result))
    return result


def projected_hull(points, rotation, position, scale=(1, 1, 1)):
    matrix = Euler(rotation).to_matrix()
    x, y = position[:2]
    projected = []
    for p in points:
        q = matrix@Vector(tuple(p[k]*scale[k] for k in range(3)))
        projected.append(Vector((x+q.x, y+q.y)))
    hull = convex_hull_2d(projected)
    return [tuple(projected[i]) if isinstance(i, int) else tuple(i) for i in hull]


def bounds_corners(bounds):
    return [(x, y, z) for x in bounds[0] for y in bounds[1] for z in bounds[2]]


def circle_intersects(hull, x, y, radius):
    if inside_polygon(x, y, hull):
        return True
    for a, b in zip(hull, hull[1:]+hull[:1]):
        dx, dy = b[0]-a[0], b[1]-a[1]
        den = dx*dx+dy*dy
        t = max(0, min(1, ((x-a[0])*dx+(y-a[1])*dy)/den)) if den else 0
        if math.hypot(x-a[0]-t*dx, y-a[1]-t*dy) <= radius:
            return True
    return False


def tree_kd(rows):
    kd = KDTree(len(rows))
    for i, row in enumerate(rows):
        kd.insert(Vector((*row['position'][:2], 0)), i)
    kd.balance()
    return kd


def mask_original_grass(scene, prepared, final_rows, surface=None):
    import numpy as np
    route = prepared['route']
    surface = surface or mapped_surface(scene, final=True)
    prepared['boundary_repair_grid'] = {}
    changed_trees = [r for r in final_rows if r['id'] in prepared['cfg']['forest']['xy_overrides']
                     or r['baseline']['source'] != 'saved-post-compression-v06']
    kd = tree_kd(changed_trees)
    parent = owned_collection('V07_MASKS', owned_collection('V07_ROOT', scene.collection))
    stats = {'chunks': [], 'removed_lawn': 0, 'removed_meadow': 0,
             'core': 0, 'graded_support': 0, 'new_root': 0, 'actual_support': 0,
             'boundary_repair_boxes': 0,
             'tested_full_footprints': 0, 'untouched_chunks': 0}
    for kind, step, group_source in [('LAWN', 8, 'V06_LAWN_GN'), ('MEADOW', 32, 'V06_MEADOW_GN')]:
        descriptors = grass_descriptors(kind)
        group = instance_group('V07_MASK_'+kind+'_GN', parent, source_group=group_source, mask=True)
        for original in sorted(scene.objects, key=lambda o: o.name):
            if not original.name.startswith('V06_'+kind+'_') or original.type != 'MESH' or 'prototype' not in original.data.attributes:
                continue
            source_mesh = original.data
            name = original.name.replace('V06_', 'V07_MASK_', 1)
            ix, iy = map(int, original.name.rsplit('_', 2)[1:])
            rect = [(ix*step, iy*step), ((ix+1)*step, iy*step),
                    ((ix+1)*step, (iy+1)*step), (ix*step, (iy+1)*step)]
            pilot = prepared.get('pilot_bounds')
            if pilot and ((ix+1)*step < pilot[0] or ix*step > pilot[1]
                          or (iy+1)*step < pilot[2] or iy*step > pilot[3]):
                continue
            near_tree = any(ix*step-2 <= r['position'][0] <= (ix+1)*step+2 and iy*step-2 <= r['position'][1] <= (iy+1)*step+2 for r in changed_trees)
            if not nearby_segments(route, rect, 3) and not near_tree:
                stats['untouched_chunks'] += 1
                obsolete = bpy.data.objects.get(name)
                if obsolete is not None:
                    assert obsolete.get('v07_owned')
                    data = obsolete.data
                    bpy.data.objects.remove(obsolete, do_unlink=True)
                    if data.users == 0:
                        assert data.get('v07_owned')
                        bpy.data.meshes.remove(data)
                original.hide_render = False
                original.hide_viewport = False
                continue
            count = len(source_mesh.vertices)
            positions = np.empty((count, 3), dtype=np.float32)
            rotations = np.empty((count, 3), dtype=np.float32)
            scales = np.empty((count, 3), dtype=np.float32)
            prototypes = np.empty(count, dtype=np.int32)
            source_mesh.vertices.foreach_get('co', positions.ravel())
            source_mesh.attributes['rotation'].data.foreach_get('vector', rotations.ravel())
            source_mesh.attributes['scale'].data.foreach_get('vector', scales.ravel())
            source_mesh.attributes['prototype'].data.foreach_get('value', prototypes)
            reasons = np.zeros(count, dtype=np.int32)
            for index in range(count):
                x, y, z = map(float, positions[index])
                descriptor = descriptors[int(prototypes[index])]
                radius = descriptor['radius_3d']*float(max(scales[index]))
                d, station, lateral, h, segment, t, outside = route.closest(x, y)
                close_route = d < route.width(station)/2+1.05+radius
                roots = kd.find_range(Vector((x, y, 0)), radius+.25)
                # Connector lies just before station zero; include it independently.
                connector = 5.7 < x < 10.1 and -9.3 < y < -8.0
                if not close_route and not roots and not connector:
                    continue
                rotation = tuple(map(float, rotations[index]))
                scale = tuple(map(float, scales[index]))
                hull = projected_hull(descriptor['hull'], rotation, (x, y, z), scale)
                stats['tested_full_footprints'] += 1
                reason = 0
                if footprint_hits_core(route, hull):
                    reason |= 1
                root_hull = projected_hull(bounds_corners(descriptor['root_bounds']), rotation, (x, y, z), scale)
                if footprint_hits_route(route, root_hull, extra=1.001):
                    reason |= 2
                if any(circle_intersects(hull, co.x, co.y, .25) for co, _, distance in roots):
                    reason |= 4
                matrix = Euler(rotation).to_matrix()
                root = [matrix@Vector(tuple(p[k]*scale[k] for k in range(3)))
                        for p in bounds_corners(descriptor['root_bounds'])]
                root_box = [x+min(p.x for p in root), x+max(p.x for p in root),
                            y+min(p.y for p in root), y+max(p.y for p in root)]
                if not reason:
                    normal = matrix@Vector((0, 0, 1))
                    lo, hi, pieces = surface.range_over_box(root_box, (x, y, z), normal)
                    exposure = max(0, descriptor['root_bounds'][2][1])*scale[2]/normal.z-lo
                    burial = hi-descriptor['root_bounds'][2][0]*scale[2]/normal.z
                    if exposure > .001 or burial > .020:
                        reason |= 8
                # Restore the root footprint of boundary patches that extend
                # outside the continuous shoulder strip, using smaller masters.
                if kind == 'MEADOW' and reason & (2 | 8) and d > route.width(station)/2+.9:
                    stats['boundary_repair_boxes'] += 1
                    for cy in range(math.floor(root_box[2]/4), math.floor(root_box[3]/4)+1):
                        for cx in range(math.floor(root_box[0]/4), math.floor(root_box[1]/4)+1):
                            prepared['boundary_repair_grid'].setdefault((cx, cy), []).append(root_box)
                reasons[index] = reason
            removed = int(np.count_nonzero(reasons))
            stats['removed_'+kind.lower()] += removed
            for flag, key in [(1, 'core'), (2, 'graded_support'), (4, 'new_root'), (8, 'actual_support')]:
                stats[key] += int(np.count_nonzero(reasons & flag))
            if not removed:
                stats['untouched_chunks'] += 1
                original.hide_render = False
                original.hide_viewport = False
                continue
            ob = bpy.data.objects.get(name)
            if ob is None:
                me = source_mesh.copy()
                me.name = name+'_POINTS'
                me['v07_owned'] = True
                if 'v06_owned' in me:
                    del me['v06_owned']
                ob = owned_object(name, me, parent)
                modifier = ob.modifiers.new('Footprint clearance, retained buffers', 'NODES')
                modifier.node_group = group
            else:
                assert ob.get('v07_owned') and ob.data.get('v07_owned')
                ob.hide_render = False
                ob.hide_viewport = False
                me = ob.data
            attribute = me.attributes.get('v07_remove') or me.attributes.new('v07_remove', 'BOOLEAN', 'POINT')
            attribute.data.foreach_set('value', (reasons != 0))
            reason_attribute = me.attributes.get('v07_reason') or me.attributes.new('v07_reason', 'INT', 'POINT')
            reason_attribute.data.foreach_set('value', reasons)
            ob['v07_source_chunk'] = original.name
            ob['v07_instances'] = count-removed
            ob['v07_removed'] = removed
            original.hide_render = True
            original.hide_viewport = True
            stats['chunks'].append({'source': original.name, 'copy': name, 'total': count, 'removed': removed,
                                    'mask_sha256': hashlib.sha256(reasons.tobytes()).hexdigest()})
    return stats


def hard_obstacles(scene):
    polygons = []
    posts = []
    trunks = []
    for ob in scene.objects:
        if ob.name == 'BASE_slab' or ob.name == 'BED_entry' or ob.name.startswith(('PORCH_paving', 'ENTRY_step_', 'PATH_slab', 'V05_PATH_slab_')):
            pts = [ob.matrix_world@Vector(v) for v in ob.bound_box]
            x0, x1 = min(p.x for p in pts)-.03, max(p.x for p in pts)+.03
            y0, y1 = min(p.y for p in pts)-.03, max(p.y for p in pts)+.03
            polygons.append([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
        if ob.name.startswith(('FENCE_post_proxy', 'V05_FENCE_POST_', 'V05_GATE_POST_')):
            posts.append((ob.location.x, ob.location.y))
        if ob.name in ['V04_ORCHARD', 'V04_YOUNG_00', 'V04_YOUNG_01', 'V04_YOUNG_02']:
            trunks.append((ob.location.x, ob.location.y))
    return polygons, posts, trunks


def build_shoulders(scene, prepared, surface, final_rows):
    route = prepared['route']
    cfg = prepared['cfg']
    descriptors = grass_descriptors('MEADOW')
    kd = tree_kd(final_rows)
    hard, posts, garden_trunks = hard_obstacles(scene)
    cells = set()
    for ix, iy in route.core_grid:
        cells.update((ix+dx, iy+dy) for dx in [-1, 0, 1] for dy in [-1, 0, 1])
    rows = []
    stats = {'root_rejected': 0, 'core_rejected': 0, 'root_refinements': 0,
             'support_rejected': 0, 'maximum_exposure_m': -1e20, 'maximum_burial_m': 0.,
             'triangle_pieces': 0, 'boundary_rejected': 0, 'boundary_repair_instances': 0}
    step = cfg['clearance']['shoulder_grid_m']
    def place(x, y, key, tier=1, repair=False):
        rr = rng(cfg['seed'], 'shoulder-form', key, tier)
        z, normal, face = sample(surface, x, y)
        if normal.z < math.cos(math.radians(68)):
            stats['support_rejected'] += 1
            return
        mixture = min(2.999999, 3*field(x, y))
        low = int(mixture)
        variant = low+int(rr.random() < mixture-low)
        proto = tier*4+variant
        if normal.z < math.cos(math.radians(60)):
            proto += 12
        descriptor = descriptors[proto]
        rotation = [f32(v) for v in pose(normal, rr.random()*math.tau)]
        hull = projected_hull(descriptor['hull'], rotation, (x, y, z))
        extent = surface.extent
        if any(not (extent[0] <= a <= extent[1] and extent[2] <= b <= extent[3]) for a, b in hull):
            stats['boundary_rejected'] += 1
            return
        if footprint_hits_core(route, hull) or any(polygon_intersects(hull, polygon) for polygon in hard):
            stats['core_rejected'] += 1
            return
        radius = descriptor['radius_3d']
        near = kd.find_range(Vector((x, y, 0)), radius+.25)
        if (any(circle_intersects(hull, co.x, co.y, .25) for co, _, _ in near)
                or any(circle_intersects(hull, a, b, .20) for a, b in posts)
                or any(circle_intersects(hull, a, b, .25) for a, b in garden_trunks)):
            stats['root_rejected'] += 1
            return
        matrix = Euler(rotation).to_matrix()
        root = [matrix@Vector(v) for v in bounds_corners(descriptor['root_bounds'])]
        box = [x+min(p.x for p in root), x+max(p.x for p in root),
               y+min(p.y for p in root), y+max(p.y for p in root)]
        x0, x1, y0, y1 = surface.extent
        if box[0] < x0 or box[1] > x1 or box[2] < y0 or box[3] > y1:
            stats['support_rejected'] += 1
            return
        lo, hi, pieces = surface.range_over_box(box, (x, y, z), normal)
        span = hi-lo
        headroom = max(0, descriptor['root_bounds'][2][1])/normal.z
        if span > .005 and tier < 2:
            stats['root_refinements'] += 1
            for dy in [-.03125, .03125]:
                for dx in [-.03125, .03125]:
                    place(f32(x+dx), f32(y+dy), key+f':{dx}:{dy}', 2, repair)
            return
        if span+headroom > .017:
            stats['support_rejected'] += 1
            return
        embed = .002+headroom
        position = [f32(x), f32(y), f32(z+lo-embed)]
        rows.append({'position': position, 'prototype': proto, 'rotation': rotation, 'scale': [1., 1., 1.]})
        stats['boundary_repair_instances'] += int(repair)
        stats['maximum_exposure_m'] = max(stats['maximum_exposure_m'], -.002)
        stats['maximum_burial_m'] = max(stats['maximum_burial_m'], span+embed)
        stats['triangle_pieces'] += pieces
    x0, x1, y0, y1 = surface.extent
    per_cell = round(4/step)
    for cell_x, cell_y in sorted(cells):
        pilot = prepared.get('pilot_bounds')
        if pilot and ((cell_x+1)*4 < pilot[0] or cell_x*4 > pilot[1]
                      or (cell_y+1)*4 < pilot[2] or cell_y*4 > pilot[3]):
            continue
        for j in range(per_cell):
            for i in range(per_cell):
                ix, iy = cell_x*per_cell+i, cell_y*per_cell+j
                rr = rng(cfg['seed'], 'shoulder-grid', ix, iy)
                x = f32((ix+.5+rr.uniform(-.35, .35))*step)
                y = f32((iy+.5+rr.uniform(-.35, .35))*step)
                if pilot and not (pilot[0] <= x <= pilot[1] and pilot[2] <= y <= pilot[3]):
                    continue
                if not x0+.1 < x < x1-.1 or not y0+.1 < y < y1-.1:
                    continue
                d, station, lateral, h, segment, t, outside = route.closest(x, y)
                half = route.width(station)/2
                in_strip = half-.08 < d < half+1.15
                repair = any(a <= x <= b and c <= y <= e for a, b, c, e in
                             prepared.get('boundary_repair_grid', {}).get((cell_x, cell_y), []))
                if outside or not (in_strip or repair):
                    continue
                if in_strip and rr.random() > smooth(-.08, .22, d-half):
                    continue
                place(x, y, f'{ix}:{iy}', repair=not in_strip)
    parent = owned_collection('V07_SHOULDERS', owned_collection('V07_ROOT', scene.collection))
    group = instance_group('V07_SHOULDERS_GN', parent, source_group='V06_MEADOW_GN')
    put_points('V07_SHOULDER_POINTS', rows, parent, group)
    stats['instances'] = len(rows)
    return stats


def apply_masks(scene, prepared, surface, final_rows):
    result = mask_original_grass(scene, prepared, final_rows, surface)
    result['shoulders'] = build_shoulders(scene, prepared, surface, final_rows)
    return result


def plain_material(name, color, roughness):
    material = bpy.data.materials.get(name)
    if material is None:
        material = bpy.data.materials.new(name)
        material['v07_owned'] = True
    assert material.get('v07_owned')
    material.use_nodes = True
    shader = next(n for n in material.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    shader.inputs['Base Color'].default_value = (*color, 1)
    shader.inputs['Roughness'].default_value = roughness
    material.diffuse_color = (*color, 1)
    material.roughness = roughness
    return material


def detail_masters(kind):
    col = owned_collection('V07_MASTER_'+kind)
    materials = ([plain_material('MAT_V07_STONE', (.17, .15, .12), .88)] if kind == 'STONES'
                 else [plain_material('MAT_V07_LITTER', (.040, .027, .011), .94)])
    for i in range(3):
        name = f'V07_{kind}_MASTER_{i}'
        if bpy.data.objects.get(name) is not None:
            continue
        if kind == 'STONES':
            bm = bmesh.new()
            bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1)
            rr = rng(13707, 'stone-master', i)
            verts = []
            for vertex in bm.verts:
                verts.append((vertex.co.x*rr.uniform(.85, 1.15),
                              vertex.co.y*(.70+.10*i)*rr.uniform(.9, 1.1),
                              vertex.co.z*(.48+.08*i)*rr.uniform(.9, 1.1)))
            bm.verts.ensure_lookup_table()
            ids = {v: k for k, v in enumerate(bm.verts)}
            faces = [tuple(ids[v] for v in f.verts) for f in bm.faces]
            bm.free()
            low = min(v[2] for v in verts)
            verts = [(x, y, z-low) for x, y, z in verts]
        else:
            verts = [(-.5, -.5, 0), (.5, -.12, .025), (.45, .20, .035),
                     (-.45, .5, .015), (-.1, .0, .09+.02*i)]
            faces = [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)]
        me = owned_mesh(name+'_MESH', verts, faces, materials)
        for face in me.polygons:
            face.use_smooth = kind == 'STONES'
        owned_object(name, me, col)
    return col


def build_details(scene, prepared, surface):
    route, cfg = prepared['route'], prepared['cfg']
    parent = owned_collection('V07_DETAILS', owned_collection('V07_ROOT', scene.collection))
    result = {}
    for kind, maximum in [('STONES', cfg['clearance']['maximum_stones']), ('LITTER', cfg['clearance']['maximum_litter'])]:
        masters = detail_masters(kind)
        group = instance_group('V07_'+kind+'_GN', parent, masters=masters)
        rows = []
        for attempt in range(maximum*8):
            rr = rng(cfg['seed'], 'detail', kind, attempt)
            station = rr.uniform(2, 28) if rr.random() < .6 else rr.uniform(65, 115)
            cx, cy = route.point_at(station)
            i = min(len(route.tangent)-1, bisect.bisect_left(route.station, station))
            dx, dy = route.tangent[i]
            side = -1 if rr.random() < .5 else 1
            lateral = side*(route.width(station)/2+rr.uniform(.08, .5))
            x, y = f32(cx-dy*lateral), f32(cy+dx*lateral)
            z, normal, face = sample(surface, x, y)
            rotation = [f32(v) for v in pose(normal, rr.random()*math.tau)]
            proto = rr.randrange(3)
            if kind == 'STONES':
                size = rr.uniform(.008, .023)
                scale = [f32(size*rr.uniform(.85, 1.2)), f32(size), f32(size*rr.uniform(.8, 1.1))]
            else:
                scale = [f32(rr.uniform(.025, .06)), f32(rr.uniform(.0008, .0018)), f32(rr.uniform(.002, .004))]
            master = bpy.data.objects[f'V07_{kind}_MASTER_{proto}'].data
            matrix = Euler(rotation).to_matrix()
            points = [matrix@Vector(tuple(v.co[k]*scale[k] for k in range(3))) for v in master.vertices]
            hull_2d = [Vector((x+p.x, y+p.y)) for p in points]
            hull = [tuple(hull_2d[k]) for k in convex_hull_2d(hull_2d)]
            if footprint_hits_core(route, hull):
                continue
            root = [p for p in points if p.z <= min(q.z for q in points)+.002]
            box = [x+min(p.x for p in root), x+max(p.x for p in root),
                   y+min(p.y for p in root), y+max(p.y for p in root)]
            lo, hi, pieces = surface.range_over_box(box, (x, y, z), (0, 0, 1))
            position = [x, y, f32(z+lo-max(p.z for p in root)-.001)]
            rows.append({'position': position, 'rotation': rotation, 'scale': scale, 'prototype': proto})
            if len(rows) == maximum:
                break
        put_points('V07_'+kind+'_POINTS', rows, parent, group)
        result[kind.lower()] = len(rows)
    return result


def configure_p0(scene):
    scene.camera = scene.objects['CAM_A_REFERENCE']
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.render.threads_mode = 'FIXED'
    scene.render.threads = 8
    scene.cycles.samples = 96
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = 'OPENIMAGEDENOISE'
    scene.cycles.denoising_use_gpu = False
    scene.cycles.denoising_prefilter = 'ACCURATE'
    scene.cycles.denoising_quality = 'HIGH'
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.adaptive_threshold = .01
    scene.cycles.adaptive_min_samples = 0
    scene.cycles.seed = 0
    scene.cycles.use_animated_seed = False
    scene.frame_set(0)
    scene.render.resolution_x = 1448
    scene.render.resolution_y = 1086
    scene.render.resolution_percentage = 100
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'None'
    scene.view_settings.exposure = 0
    scene.view_settings.gamma = 1


def apply_v07(scene, P, ROOT, *, components=None):
    """Apply owned components from immutable V06 inputs; explicit components force a fixed-point check."""
    before = random.getstate()
    assert not bpy.app.is_job_running('RENDER')
    prepared = prepare(scene, P)
    cfg = prepared['cfg']
    names = ['route', 'forest', 'crest', 'masks', 'details']
    requested = set(names if components is None else components)
    assert requested <= set(names), requested
    state = json.loads(scene.get('v07_component_state', '{}'))
    previous = json.loads(scene.get('forest_trail_v07_summary', '{}'))
    geometry_key = [cfg['route'], cfg['threshold']]
    forest_key = [cfg['seed'], cfg['counts'], cfg['forest'], cfg['crest'], geometry_key]
    keys = {'route': digest([geometry_key, cfg['material']]),
            'forest': digest(forest_key), 'crest': digest(forest_key),
            'masks': digest([forest_key, cfg['clearance']]),
            'details': digest([geometry_key, cfg['clearance']['maximum_stones'], cfg['clearance']['maximum_litter']])}
    todo = {key for key in requested if components is not None or state.get(key) != keys[key]}
    if not todo:
        assert before == random.getstate()
        return previous
    result = dict(previous)
    if 'route' in todo:
        surface, result['route'] = build_trail(scene, prepared, ROOT)
    else:
        surface = mapped_surface(scene, final=True) if 'V07_TERRAIN_NEAR' in scene.objects else prepared['original']
    if todo & {'forest', 'crest'}:
        final_rows, result['forest'] = apply_forest_layers(scene, prepared, surface, todo)
    elif bpy.data.texts.get('V07_FOREST_REGISTRY.json'):
        final_rows = json.loads(bpy.data.texts['V07_FOREST_REGISTRY.json'].as_string())
    else:
        final_rows = final_forest_records(prepared, surface)
    if 'masks' in todo:
        result['masks'] = apply_masks(scene, prepared, surface, final_rows)
    if 'details' in todo:
        result['details'] = build_details(scene, prepared, surface)
    result['cameras'] = make_review_cameras(scene, P, prepared, surface)
    configure_p0(scene)
    for key in todo:
        state[key] = keys[key]
    result['configuration_sha256'] = digest(cfg)
    result['global_rng_unchanged'] = random.getstate() == before
    assert result['global_rng_unchanged']
    scene['v07_component_state'] = json.dumps(state, sort_keys=True)
    scene['forest_trail_v07_summary'] = json.dumps(result, sort_keys=True)
    return result

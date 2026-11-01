import bpy
import bmesh
import math
import json
import sys
from pathlib import Path
from mathutils import Vector, Matrix
import numpy as np

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "output"
OUT.mkdir(exist_ok=True)
PI = math.pi
TAU = math.tau

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
for block in list(bpy.data.collections):
    if block.name != "Collection":
        bpy.data.collections.remove(block)
def collection(name):
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    return c

COLS = {
    "root": collection("00 • STARLING-01"),
    "body": collection("01 • Ceramic fuselage"),
    "nose": collection("02 • Fairing and collar"),
    "window": collection("03 • Optical cockpit"),
    "fins": collection("04 • Sculpted stabilizers"),
    "engine": collection("05 • Propulsion system"),
    "details": collection("06 • Service details and livery"),
    "studio": collection("90 • Studio"),
}
CURRENT = COLS["body"]

def move(obj, coll=None):
    coll = coll or CURRENT
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    coll.objects.link(obj)
    return obj

def srgb(hex_color):
    h = hex_color.lstrip("#")
    vals = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in vals)

def material(name, color, metallic=0.0, roughness=0.3, coat=0.0, transmission=0.0, emission=None):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value = (*srgb(color), 1)
    p.inputs["Metallic"].default_value = metallic
    p.inputs["Roughness"].default_value = roughness
    p.inputs["Coat Weight"].default_value = coat
    p.inputs["Coat Roughness"].default_value = 0.18
    p.inputs["Transmission Weight"].default_value = transmission
    p.inputs["IOR"].default_value = 1.46
    if emission:
        p.inputs["Emission Color"].default_value = (*srgb(emission[0]), 1)
        p.inputs["Emission Strength"].default_value = emission[1]
    m.diffuse_color = (*srgb(color), 1)
    return m

def microfinish(mat, scale=180, strength=0.025, distance=0.006, brushed=False):
    nt = mat.node_tree
    p = nt.nodes.get("Principled BSDF")
    tex = nt.nodes.new("ShaderNodeTexNoise")
    tex.inputs["Scale"].default_value = scale
    tex.inputs["Detail"].default_value = 2
    coord = nt.nodes.new("ShaderNodeTexCoord")
    if brushed:
        mapping = nt.nodes.new("ShaderNodeVectorMath")
        mapping.operation = "MULTIPLY"
        mapping.inputs[1].default_value = (1.0, 1.0, 12.0)
        nt.links.new(coord.outputs["Generated"], mapping.inputs[0])
        nt.links.new(mapping.outputs[0], tex.inputs["Vector"])
        p.inputs["Anisotropic"].default_value = 0.35
    else:
        nt.links.new(coord.outputs["Generated"], tex.inputs["Vector"])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = strength
    bump.inputs["Distance"].default_value = distance
    nt.links.new(tex.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], p.inputs["Normal"])

MAT = {
    "ivory": material("01 | Ceramic enamel • warm ivory", "#F3F0E8", roughness=0.27, coat=0.25),
    "coral": material("02 | Ceramic enamel • coral orange", "#F26647", roughness=0.23, coat=0.38),
    "orange": material("03 | Accent enamel • warm apricot", "#FFAA64", roughness=0.26, coat=0.28),
    "champagne": material("04 | Satin champagne alloy", "#C8C4BD", metallic=0.88, roughness=0.25),
    "titanium": material("05 | Deep titanium", "#303844", metallic=0.82, roughness=0.30),
    "silver": material("06 | Brushed silver", "#BCC4CB", metallic=0.95, roughness=0.24),
    "rubber": material("07 | Graphite elastomer", "#151C24", roughness=0.52),
    "seam": material("08 | Recess shadow", "#586069", metallic=0.15, roughness=0.48),
    "heat": material("09 | Refractory nozzle interior", "#171D25", metallic=0.62, roughness=0.43),
    "glass": material("10 | Optical cyan glass", "#C9F7FA", roughness=0.065, coat=0.20, transmission=0.97),
    "glow": material("11 | Ion blue", "#8DEEFF", roughness=0.22, emission=("#8DEEFF", 1.8)),
    "instrument": material("12 | Instrument phosphor", "#65D9E6", roughness=0.28, emission=("#65D9E6", 2.3)),
    "lamp": material("13 | Navigation amber", "#FFAA64", roughness=0.18, emission=("#FFAA64", 2.5)),
    "ground": material("90 | Warm stone cyclorama", "#D8D1C5", roughness=0.76),
}
microfinish(MAT["ivory"], scale=210, strength=0.025, distance=0.004)
microfinish(MAT["coral"], scale=190, strength=0.022, distance=0.004)
microfinish(MAT["titanium"], scale=160, strength=0.06, distance=0.008, brushed=True)
microfinish(MAT["silver"], scale=190, strength=0.05, distance=0.006, brushed=True)
nt = MAT["glass"].node_tree
absorb = nt.nodes.new("ShaderNodeVolumeAbsorption")
absorb.inputs["Color"].default_value = (*srgb("#65D9E6"), 1)
absorb.inputs["Density"].default_value = 0.16
nt.links.new(absorb.outputs[0], nt.nodes.get("Material Output").inputs["Volume"])


def mesh_object(name, verts, faces, mat, coll=None, smooth=True):
    mesh = bpy.data.meshes.new(name + " · mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    (coll or CURRENT).objects.link(obj)
    if mat:
        obj.data.materials.append(mat)
    for p in mesh.polygons:
        p.use_smooth = smooth
    return obj


def bevel(obj, width=0.02, segments=3, weighted=True):
    mod = obj.modifiers.new("Precision edge radii", "BEVEL")
    mod.width = width
    mod.segments = segments
    if weighted:
        mod.harden_normals = True
        wn = obj.modifiers.new("Area weighted normals", "WEIGHTED_NORMAL")
        wn.keep_sharp = True
    return obj


def catmull_open(points, samples=8):
    pts = [Vector(p) for p in points]
    out = []
    for i in range(len(pts) - 1):
        p0, p1 = pts[max(i - 1, 0)], pts[i]
        p2, p3 = pts[i + 1], pts[min(i + 2, len(pts) - 1)]
        for j in range(samples):
            t = j / samples
            v = 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t * t * t)
            out.append(tuple(v))
    out.append(tuple(pts[-1]))
    return out


def catmull_closed(points, samples=5):
    pts = [Vector(p) for p in points]
    out = []
    for i in range(len(pts)):
        p0, p1 = pts[(i - 1) % len(pts)], pts[i]
        p2, p3 = pts[(i + 1) % len(pts)], pts[(i + 2) % len(pts)]
        for j in range(samples):
            t = j / samples
            v = 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t * t * t)
            out.append(tuple(v))
    return out


def lathe(name, profile, mat, segments=160, caps=False, closed=False, coll=None, extra_mats=None, mat_ids=None):
    verts = []
    for r, z in profile:
        for j in range(segments):
            a = TAU * j / segments
            verts.append((max(r, 0.0005) * math.cos(a), max(r, 0.0005) * math.sin(a), z))
    faces, ids = [], []
    count = len(profile) if closed else len(profile) - 1
    for i in range(count):
        ni = (i + 1) % len(profile)
        for j in range(segments):
            nj = (j + 1) % segments
            faces.append((i * segments + j, i * segments + nj, ni * segments + nj, ni * segments + j))
            ids.append(mat_ids[i] if mat_ids else 0)
    if caps and not closed:
        faces.append(tuple(reversed(range(segments))))
        ids.append(0)
        faces.append(tuple((len(profile) - 1) * segments + j for j in range(segments)))
        ids.append(0)
    obj = mesh_object(name, verts, faces, mat, coll)
    if extra_mats:
        for m in extra_mats:
            obj.data.materials.append(m)
    for p, idx in zip(obj.data.polygons, ids):
        p.material_index = idx
    return obj


def torus(name, radius, tube, loc, mat, normal=(0, 0, 1), coll=None, major_segments=128, minor_segments=16):
    bpy.ops.mesh.primitive_torus_add(major_radius=radius, minor_radius=tube, major_segments=major_segments, minor_segments=minor_segments, location=loc)
    obj = move(bpy.context.object, coll)
    obj.name = name
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(Vector(normal).normalized())
    obj.data.materials.append(mat)
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj


def cylinder(name, radius, depth, loc, mat, normal=(0, 0, 1), vertices=64, edge=0.008, coll=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    obj = move(bpy.context.object, coll)
    obj.name = name
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(Vector(normal).normalized())
    obj.data.materials.append(mat)
    for p in obj.data.polygons:
        p.use_smooth = len(p.vertices) == 4
    if edge:
        bevel(obj, edge, 3)
    return obj


def box(name, dims, loc, mat, edge=0.02, rotation=None, coll=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = move(bpy.context.object, coll)
    obj.name = name
    obj.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if rotation is not None:
        obj.rotation_euler = rotation
    obj.data.materials.append(mat)
    if edge:
        bevel(obj, edge, 4)
    return obj


def sphere(name, loc, scale, mat, coll=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, location=loc)
    obj = move(bpy.context.object, coll)
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(mat)
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj


def path(name, points, radius, mat, cyclic=False, coll=None):
    data = bpy.data.curves.new(name + " · path", "CURVE")
    data.dimensions = "3D"
    data.resolution_u = 2
    data.bevel_depth = radius
    data.bevel_resolution = 3
    spline = data.splines.new("POLY")
    spline.points.add(len(points) - 1)
    for p, co in zip(spline.points, points):
        p.co = (*co, 1)
    spline.use_cyclic_u = cyclic
    obj = bpy.data.objects.new(name, data)
    (coll or CURRENT).objects.link(obj)
    data.materials.append(mat)
    return obj


BODY_CTRL = [
    (0.64, 1.16), (0.76, 1.25), (0.88, 1.43), (0.99, 1.76),
    (1.075, 2.20), (1.10, 2.68), (1.065, 3.13), (1.00, 3.52),
    (0.925, 3.82), (0.915, 3.94),
]
BODY = catmull_open(BODY_CTRL, 10)
NOSE_CTRL = [
    (0.915, 3.955), (0.90, 4.09), (0.83, 4.29), (0.69, 4.52),
    (0.50, 4.73), (0.29, 4.91), (0.12, 5.035), (0.035, 5.075), (0.001, 5.080),
]
NOSE = catmull_open(NOSE_CTRL, 10)


def radius_at(z, profile=BODY):
    if z <= profile[0][1]:
        return profile[0][0]
    if z >= profile[-1][1]:
        return profile[-1][0]
    for (r0, z0), (r1, z1) in zip(profile, profile[1:]):
        if z0 <= z <= z1:
            t = (z - z0) / max(z1 - z0, 1e-8)
            return r0 * (1 - t) + r1 * t


def body_slice(name, z0, z1):
    profile = [(radius_at(z0), z0)]
    profile.extend((r, z) for r, z in BODY if z0 < z < z1)
    profile.append((radius_at(z1), z1))
    return lathe(name, profile, MAT["ivory"], segments=192, caps=True, coll=COLS["body"])


CURRENT = COLS["body"]
body_slice("Fuselage / lower pressure shell", 1.16, 2.015)
body_slice("Fuselage / mid pressure shell", 2.029, 3.665)
body_slice("Fuselage / upper pressure shell", 3.679, 3.94)
lathe("Continuous recessed seam carrier", [(max(r - 0.018, 0.01), z) for r, z in BODY], MAT["seam"], segments=128, caps=True, coll=COLS["body"])
for z in (2.022, 3.672):
    torus("Precision circumferential shell break", radius_at(z) - 0.006, 0.009, (0, 0, z), MAT["seam"], coll=COLS["body"], major_segments=192)
for z in (1.31, 3.83):
    torus("Ivory structural bead", radius_at(z) + 0.002, 0.014, (0, 0, z), MAT["ivory"], coll=COLS["body"], major_segments=192)

for idx, angle in enumerate((0.12, 1.68, 3.10, 4.63)):
    points = []
    for r, z in BODY:
        if 1.42 < z < 3.76:
            points.append(((r + 0.003) * math.cos(angle), (r + 0.003) * math.sin(angle), z))
    path(f"Longitudinal shell seam {idx + 1:02d}", points, 0.005, MAT["seam"], coll=COLS["body"])

CURRENT = COLS["nose"]
lathe("Fairing / continuous coral ceramic", NOSE, MAT["coral"], segments=224, caps=True, coll=COLS["nose"])
COLLAR = catmull_open([(0.91, 3.855), (0.94, 3.865), (0.955, 3.895), (0.955, 3.955), (0.94, 3.99), (0.915, 4.005)], 5)
lathe("Machined fairing collar", COLLAR, MAT["champagne"], segments=192, caps=True, coll=COLS["nose"])
for z in (3.89, 3.955):
    torus("Collar annular groove", 0.953, 0.008, (0, 0, z), MAT["titanium"], coll=COLS["nose"], major_segments=192)
for z, mat in ((3.795, MAT["orange"]), (3.835, MAT["champagne"])):
    torus("Twin fairing datum line", radius_at(z) + 0.008, 0.012, (0, 0, z), mat, coll=COLS["nose"], major_segments=192)
for i in range(12):
    a = TAU * i / 12
    cylinder(f"Fairing collar fastener {i + 1:02d}", 0.018, 0.015, (0.956 * math.cos(a), 0.956 * math.sin(a), 3.925), MAT["silver"], normal=(math.cos(a), math.sin(a), 0), vertices=24, edge=0.003, coll=COLS["nose"])

CURRENT = COLS["window"]
CZ = 3.12
cylinder("Porthole / recessed ceramic mounting saddle", 0.575, 0.25, (0, -1.005, CZ), MAT["ivory"], normal=(0, -1, 0), vertices=128, edge=0.045, coll=COLS["window"])
cylinder("Porthole / shadow reveal", 0.548, 0.07, (0, -1.115, CZ), MAT["seam"], normal=(0, -1, 0), vertices=128, edge=0.018, coll=COLS["window"])
torus("Porthole / champagne outer bezel", 0.485, 0.066, (0, -1.17, CZ), MAT["champagne"], normal=(0, -1, 0), coll=COLS["window"], major_segments=160, minor_segments=24)
torus("Porthole / elastomer seal", 0.422, 0.025, (0, -1.19, CZ), MAT["rubber"], normal=(0, -1, 0), coll=COLS["window"], major_segments=160, minor_segments=20)
cylinder("Porthole / interior instrument well", 0.413, 0.065, (0, -1.127, CZ), MAT["titanium"], normal=(0, -1, 0), vertices=128, edge=0.018, coll=COLS["window"])

R = 0.412
DEPTH = 0.165
SEG = 160
RINGS = 36
verts = [(0, -1.19 - DEPTH, CZ)]
for i in range(1, RINGS + 1):
    t = (PI / 2) * i / RINGS
    for j in range(SEG):
        a = TAU * j / SEG
        verts.append((R * math.sin(t) * math.cos(a), -1.19 - DEPTH * math.cos(t), CZ + R * math.sin(t) * math.sin(a)))
faces = []
for j in range(SEG):
    faces.append((0, 1 + j, 1 + (j + 1) % SEG))
for i in range(RINGS - 1):
    s0, s1 = 1 + i * SEG, 1 + (i + 1) * SEG
    for j in range(SEG):
        nj = (j + 1) % SEG
        faces.append((s0 + j, s1 + j, s1 + nj, s0 + nj))
outer_count = len(verts)
inner_verts = [(x, y + 0.018, z) for x, y, z in verts]
verts += inner_verts
faces += [tuple(v + outer_count for v in reversed(f)) for f in list(faces)]
rim_start = 1 + (RINGS - 1) * SEG
for j in range(SEG):
    nj = (j + 1) % SEG
    faces.append((rim_start + j, rim_start + nj, rim_start + nj + outer_count, rim_start + j + outer_count))
glass = mesh_object("Porthole / solid optical glass dome", verts, faces, MAT["glass"], COLS["window"])

for k, (rad, start, end) in enumerate(((0.27, 0.18, 2.25), (0.32, 3.15, 5.65))):
    pts = []
    for j in range(70):
        a = start + (end - start) * j / 69
        pts.append((rad * math.cos(a), -1.166, CZ + rad * math.sin(a)))
    path(f"Interior luminous instrument arc {k + 1}", pts, 0.006, MAT["instrument"], coll=COLS["window"])
for i in range(7):
    x = (i - 3) * 0.035
    z = CZ - 0.11 + 0.018 * math.cos(i * 1.3)
    sphere(f"Interior status pixel {i + 1}", (x, -1.172, z), (0.009, 0.006, 0.009), MAT["glow"], COLS["window"])
for i in range(8):
    a = TAU * i / 8 + PI / 8
    x, z = 0.516 * math.cos(a), CZ + 0.516 * math.sin(a)
    cylinder(f"Porthole screw {i + 1:02d} / head", 0.025, 0.025, (x, -1.231, z), MAT["silver"], normal=(0, -1, 0), vertices=32, edge=0.004, coll=COLS["window"])
    slot = box(f"Porthole screw {i + 1:02d} / machined slot", (0.028, 0.005, 0.006), (x, -1.246, z), MAT["titanium"], edge=0.002, coll=COLS["window"])
    slot.rotation_euler[1] = a


def fin_point(p, angle, t=0):
    r, z = p
    return (r * math.cos(angle) - t * math.sin(angle), r * math.sin(angle) + t * math.cos(angle), z)


def fin_solid(name, outline, angle, mat, thickness=0.16, t_offset=0, sculpt=True, coll=None):
    pts = catmull_closed(outline, 5) if sculpt else outline
    verts = []
    for side in (-1, 1):
        for r, z in pts:
            th = thickness * (1.12 - 0.42 * max(0, min(1, (r - 0.80) / 0.80)))
            verts.append(fin_point((r, z), angle, t_offset + side * th / 2))
    n = len(pts)
    faces = [tuple(reversed(range(n))), tuple(range(n, 2 * n))]
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, j + n, i + n))
    obj = mesh_object(name, verts, faces, mat, coll or COLS["fins"])
    bevel(obj, min(0.035, thickness * 0.24), 4)
    return obj


FIN_OUTLINE = [(0.79, 1.04), (0.82, 2.30), (1.04, 2.12), (1.48, 1.43), (1.59, 1.12), (1.47, 0.98), (0.91, 0.96)]
ARMOR_OUTLINE = [(0.94, 1.24), (0.94, 2.10), (1.055, 1.98), (1.38, 1.40), (1.38, 1.23), (1.14, 1.15)]
for i, angle in enumerate((0, TAU / 3, 2 * TAU / 3)):
    tag = f"Fin {i + 1}"
    fin_solid(tag + " / sculpted load-bearing shell", FIN_OUTLINE, angle, MAT["coral"], thickness=0.18)
    for side in (-1, 1):
        fin_solid(tag + f" / ivory armor {side:+d}", ARMOR_OUTLINE, angle, MAT["ivory"], thickness=0.022, t_offset=side * 0.103)
    trim = catmull_open([(1.05, 2.10), (1.49, 1.42), (1.59, 1.12), (1.47, 0.98)], 10)
    path(tag + " / fine alloy edge", [fin_point(p, angle) for p in trim], 0.012, MAT["champagne"], coll=COLS["fins"])
    tangent = (-math.sin(angle), math.cos(angle), 0)
    for j, z in enumerate((1.28, 1.80)):
        loc = fin_point((0.89, z), angle)
        cylinder(tag + f" / root hinge {j + 1}", 0.125, 0.36, loc, MAT["titanium"], normal=tangent, edge=0.016, coll=COLS["fins"])
        for side in (-1, 1):
            p = Vector(loc) + Vector(tangent) * side * 0.185
            cylinder(tag + f" / hinge cap {j + 1}-{side:+d}", 0.088, 0.022, p, MAT["champagne"], normal=tangent, edge=0.009, coll=COLS["fins"])
            cylinder(tag + f" / hinge pin {j + 1}-{side:+d}", 0.030, 0.026, p + Vector(tangent) * side * 0.014, MAT["silver"], normal=tangent, vertices=32, edge=0.004, coll=COLS["fins"])

CURRENT = COLS["engine"]
TRANSITION = catmull_open([(0.60, 1.00), (0.66, 1.04), (0.73, 1.13), (0.74, 1.24), (0.69, 1.31)], 7)
lathe("Engine / compact mechanical transition", TRANSITION, MAT["titanium"], segments=160, caps=True, coll=COLS["engine"])
for z, r in ((1.07, 0.68), (1.23, 0.735)):
    torus("Engine / transition flange", r, 0.028, (0, 0, z), MAT["champagne"], coll=COLS["engine"], major_segments=160)
for i in range(16):
    a = TAU * i / 16
    cylinder(f"Engine flange bolt {i + 1:02d}", 0.024, 0.026, (0.664 * math.cos(a), 0.664 * math.sin(a), 1.065), MAT["silver"], vertices=6, edge=0.003, coll=COLS["engine"])

OUTER_CTRL = [(0.60, 0.20), (0.64, 0.25), (0.61, 0.34), (0.53, 0.50), (0.41, 0.72), (0.30, 0.94), (0.31, 1.03)]
INNER_CTRL = [(0.55, 0.22), (0.55, 0.28), (0.51, 0.39), (0.43, 0.55), (0.32, 0.76), (0.24, 0.94), (0.25, 1.03)]
OUTER = catmull_open(OUTER_CTRL, 8)
INNER = catmull_open(INNER_CTRL, 8)
NOZZLE_PROFILE = OUTER + list(reversed(INNER))
NOZZLE_MATS = [0] * (len(OUTER) - 1) + [2] + [1] * (len(INNER) - 1) + [2]
lathe("Engine / thick-wall bell with refractory interior", NOZZLE_PROFILE, MAT["titanium"], segments=192, closed=True, coll=COLS["engine"], extra_mats=[MAT["heat"], MAT["silver"]], mat_ids=NOZZLE_MATS)
for z in (0.25, 0.34, 0.46, 0.60, 0.76, 0.92):
    r = radius_at(z, OUTER)
    torus("Engine / circumferential cooling channel", r + 0.003, 0.011, (0, 0, z), MAT["heat"], coll=COLS["engine"], major_segments=160)
for z, r, tube in ((0.225, 0.606, 0.026), (0.36, 0.588, 0.018), (0.98, 0.307, 0.018)):
    torus("Engine / machined nozzle lip", r, tube, (0, 0, z), MAT["silver"], coll=COLS["engine"], major_segments=192)
VANE_OUTLINE = [(0.245, 0.93), (0.30, 0.82), (0.51, 0.39), (0.535, 0.31), (0.48, 0.37), (0.26, 0.79)]
for i in range(12):
    fin_solid(f"Engine / internal guide vane {i + 1:02d}", VANE_OUTLINE, TAU * i / 12, MAT["silver"], thickness=0.024, sculpt=False, coll=COLS["engine"])
cylinder("Engine / recessed ion core", 0.17, 0.055, (0, 0, 0.895), MAT["glow"], vertices=96, edge=0.018, coll=COLS["engine"])
torus("Engine / core containment ring", 0.205, 0.018, (0, 0, 0.86), MAT["champagne"], coll=COLS["engine"])
for i in range(6):
    a = TAU * i / 6
    p0 = Vector((0.57 * math.cos(a), 0.57 * math.sin(a), 1.08))
    p1 = Vector((0.69 * math.cos(a), 0.69 * math.sin(a), 1.25))
    mid = (p0 + p1) / 2
    cylinder(f"Engine / radial brace {i + 1}", 0.035, (p1 - p0).length, mid, MAT["champagne"], normal=p1 - p0, vertices=32, edge=0.008, coll=COLS["engine"])

CURRENT = COLS["details"]

def rounded_rect(w, h, r, steps=7):
    pts = []
    for cx, cy, start in ((w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, PI / 2), (-w / 2 + r, -h / 2 + r, PI), (w / 2 - r, -h / 2 + r, 3 * PI / 2)):
        for i in range(steps):
            a = start + (PI / 2) * i / (steps - 1)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def surface_panel(name, angle, z, width, height, offset, mat, corner=0.05):
    boundary = rounded_rect(width, height, corner)
    def mapped(u, v):
        zz = z + v
        rr = radius_at(zz) + offset
        aa = angle + u / max(radius_at(zz), 0.2)
        return (rr * math.cos(aa), rr * math.sin(aa), zz)
    verts = [mapped(0, 0)] + [mapped(u, v) for u, v in boundary]
    faces = [(0, i + 1, ((i + 1) % len(boundary)) + 1) for i in range(len(boundary))]
    obj = mesh_object(name, verts, faces, mat, COLS["details"])
    solid = obj.modifiers.new("Real panel thickness", "SOLIDIFY")
    solid.thickness = 0.012
    solid.offset = 0
    bevel(obj, 0.004, 3, weighted=False)
    return obj


for idx, angle in enumerate((0.68, 3.85)):
    surface_panel(f"Service hatch {idx + 1} / recessed gasket", angle, 2.58, 0.48, 0.62, 0.008, MAT["seam"], 0.085)
    surface_panel(f"Service hatch {idx + 1} / flush ceramic cover", angle, 2.58, 0.445, 0.585, 0.020, MAT["ivory"], 0.075)
    for u in (-0.16, 0.16):
        for v in (-0.23, 0.23):
            zz = 2.58 + v
            aa = angle + u / radius_at(zz)
            rr = radius_at(zz) + 0.035
            cylinder(f"Service hatch {idx + 1} / captive screw", 0.018, 0.014, (rr * math.cos(aa), rr * math.sin(aa), zz), MAT["champagne"], normal=(math.cos(aa), math.sin(aa), 0), vertices=24, edge=0.003, coll=COLS["details"])

for group, angle in enumerate((0.12, 2.98)):
    surface_panel(f"Vent group {group + 1} / inset", angle, 2.08, 0.46, 0.39, 0.008, MAT["titanium"], 0.04)
    radial = Vector((math.cos(angle), math.sin(angle), 0))
    tangent = Vector((-math.sin(angle), math.cos(angle), 0))
    for j in range(6):
        z = 1.945 + j * 0.054
        loc = radial * (radius_at(z) + 0.022) + Vector((0, 0, z))
        obj = box(f"Vent group {group + 1} / louvre {j + 1}", (0.37, 0.025, 0.022), loc, MAT["champagne"], edge=0.007, coll=COLS["details"])
        rot = Matrix((tangent, -radial, Vector((0, 0, 1)))).transposed()
        obj.rotation_euler = rot.to_euler()

for i in range(20):
    a = TAU * i / 20
    z = 1.54
    rr = radius_at(z) + 0.008
    radial = Vector((math.cos(a), math.sin(a), 0))
    tangent = Vector((-math.sin(a), math.cos(a), 0))
    obj = box(f"Aft ventilation slot {i + 1:02d}", (0.11, 0.018, 0.16), radial * rr + Vector((0, 0, z)), MAT["titanium"], edge=0.025, coll=COLS["details"])
    rot = Matrix((tangent, -radial, Vector((0, 0, 1)))).transposed()
    obj.rotation_euler = rot.to_euler()

for i in range(16):
    a = TAU * i / 16
    z = 3.745
    rr = radius_at(z) + 0.012
    cylinder(f"Upper shell rivet {i + 1:02d}", 0.016, 0.012, (rr * math.cos(a), rr * math.sin(a), z), MAT["champagne"], normal=(math.cos(a), math.sin(a), 0), vertices=24, edge=0.004, coll=COLS["details"])

for i, (a, mat) in enumerate(((0.82, MAT["instrument"]), (3.96, MAT["lamp"]))):
    z = 2.89
    rr = radius_at(z)
    radial = Vector((math.cos(a), math.sin(a), 0))
    cylinder(f"Navigation lamp {i + 1} / bezel", 0.060, 0.036, radial * (rr + 0.018) + Vector((0, 0, z)), MAT["champagne"], normal=radial, edge=0.010, coll=COLS["details"])
    sphere(f"Navigation lamp {i + 1} / lens", radial * (rr + 0.045) + Vector((0, 0, z)), (0.041, 0.041, 0.041), mat, COLS["details"])


def surface_text(name, text, angle, z, size, mat, offset=0.018):
    data = bpy.data.curves.new(name, "FONT")
    data.body = text
    data.align_x = "CENTER"
    data.align_y = "CENTER"
    data.size = size
    data.extrude = 0.0008
    data.bevel_depth = 0.0004
    data.bevel_resolution = 2
    obj = bpy.data.objects.new(name, data)
    COLS["details"].objects.link(obj)
    radial = Vector((math.cos(angle), math.sin(angle), 0))
    tangent = Vector((-math.sin(angle), math.cos(angle), 0))
    up = Vector((0, 0, 1))
    obj.rotation_euler = Matrix((tangent, up, radial)).transposed().to_euler()
    obj.location = radial * (radius_at(z) + offset) + Vector((0, 0, z))
    data.materials.append(mat)
    return obj


surface_text("Livery / STARLING", "S T A R L I N G", -PI / 2, 2.37, 0.115, MAT["titanium"])
surface_text("Livery / mission designation", "0 1   /   I N T E R S T E L L A R   C O U R I E R", -PI / 2, 2.205, 0.043, MAT["seam"])
surface_text("Livery / lower serial", "S-01  •  deep space service", -PI / 2, 1.72, 0.052, MAT["titanium"])
BADGE_A = 1.03
BADGE_Z = 3.23
badge_r = radius_at(BADGE_Z) + 0.025
badge_n = (math.cos(BADGE_A), math.sin(BADGE_A), 0)
badge_loc = (badge_r * math.cos(BADGE_A), badge_r * math.sin(BADGE_A), BADGE_Z)
torus("Mission badge / orbital ring", 0.103, 0.009, badge_loc, MAT["champagne"], normal=badge_n, coll=COLS["details"], major_segments=80)
for a in (0, PI / 2):
    pts = []
    for j in range(40):
        t = TAU * j / 39
        u = 0.072 * math.cos(t)
        v = 0.027 * math.sin(t)
        uu = u * math.cos(a) - v * math.sin(a)
        vv = u * math.sin(a) + v * math.cos(a)
        tangent = Vector((-math.sin(BADGE_A), math.cos(BADGE_A), 0))
        p = Vector(badge_loc) + tangent * uu + Vector((0, 0, vv)) + Vector(badge_n) * 0.006
        pts.append(p)
    path("Mission badge / geometric orbit", pts, 0.006, MAT["coral"], cyclic=True, coll=COLS["details"])
surface_text("Mission badge / number", "01", BADGE_A, 3.045, 0.085, MAT["titanium"])

CURRENT = COLS["root"]
root = bpy.data.objects.new("STARLING-01 | MASTER • animated turntable", None)
COLS["root"].objects.link(root)
root.empty_display_type = "CIRCLE"
root.empty_display_size = 1.3
root["Asset"] = "STARLING-01 / 星际信使"
root["Design"] = "Original retro-futurist animated-film hero prop"
root["Units"] = "meters"
root["Height"] = "4.90 m above display plane"
for coll in (COLS["body"], COLS["nose"], COLS["window"], COLS["fins"], COLS["engine"], COLS["details"]):
    for obj in coll.objects:
        obj.parent = root

CURRENT = COLS["studio"]
box("Studio / seamless ground", (2000, 2000, 0.10), (0, 0, 0.13), MAT["ground"], edge=0, coll=COLS["studio"])

scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.length_unit = "METERS"
world = bpy.data.worlds.new("Studio HDRI • generated softboxes")
scene.world = world
world.use_nodes = True
nt = world.node_tree
nt.nodes.clear()
out = nt.nodes.new("ShaderNodeOutputWorld")
bg = nt.nodes.new("ShaderNodeBackground")
bg.inputs["Strength"].default_value = 0.28
tex = nt.nodes.new("ShaderNodeTexEnvironment")
W, H = 1024, 512
u = np.linspace(0, 1, W, endpoint=False)[None, :]
v = np.linspace(0, 1, H)[:, None]
def wrapped(a):
    return (a + 0.5) % 1 - 0.5
base = np.zeros((H, W, 3), dtype=np.float32) + np.array([0.20, 0.22, 0.25])
for cu, cv, su, sv, power, color in (
    (0.17, 0.66, 0.075, 0.18, 3.5, (1.0, 0.88, 0.74)),
    (0.62, 0.57, 0.10, 0.20, 2.4, (0.68, 0.83, 1.0)),
    (0.84, 0.72, 0.065, 0.13, 3.0, (1.0, 0.67, 0.43)),
):
    lobe = np.exp(-((wrapped(u - cu) / su) ** 2 + ((v - cv) / sv) ** 2) * 1.6)[..., None]
    base += lobe * power * np.array(color)
rgba = np.ones((H, W, 4), dtype=np.float32)
rgba[:, :, :3] = base
img = bpy.data.images.new("Packed studio HDRI", width=W, height=H, float_buffer=True)
img.pixels.foreach_set(rgba.ravel())
img.pack()
tex.image = img
nt.links.new(tex.outputs["Color"], bg.inputs["Color"])
nt.links.new(bg.outputs[0], out.inputs[0])


def area(name, loc, energy, color, size, target=(0, 0, 2.4), shape="DISK", size_y=None):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.color = color
    data.shape = shape
    data.size = size
    if size_y is not None:
        data.size_y = size_y
    obj = bpy.data.objects.new(name, data)
    COLS["studio"].objects.link(obj)
    obj.location = loc
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()
    return obj


area("Key / large warm silk", (-4.5, -5.5, 8.0), 1050, (1.0, 0.86, 0.73), 5.0, shape="RECTANGLE", size_y=6.0)
area("Fill / cool vertical card", (5.0, -2.5, 4.8), 650, (0.67, 0.83, 1.0), 4.0, shape="RECTANGLE", size_y=5.0)
area("Rim / warm rear strip", (1.8, 4.0, 6.2), 1300, (1.0, 0.68, 0.43), 3.0, shape="RECTANGLE", size_y=4.5)
area("Top / broad reflection", (-1.0, 1.0, 9.0), 550, (1.0, 0.97, 0.90), 3.5)
ld = bpy.data.lights.new("Engine / subtle ion spill", "POINT")
ld.energy = 18
ld.color = srgb("#8DEEFF")
ld.shadow_soft_size = 0.20
lo = bpy.data.objects.new(ld.name, ld)
COLS["studio"].objects.link(lo)
lo.location = (0, 0, 0.62)

cam_data = bpy.data.cameras.new("Hero • 80 mm product lens")
cam = bpy.data.objects.new("CAMERA • hero three-quarter", cam_data)
COLS["studio"].objects.link(cam)
cam.location = (7.2, -11.5, 6.25)
target = Vector((0, 0, 2.54))
cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
cam_data.lens = 80
cam_data.sensor_width = 36
scene.camera = cam

scene.render.engine = "CYCLES"
prefs = bpy.context.preferences.addons["cycles"].preferences
prefs.compute_device_type = "METAL"
prefs.get_devices()
for device in prefs.devices:
    device.use = device.type == "METAL"
scene.cycles.device = "GPU"
scene.cycles.samples = 128
scene.cycles.use_denoising = True
scene.cycles.adaptive_threshold = 0.015
scene.cycles.max_bounces = 10
scene.cycles.transmission_bounces = 8
scene.cycles.glossy_bounces = 5
scene.render.resolution_x = 2048
scene.render.resolution_y = 2048
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGB"
scene.render.image_settings.color_depth = "8"
scene.render.film_transparent = False
scene.view_settings.view_transform = "AgX"
scene.view_settings.look = "AgX - Medium High Contrast"
scene.view_settings.exposure = 0.0
scene.render.fps = 24
scene.frame_start = 1
scene.frame_end = 240
scene.render.filepath = str(OUT / "STARLING-01_Hero_2048.png")

root.rotation_euler = (0, 0, 0)
root.keyframe_insert(data_path="rotation_euler", index=2, frame=1)
root.rotation_euler.z = TAU
root.keyframe_insert(data_path="rotation_euler", index=2, frame=241)
action = root.animation_data.action
try:
    fcurves = action.fcurves
except AttributeError:
    fcurves = []
    for layer in action.layers:
        for strip in layer.strips:
            bag = strip.channelbag(root.animation_data.action_slot)
            if bag:
                fcurves.extend(bag.fcurves)
for fc in fcurves:
    for kp in fc.keyframe_points:
        kp.interpolation = "LINEAR"
scene.frame_set(1)

bpy.ops.object.select_all(action="DESELECT")
root.select_set(True)
bpy.context.view_layer.objects.active = root
for screen in bpy.data.screens:
    for area_ui in screen.areas:
        if area_ui.type == "VIEW_3D":
            area_ui.spaces.active.region_3d.view_perspective = "CAMERA"

blend_path = OUT / "STARLING-01.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
stats = {
    "asset": "STARLING-01 / 星际信使",
    "blender": bpy.app.version_string,
    "objects_in_asset": sum(len(c.objects) for c in (COLS["body"], COLS["nose"], COLS["window"], COLS["fins"], COLS["engine"], COLS["details"])),
    "materials": len(MAT) - 1,
    "height_m": 4.88,
    "body_max_diameter_m": 2.2,
    "render": "Cycles / Metal / AgX",
    "animation": "240 frames at 24 fps, linear 360-degree master rotation",
}
(OUT / "asset_manifest.json").write_text(json.dumps(stats, indent=2, ensure_ascii=False))
print("ASSET_STATS", json.dumps(stats), flush=True)
if "--draft" in sys.argv:
    scene.render.resolution_x = 1100
    scene.render.resolution_y = 1100
    scene.cycles.samples = 40
    scene.cycles.adaptive_threshold = 0.035
    scene.render.filepath = str(OUT / "draft.png")
    bpy.ops.render.render(write_still=True)
    print("DRAFT_RENDERED", scene.render.filepath, flush=True)

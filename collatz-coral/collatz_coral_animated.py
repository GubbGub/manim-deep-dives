"""
Collatz coral, animated (Blender).

Paste into Blender's Scripting workspace and press Alt+P.
Every n in 2..N is traced backward from 1. Each step bends the strand:
even values one way, odd values the other, plus a small twist so it grows in 3D.
Numbers whose sequences end the same way share a branch.
The coral grows from the root over GROW_FRAMES while the camera orbits.
"""
import bpy, math
from mathutils import Vector, Matrix

N         = 1500     # numbers 2..N
STEP      = 0.15     # length of one step
EVEN_TURN = 0.11     # radians
ODD_TURN  = -0.24
TWIST     = 0.30     # roll per step (makes it 3D)
GROW_FRAMES = 180

for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
scene = bpy.context.scene
scene.frame_start, scene.frame_end = 1, 300
for eng in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
    try:
        scene.render.engine = eng
        break
    except Exception:
        pass
col = scene.collection


def collatz(n):
    s = [n]
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        s.append(n)
    return s[::-1]          # 1 ... n


paths = []
lo, hi = Vector((1e9,) * 3), Vector((-1e9,) * 3)
R_even = Matrix.Rotation(EVEN_TURN, 3, 'X')
R_odd = Matrix.Rotation(ODD_TURN, 3, 'X')
R_tw = Matrix.Rotation(TWIST, 3, 'Z')
for n in range(2, N + 1):
    s = collatz(n)
    pos, M = Vector((0, 0, 0)), Matrix.Identity(3)
    pts = [pos.copy()]
    for v in s[1:]:
        M = M @ R_tw @ (R_even if v % 2 == 0 else R_odd)
        pos = pos + M @ Vector((0, 0, STEP))
        pts.append(pos.copy())
        for a in range(3):
            lo[a], hi[a] = min(lo[a], pos[a]), max(hi[a], pos[a])
    paths.append((len(s), pts))


def mat(name, rgb, emit=0.0, metal=0.3):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*rgb, 1)
    p.inputs["Metallic"].default_value = metal
    p.inputs["Roughness"].default_value = 0.35
    if emit:
        p.inputs["Emission Color"].default_value = (*rgb, 1)
        p.inputs["Emission Strength"].default_value = emit
    return m


# colour by path length: indigo (short) -> gold (longest)
colors = [((0.02, 0.04, 0.25), 0.4), ((0.03, 0.10, 0.45), 0.6),
          ((0.05, 0.25, 0.70), 0.8), ((0.10, 0.55, 0.85), 1.0),
          ((0.60, 0.80, 0.95), 1.2), ((1.00, 0.60, 0.15), 3.0)]
lengths = sorted(L for L, _ in paths)
cuts = [lengths[int(len(lengths) * q)] for q in (0.3, 0.55, 0.75, 0.9, 0.97)]
groups = [[] for _ in colors]
for L, pts in paths:
    groups[sum(L >= c for c in cuts)].append(pts)

for i, pts_list in enumerate(groups):
    cu = bpy.data.curves.new("Collatz_%d" % i, 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = 2.2 * (0.010 + 0.004 * (len(groups) - i) / len(groups))
    cu.bevel_resolution = 1
    for pts in pts_list:
        sp = cu.splines.new('POLY')
        sp.points.add(len(pts) - 1)
        flat = []
        for p in pts:
            flat += [p.x, p.y, p.z, 1.0]
        sp.points.foreach_set("co", flat)
    ob = bpy.data.objects.new("Collatz_%d" % i, cu)
    rgb, e = colors[i]
    ob.data.materials.append(mat("Col_%d" % i, rgb, emit=e))
    col.objects.link(ob)
    cu.driver_add("bevel_factor_end").driver.expression = "min(1, frame/%d)" % GROW_FRAMES

bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18, location=(0, 0, 0))
seed = bpy.context.active_object
seed.name = "One"
seed.data.materials.append(mat("Seed", (1.0, 0.6, 0.15), emit=8.0, metal=1.0))
bpy.ops.object.shade_smooth()

world = scene.world or bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.004, 0.006, 0.02, 1)

center, size = (lo + hi) / 2, max(hi - lo)

key = bpy.data.lights.new("Key", 'AREA')
key.energy, key.size, key.color = 3000, 10, (0.75, 0.85, 1.0)
ko = bpy.data.objects.new("Key", key)
ko.location = center + Vector((-size, -size, size))
ko.rotation_euler = (math.radians(50), 0, math.radians(-45))
col.objects.link(ko)
glow = bpy.data.lights.new("SeedGlow", 'POINT')
glow.energy, glow.color = 800, (1.0, 0.6, 0.2)
col.objects.link(bpy.data.objects.new("SeedGlow", glow))

target = bpy.data.objects.new("Target", None)
target.location = (center.x, center.y, hi.z * 0.375)
col.objects.link(target)
target.driver_add("rotation_euler", 2).driver.expression = "frame*%.5f" % (2 * math.pi / 300)
cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
cam.data.lens = 20
cam.parent = target
cam.location = (size * 0.85, -size * 0.85, size * 0.12 + 1.5)
col.objects.link(cam)
tc = cam.constraints.new('TRACK_TO')
tc.target, tc.track_axis, tc.up_axis = target, 'TRACK_NEGATIVE_Z', 'UP_Y'
scene.camera = cam

for scr in bpy.data.screens:
    for area in scr.areas:
        if area.type == 'VIEW_3D':
            sp = area.spaces.active
            sp.shading.type = 'RENDERED'
            sp.region_3d.view_perspective = 'CAMERA'
            sp.overlay.show_overlays = False

scene.frame_set(1)
print("Collatz coral: %d numbers, longest path %d steps" % (N - 1, lengths[-1]))

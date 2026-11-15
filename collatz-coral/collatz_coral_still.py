"""
Collatz coral, clean still (Blender).

Flat emissive strands on a transparent background, with the path of n = 27
traced in gold. Renders a 3840x2160 RGBA PNG to ~/Documents/Collatz/
that wallpaper/wallpaper.tex lays out with LaTeX.
"""
import bpy, math, os
from mathutils import Vector, Matrix

N, STEP = 1500, 0.15
EVEN_TURN, ODD_TURN, TWIST = 0.11, -0.24, 0.30
HIGHLIGHT = 27          # 111 steps, peaks at 9232

for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
scene = bpy.context.scene
col = scene.collection
for eng in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
    try:
        scene.render.engine = eng
        break
    except Exception:
        pass
scene.view_settings.view_transform = 'Standard'
scene.render.film_transparent = True


def collatz(n):
    s = [n]
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        s.append(n)
    return s[::-1]


Re, Ro, Rt = (Matrix.Rotation(EVEN_TURN, 3, 'X'), Matrix.Rotation(ODD_TURN, 3, 'X'),
              Matrix.Rotation(TWIST, 3, 'Z'))


def trace(s):
    pos, M = Vector((0, 0, 0)), Matrix.Identity(3)
    pts = [pos.copy()]
    for v in s[1:]:
        M = M @ Rt @ (Re if v % 2 == 0 else Ro)
        pos = pos + M @ Vector((0, 0, STEP))
        pts.append(pos.copy())
    return pts


paths = [(len(collatz(n)), trace(collatz(n))) for n in range(2, N + 1)]
allp = [p for _, ps in paths for p in ps]
lo = Vector((min(p.x for p in allp), min(p.y for p in allp), min(p.z for p in allp)))
hi = Vector((max(p.x for p in allp), max(p.y for p in allp), max(p.z for p in allp)))
center, size = (lo + hi) / 2, max(hi - lo)


def emit(name, rgb, strength=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    e = nt.nodes.new('ShaderNodeEmission')
    e.inputs[0].default_value = (*rgb, 1)
    e.inputs[1].default_value = strength
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(e.outputs[0], out.inputs[0])
    return m


def curve_obj(name, pts_list, depth, material):
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth, cu.bevel_resolution = depth, 2
    for pts in pts_list:
        sp = cu.splines.new('POLY')
        sp.points.add(len(pts) - 1)
        flat = []
        for p in pts:
            flat += [p.x, p.y, p.z, 1.0]
        sp.points.foreach_set("co", flat)
    ob = bpy.data.objects.new(name, cu)
    ob.data.materials.append(material)
    col.objects.link(ob)
    return ob


ramp = [(0.10, 0.16, 0.42), (0.16, 0.26, 0.60), (0.26, 0.40, 0.76),
        (0.42, 0.56, 0.86), (0.66, 0.76, 0.93), (0.88, 0.91, 0.97)]
lengths = sorted(L for L, _ in paths)
cuts = [lengths[int(len(lengths) * q)] for q in (0.3, 0.55, 0.75, 0.9, 0.97)]
groups = [[] for _ in ramp]
for L, pts in paths:
    groups[sum(L >= c for c in cuts)].append(pts)
for i, g in enumerate(groups):
    curve_obj("Collatz_%d" % i, g, 0.012, emit("Ink_%d" % i, ramp[i]))

gold = emit("Gold", (1.0, 0.70, 0.30), 1.6)
curve_obj("n27", [trace(collatz(HIGHLIGHT))], 0.03, gold)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(0, 0, 0))
dot = bpy.context.active_object
dot.data.materials.append(gold)
bpy.ops.object.shade_smooth()

target = bpy.data.objects.new("Target", None)
target.location = (center.x, center.y, hi.z * 0.375)
target.rotation_euler[2] = 200 * 2 * math.pi / 300
col.objects.link(target)
cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
cam.data.lens = 20
cam.parent = target
cam.location = (size * 0.85, -size * 0.85, size * 0.12 + 1.5)
col.objects.link(cam)
tc = cam.constraints.new('TRACK_TO')
tc.target, tc.track_axis, tc.up_axis = target, 'TRACK_NEGATIVE_Z', 'UP_Y'
scene.camera = cam

r = scene.render
r.resolution_x, r.resolution_y, r.resolution_percentage = 3840, 2160, 100
r.image_settings.file_format = 'PNG'
r.image_settings.color_mode = 'RGBA'
try:
    scene.eevee.taa_render_samples = 128
except Exception:
    pass
outdir = os.path.join(os.path.expanduser("~"), "Documents", "Collatz")
os.makedirs(outdir, exist_ok=True)
r.filepath = os.path.join(outdir, "coral_transparent.png")
bpy.ops.render.render(write_still=True)
print("Saved", r.filepath)

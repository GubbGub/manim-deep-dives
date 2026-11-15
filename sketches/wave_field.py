"""
Wave field (Blender sketch).

~400 indigo pillars whose heights are driven by two interfering sine waves,
under a floating gold ring. Loops seamlessly over 240 frames.
Paste into Blender's Scripting workspace and press Alt+P.
"""
import bpy, bmesh, math

for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)

scene = bpy.context.scene
scene.frame_start, scene.frame_end = 1, 240
for eng in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
    try:
        scene.render.engine = eng
        break
    except Exception:
        pass
col = scene.collection

world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
world.node_tree.nodes.get("Background").inputs[0].default_value = (0.005, 0.008, 0.025, 1)


def mat(name, rgb, metal=0.2, rough=0.3, emit=None, strength=0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value = (*rgb, 1)
    p.inputs["Metallic"].default_value = metal
    p.inputs["Roughness"].default_value = rough
    if emit:
        p.inputs["Emission Color"].default_value = (*emit, 1)
        p.inputs["Emission Strength"].default_value = strength
    return m


palette = [(0.010, 0.020, 0.120), (0.015, 0.045, 0.220), (0.030, 0.090, 0.380),
           (0.080, 0.200, 0.550), (0.350, 0.550, 0.800), (0.850, 0.900, 0.950)]
mats = [mat("Indigo%d" % i, c) for i, c in enumerate(palette)]
gold = mat("KintsugiGold", (1.0, 0.62, 0.15), metal=1.0, rough=0.15,
           emit=(1.0, 0.55, 0.12), strength=4.0)

me = bpy.data.meshes.new("Pillar")
bm = bmesh.new()
bmesh.ops.create_cube(bm, size=1.0)
for v in bm.verts:
    v.co.z += 0.5           # origin at the base so pillars grow upward
bm.to_mesh(me)
bm.free()
me.materials.append(mats[0])

N, gap = 26, 0.42
w = 2 * math.pi * 5 / 240   # loops seamlessly over 240 frames
R = (N - 1) / 2 * gap
for i in range(N):
    for j in range(N):
        x, y = (i - (N - 1) / 2) * gap, (j - (N - 1) / 2) * gap
        d = math.hypot(x, y)
        if d > R:
            continue
        ob = bpy.data.objects.new("P_%d_%d" % (i, j), me)
        ob.location = (x, y, 0)
        ob.scale = (0.36, 0.36, 1)
        col.objects.link(ob)
        k = min(len(mats) - 1, int((1 - d / R) * len(mats)))
        ob.material_slots[0].link = "OBJECT"
        ob.material_slots[0].material = mats[k]
        ob.driver_add("scale", 2).driver.expression = (
            "1.4 + 0.9*sin(frame*%.5f - %.4f) + 0.35*sin(frame*%.5f - %.4f)"
            % (w, d * 1.15, 2 * w, (x + y) * 0.6))

bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
bpy.context.active_object.data.materials.append(mat("Floor", (0.004, 0.006, 0.02), metal=0.0, rough=0.15))

bpy.ops.mesh.primitive_torus_add(major_radius=1.3, minor_radius=0.07,
                                 major_segments=96, minor_segments=16, location=(0, 0, 4.6))
ring = bpy.context.active_object
ring.data.materials.append(gold)
bpy.ops.object.shade_smooth()
ring.driver_add("rotation_euler", 0).driver.expression = "0.5 + 0.25*sin(frame*%.5f)" % w
ring.driver_add("rotation_euler", 2).driver.expression = "frame*%.5f" % (w / 5)
ring.driver_add("location", 2).driver.expression = "4.6 + 0.25*sin(frame*%.5f)" % (2 * w / 5)

key = bpy.data.lights.new("Key", "AREA")
key.energy, key.size, key.color = 2500, 8, (0.75, 0.85, 1.0)
ko = bpy.data.objects.new("Key", key)
ko.location = (-6, -4, 10)
ko.rotation_euler = (math.radians(30), math.radians(-35), 0)
col.objects.link(ko)
glow = bpy.data.lights.new("GoldGlow", "POINT")
glow.energy, glow.color = 1500, (1.0, 0.6, 0.2)
go = bpy.data.objects.new("GoldGlow", glow)
go.parent = ring
col.objects.link(go)

target = bpy.data.objects.new("Target", None)
target.location = (0, 0, 1.6)
col.objects.link(target)
target.driver_add("rotation_euler", 2).driver.expression = "frame*%.5f" % (2 * math.pi / 240)
cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
cam.data.lens = 40
cam.parent = target
cam.location = (12, -12, 6.9)
col.objects.link(cam)
tc = cam.constraints.new("TRACK_TO")
tc.target, tc.track_axis, tc.up_axis = target, "TRACK_NEGATIVE_Z", "UP_Y"
scene.camera = cam

for scr in bpy.data.screens:
    for area in scr.areas:
        if area.type == "VIEW_3D":
            sp = area.spaces.active
            sp.shading.type = "RENDERED"
            sp.region_3d.view_perspective = "CAMERA"
            sp.overlay.show_overlays = False
scene.frame_set(1)

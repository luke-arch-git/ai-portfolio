import bpy
import sys
import math
import json
import argparse
import subprocess
from pathlib import Path
from mathutils import Vector
import imageio_ffmpeg

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "output"
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
parser = argparse.ArgumentParser()
parser.add_argument("--mode", choices=("checks", "hero", "views", "export", "animation-test", "animation"), required=True)
parser.add_argument("--start", type=int, default=0)
parser.add_argument("--end", type=int, default=120)
opt = parser.parse_args(args)
bpy.ops.wm.open_mainfile(filepath=str(OUT / "STARLING-01.blend"))
scene = bpy.context.scene
root = bpy.data.objects["STARLING-01 | MASTER • animated turntable"]
hero = bpy.data.objects["CAMERA • hero three-quarter"]
studio = bpy.data.collections["90 • Studio"]
ground = bpy.data.objects["Studio / seamless ground"]


def gpu():
    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type = "METAL"
    prefs.get_devices()
    for device in prefs.devices:
        device.use = device.type == "METAL"
    scene.cycles.device = "GPU"
    scene.cycles.use_denoising = True


def png(path, size, samples):
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.color_depth = "8"
    scene.render.resolution_x = size
    scene.render.resolution_y = size
    scene.render.resolution_percentage = 100
    scene.cycles.samples = samples
    scene.cycles.adaptive_threshold = 0.025 if samples >= 48 else 0.06
    scene.render.filepath = str(path)


def inspection_camera():
    obj = bpy.data.objects.get("CAMERA • inspection")
    if obj:
        return obj
    data = bpy.data.cameras.new("Inspection orthographic")
    obj = bpy.data.objects.new("CAMERA • inspection", data)
    studio.objects.link(obj)
    data.type = "ORTHO"
    data.lens = 70
    return obj


def aim(cam, loc, target, scale):
    cam.location = loc
    cam.rotation_euler = (Vector(target) - cam.location).to_track_quat("-Z", "Y").to_euler()
    cam.data.ortho_scale = scale


VIEWS = {
    "Front": ((0, -12, 2.60), (0, 0, 2.60), 5.85),
    "Side": ((12, 0, 2.60), (0, 0, 2.60), 5.85),
    "Back": ((0, 12, 2.60), (0, 0, 2.60), 5.85),
    "Top": ((0, 0, 12), (0, 0, 2.55), 4.05),
    "Bottom": ((0, 0, -10), (0, 0, 2.20), 4.05),
}

scene.frame_set(1)
if opt.mode in ("checks", "views"):
    gpu()
    scene.render.engine = "CYCLES"
    nt = scene.world.node_tree
    output = next(n for n in nt.nodes if n.type == "OUTPUT_WORLD")
    original_bg = next(n for n in nt.nodes if n.type == "BACKGROUND")
    light_path = nt.nodes.new("ShaderNodeLightPath")
    flat_bg = nt.nodes.new("ShaderNodeBackground")
    flat_bg.inputs["Color"].default_value = (0.62, 0.58, 0.52, 1)
    flat_bg.inputs["Strength"].default_value = 0.8
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(light_path.outputs["Is Camera Ray"], mix.inputs[0])
    nt.links.new(original_bg.outputs[0], mix.inputs[1])
    nt.links.new(flat_bg.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], output.inputs[0])
    cam = inspection_camera()
    scene.camera = cam
    size = 800 if opt.mode == "checks" else 1400
    samples = 24 if opt.mode == "checks" else 64
    for name, (loc, target, scale) in VIEWS.items():
        ground.hide_render = name == "Bottom"
        aim(cam, loc, target, scale)
        suffix = "check" if opt.mode == "checks" else "view"
        png(OUT / f"{name}_{suffix}.png", size, samples)
        bpy.ops.render.render(write_still=True)
        print("RENDERED", name, flush=True)
    ground.hide_render = False
    scene.camera = hero

elif opt.mode == "hero":
    gpu()
    scene.render.engine = "CYCLES"
    scene.camera = hero
    ground.hide_render = False
    png(OUT / "STARLING-01_Hero_2048.png", 2048, 112)
    scene.cycles.adaptive_threshold = 0.015
    bpy.ops.render.render(write_still=True)
    print("HERO_RENDERED", scene.render.filepath, flush=True)

elif opt.mode == "export":
    bpy.ops.object.select_all(action="DESELECT")
    asset_objects = []
    for coll in bpy.data.collections:
        if coll.name[:2] in ("00", "01", "02", "03", "04", "05", "06"):
            asset_objects.extend(coll.objects)
    for obj in asset_objects:
        obj.select_set(True)
    convertible = [o for o in asset_objects if o.type in {"MESH", "CURVE", "FONT", "SURFACE"}]
    bpy.ops.object.select_all(action="DESELECT")
    for obj in convertible:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = convertible[0]
    bpy.ops.object.convert(target="MESH")
    bpy.ops.object.select_all(action="DESELECT")
    for obj in asset_objects:
        if obj.name in bpy.data.objects:
            obj.select_set(True)
    bpy.context.view_layer.objects.active = root
    bpy.ops.export_scene.gltf(
        filepath=str(OUT / "STARLING-01.glb"),
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_materials="EXPORT",
        export_animations=False,
        export_cameras=False,
        export_lights=False,
        export_extras=True,
        export_yup=True,
    )
    report = {"file": "STARLING-01.glb", "bytes": (OUT / "STARLING-01.glb").stat().st_size}
    (OUT / "export_report.json").write_text(json.dumps(report, indent=2))
    print("GLB_EXPORTED", report, flush=True)

elif opt.mode in ("animation-test", "animation"):
    scene.camera = hero
    ground.hide_render = False
    scene.render.engine = "CYCLES"
    gpu()
    scene.cycles.samples = 24
    scene.cycles.adaptive_threshold = 0.06
    scene.render.resolution_x = 768
    scene.render.resolution_y = 768
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.color_depth = "8"
    scene.render.film_transparent = False
    frames_dir = OUT / "animation_frames"
    frames_dir.mkdir(exist_ok=True)
    if opt.mode == "animation-test":
        scene.frame_set(31)
        scene.render.filepath = str(OUT / "animation_test.png")
        bpy.ops.render.render(write_still=True)
        print("ANIMATION_TEST_RENDERED", flush=True)
    else:
        for index in range(opt.start, min(opt.end, 120)):
            scene.frame_set(1 + index * 2)
            scene.render.filepath = str(frames_dir / f"frame_{index:04d}.png")
            bpy.ops.render.render(write_still=True)
            print(f"ANIMATION_FRAME {index + 1}/120", flush=True)
        if opt.end >= 120:
            ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
            video = OUT / "STARLING-01_Turntable_10s.mp4"
            cmd = [
                ffmpeg, "-y", "-framerate", "12", "-i", str(frames_dir / "frame_%04d.png"),
                "-vf", "minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,tpad=stop_mode=clone:stop_duration=0.5",
                "-frames:v", "240", "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(video),
            ]
            subprocess.run(cmd, check=True)
            print("VIDEO_ENCODED", video, flush=True)

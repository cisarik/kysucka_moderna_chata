"""Explicit Blender batch render; writes only the chosen output and optional JSON."""
import bpy,sys,argparse,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--width',type=int,default=960);p.add_argument('--samples',type=int,default=32);p.add_argument('--clay',action='store_true');p.add_argument('--metadata')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
s=bpy.context.scene;s.render.resolution_x=a.width;s.render.resolution_y=round(a.width*3/4);s.render.resolution_percentage=100;s.cycles.samples=a.samples
s.render.filepath=str(Path(a.output).resolve());Path(s.render.filepath).parent.mkdir(parents=True,exist_ok=True)
# The validation host's Blender build omits OpenImageDenoise. Keep this route portable.
s.cycles.use_denoising=False
if a.clay:
    mat=bpy.data.materials.new('QA_clay_override');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.55,.60,.62,1);bs.inputs['Roughness'].default_value=.75
    bpy.context.view_layer.material_override=mat
bpy.ops.render.render(write_still=True)
if a.metadata:
    result={'blender':bpy.app.version_string,'file':bpy.data.filepath,'objects':len(s.objects),'camera':s.camera.name,'location':list(s.camera.location),'lens_mm':s.camera.data.lens,'resolution':[s.render.resolution_x,s.render.resolution_y],'samples':a.samples,'clay':a.clay,'missing_images':[im.name for im in bpy.data.images if im.source=='FILE' and not im.packed_file and im.filepath and not Path(bpy.path.abspath(im.filepath)).exists()],'handlers':{k:len(getattr(bpy.app.handlers,k)) for k in ['load_post','save_pre','render_pre']}}
    Path(a.metadata).write_text(json.dumps(result,indent=2))
print('RENDER_OK',s.render.filepath)

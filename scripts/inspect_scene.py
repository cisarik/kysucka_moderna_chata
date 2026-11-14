"""Read-only scene observation for the declared blender-local-v1 capability route.
Use Blender --background --disable-autoexec FILE --python THIS_SCRIPT.
No save, render, handlers, dependency installs, network, or file output.
"""
import bpy,json,math
s=bpy.context.scene;c=s.camera
print('KYSUCKA_SCENE_OBSERVATION_BEGIN')
print(json.dumps({
    'blender':bpy.app.version_string,'file':bpy.data.filepath,
    'unit_system':s.unit_settings.system,'unit_scale':s.unit_settings.scale_length,
    'seed_revision':s.get('seed_revision'),'reference_fit_status':s.get('reference_fit_status'),
    'objects':len(s.objects),'collections':[co.name for co in bpy.data.collections],
    'camera':None if not c else {'name':c.name,'location':list(c.location),'rotation_euler':list(c.rotation_euler),'lens_mm':c.data.lens,'sensor_width_mm':c.data.sensor_width,'shift_y':c.data.shift_y},
    'resolution':[s.render.resolution_x,s.render.resolution_y],
    'images':[{'name':im.name,'packed':bool(im.packed_file),'size':list(im.size)} for im in bpy.data.images if im.source=='FILE'],
    'automatic_handlers':{k:len(getattr(bpy.app.handlers,k)) for k in ['load_post','save_pre','render_pre']},
    'text_blocks':list(bpy.data.texts.keys()),
    'mesh_vertices':sum(len(o.data.vertices) for o in s.objects if o.type=='MESH')
},ensure_ascii=False,indent=2))
print('KYSUCKA_SCENE_OBSERVATION_END')

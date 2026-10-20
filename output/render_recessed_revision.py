"""Render the revised shell: two 2000px details plus four 1800px exterior views."""
import bpy,os,subprocess,json,time
OUT=os.path.dirname(os.path.abspath(__file__));s=bpy.context.scene
s.render.engine='CYCLES';s.cycles.use_denoising=False;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
report={'revision':3,'started_unix':time.time(),'views':[]}
for name in ['05_closeup_glass_junction','06_closeup_glass_grazing','01_front_hero','02_aerial','03_right_oblique','04_soffit']:
 close=name.startswith(('05','06'));s.camera=bpy.data.objects[name];size=2000 if close else 1800
 s.render.resolution_x=size;s.render.resolution_y=size;s.cycles.samples=96 if close else 64;s.cycles.adaptive_threshold=.035 if close else .065;s.cycles.adaptive_min_samples=24 if close else 16
 s.render.filepath=OUT+'/renders/'+name+'.png';started=time.time();bpy.ops.render.render(write_still=True)
 subprocess.run(['python',OUT+'/denoise.py',s.render.filepath],check=True)
 report['views'].append({'name':name,'width':size,'height':size,'samples_cap':s.cycles.samples,'seconds':time.time()-started})
 with open(OUT+'/render_revision_report.json','w') as f:json.dump(report,f,indent=2)
 print('VIEW_COMPLETE',name,flush=True)
print('RECESSED_ALL_SIX_COMPLETE',flush=True)

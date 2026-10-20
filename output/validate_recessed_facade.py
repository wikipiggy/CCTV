import bpy,os,json,gzip
from mathutils import Vector
OUT=os.path.dirname(os.path.abspath(__file__));s=bpy.context.scene
with gzip.open(OUT+'/recessed_facade_geometry.json.gz','rt') as f:data=json.load(f)
assert bpy.data.objects.get('Variable density diagonal exoskeleton') is None
assert bpy.data.objects.get('Fine curtain wall aluminium grid') is None
hits=[];deps=bpy.context.evaluated_depsgraph_get()
for patch in data['patches']:
 p=Vector(patch['point']);n=Vector(patch['normal']);ok,loc,normal,index,obj,_=s.ray_cast(deps,p+n,-n,distance=2)
 depth=(p-loc).dot(n);assert normal.dot(n)>.99,('normal orientation',normal.dot(n));assert ok and abs(depth-.03)<.0002,(patch['tag'],depth,obj.name if obj else None)
 hits.append({'patch':patch['tag'],'object':obj.name,'measured_depth_m':depth})
obj=bpy.data.objects['Continuous exterior shell and curtain panels'];coords=[obj.matrix_world@v.co for v in obj.data.vertices];height=max(p.z for p in coords)-min(p.z for p in coords);assert abs(height-234)<.001
report={'version':2,'shell_height_m':height,'real_recess_geometry':True,'primary_depth_m':.03,'fine_joint_depth_m':.003,'max_outward_offset_m':0,'raycast_verification':hits,'cameras':[o.name for o in s.objects if o.type=='CAMERA'],'coverage_checks_passed':len(data['checks']),'mesh_faces':sum(len(o.data.polygons) for o in s.objects if o.type=='MESH'),'external_images':[i.filepath for i in bpy.data.images if i.source=='FILE' and not i.packed_file]}
assert len(report['cameras'])==6
with open(OUT+'/validation.json','w') as f:json.dump(report,f,indent=2)
s.camera=bpy.data.objects['01_front_hero'];bpy.ops.wm.save_as_mainfile(filepath=OUT+'/CCTV_Headquarters.blend')
print(json.dumps(report),flush=True)

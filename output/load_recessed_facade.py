"""Install precomputed recessed shell in a new or existing Blender scene."""
import bpy,gzip,json,os
from mathutils import Vector
OUT=os.path.dirname(os.path.abspath(__file__))
def load_recessed_facade():
 with gzip.open(OUT+'/recessed_facade_geometry.json.gz','rt') as f:data=json.load(f)
 old=['Continuous exterior shell and curtain panels','Fine curtain wall aluminium grid','Variable density diagonal exoskeleton','Facade perimeter flashing',*data['meshes'].keys()]
 for name in old:
  obj=bpy.data.objects.get(name)
  if obj:bpy.data.objects.remove(obj,do_unlink=True)
 fine=bpy.data.materials.get('Flush joint gasket') or bpy.data.materials.new('Flush joint gasket');fine.use_nodes=True;n=fine.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(.025,.032,.038,1);n.inputs['Roughness'].default_value=.55
 mats=[bpy.data.materials['Silver blue curtain glass %02d'%i] for i in range(16)]+[bpy.data.materials['Standing seam titanium roof'],bpy.data.materials['Graphite diagonal cladding'],bpy.data.materials['Anodized aluminium mullions'],fine]
 coll=bpy.data.collections.get('01_CCTV_Exterior')
 if coll is None:
  coll=bpy.data.collections.new('01_CCTV_Exterior');bpy.context.scene.collection.children.link(coll)
 for name,m in data['meshes'].items():
  me=bpy.data.meshes.new(name);me.from_pydata(m['vertices'],[],m['faces']);me.update()
  ob=bpy.data.objects.new('Continuous exterior shell and curtain panels' if name=='Curtain glass and shell' else name,me);coll.objects.link(ob)
  for mat in mats:me.materials.append(mat)
  for poly,idx in zip(me.polygons,m['material_indices']):poly.material_index=idx
  ob['Facade datum']='Glass exterior = 0 m; channel floor = -0.030 m; panel joints = -0.003 m'
  ob['Max outward offset metres']=0.0
 bpy.context.scene['Facade revision']='v2: unioned recessed diagonal channels, no external diagonal rods'
 return data

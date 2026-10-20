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
 channel=bpy.data.materials.get('Diagonal channels | matte dark grey') or bpy.data.materials.new('Diagonal channels | matte dark grey')
 channel.use_nodes=True;channel.diffuse_color=(.065,.065,.065,1)
 cn=channel.node_tree.nodes.get('Principled BSDF');cn.inputs['Base Color'].default_value=(.065,.065,.065,1);cn.inputs['Metallic'].default_value=0;cn.inputs['Roughness'].default_value=1;cn.inputs['Specular IOR Level'].default_value=0;cn.inputs['Coat Weight'].default_value=0
 channel['Finish']='Opaque matte dark-grey coated metal appearance; no specular or coat lobe'
 coll=bpy.data.collections.get('01_CCTV_Exterior')
 if coll is None:
  coll=bpy.data.collections.new('01_CCTV_Exterior');bpy.context.scene.collection.children.link(coll)
 for name,m in data['meshes'].items():
  me=bpy.data.meshes.new(name);me.from_pydata(m['vertices'],[],m['faces']);me.update()
  ob=bpy.data.objects.new('Continuous exterior shell and curtain panels' if name=='Curtain glass and shell' else name,me);coll.objects.link(ob)
  is_channel=name in ['Recessed diagonal channel floors','Recessed diagonal channel walls','Diagonal channel bevels']
  for mat in ([channel] if is_channel else mats):me.materials.append(mat)
  for poly,idx in zip(me.polygons,m['material_indices']):poly.material_index=0 if is_channel else idx
  ob['Facade datum']='Glass exterior = 0 m; channel floor = -0.200 m; panel joints = -0.003 m'
  ob['Max outward offset metres']=0.0
 bpy.context.scene['Facade revision']='v3: 200mm, matte grey; unioned recessed diagonal channels, no external diagonal rods'
 return data

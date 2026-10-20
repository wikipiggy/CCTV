"""CCTV exterior study. Blender 4.3+: blender -b -t 5 --python build_cctv.py -- --stage final
Metres; X east, Y north. Reference-derived reconstruction, not survey geometry.
"""
import bpy, math, random, os, sys, argparse, json, gzip
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--stage',default='final',choices=['massing','final']);p.add_argument('--samples',type=int,default=64);p.add_argument('--preview',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
OUT=os.path.dirname(os.path.abspath(__file__));random.seed(57)
for folder in ('progress','renders'):os.makedirs(os.path.join(OUT,folder),exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for data in list(bpy.data.materials): bpy.data.materials.remove(data)
s=bpy.context.scene;s.unit_settings.system='METRIC';s.render.engine='CYCLES';s.cycles.samples=a.samples;s.cycles.use_denoising=False;s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.065;s.cycles.adaptive_min_samples=16;s.cycles.max_bounces=6;s.cycles.diffuse_bounces=2;s.cycles.glossy_bounces=3;s.render.threads_mode='FIXED';s.render.threads=5
s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.exposure=-.65
def mat(name,c,metal=0,rough=.4):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True;n=m.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(*c,1);n.inputs['Metallic'].default_value=metal;n.inputs['Roughness'].default_value=rough;return m
steel=mat('Graphite diagonal cladding',(.035,.045,.055),.35,.36);frame=mat('Anodized aluminium mullions',(.22,.25,.28),.45,.34)
roof=mat('Standing seam titanium roof',(.24,.29,.32),.65,.4);stone=mat('Pale granite paving',(.49,.48,.43),0,.75);asphalt=mat('Asphalt',(.055,.063,.072),0,.88);white=mat('Traffic paint',(.77,.77,.69),0,.65);grass=mat('Lawns',(.09,.18,.065),0,.9);bark=mat('Tree bark',(.13,.085,.045));leaf=mat('Tree canopy',(.07,.17,.055),0,.85);concrete=mat('Urban stone',(.27,.29,.3),.05,.7)
glass=[]
for i in range(16):
 m=mat('Silver blue curtain glass %02d'%i,(.055+i*.0015,.085+i*.0015,.105+i*.0015),.48,.19+i*.002);m.node_tree.nodes.get('Principled BSDF').inputs['IOR'].default_value=1.46;glass.append(m)
def mesh(name,v,f,mats,ids=None):
 me=bpy.data.meshes.new(name);me.from_pydata(v,[],f);me.update();ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob)
 for m in mats:me.materials.append(m)
 if ids:
  for po,idx in zip(me.polygons,ids):po.material_index=idx
 return ob
def cube(name,loc,scale,m):
 x,y,z=[v/2 for v in scale]
 o=mesh(name,[(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],[m]);o.location=loc;return o
class Beams:
 def __init__(self):self.v=[];self.f=[]
 def add(self,a,b,w,depth=None):
  a,b=Vector(a),Vector(b);d=b-a
  if d.length<.01:return
  d.normalize();u=d.cross(Vector((0,0,1)))
  if u.length<.01:u=d.cross(Vector((0,1,0)))
  u.normalize();v=d.cross(u).normalized();u*=w/2;v*=(depth or w)/2;k=len(self.v)
  self.v += [tuple(q+u*su+v*sv) for q in (a,b) for su,sv in [(-1,-1),(1,-1),(1,1),(-1,1)]]
  self.f += [tuple(k+j for j in f) for f in [(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]]
 def finish(self,name,m):return mesh(name,self.v,self.f,[m])
# Plan lattice: NW tower, SE tower; opposite L-shaped upper and lower links.
xs=[-76,-32,32,76];ys=xs[:];levels=[0,46.45,161,234]
occ=[{(i,j) for i in range(3) for j in range(3) if j==2 or i==2},{(0,2),(2,0)},{(i,j) for i in range(3) for j in range(3) if i==0 or j==0}]
def world(x,y,z):
 # Each tower tilts along both horizontal axes; resultant nominal slope ~6 degrees.
 return Vector((x*(1-.32*z/234),y*(1-.32*z/234), z if z<233 else 234-(x+76)/152*20.1))
faces=[]
for k,cells in enumerate(occ):
 for i,j in sorted(cells):
  x0,x1=xs[i:i+2];y0,y1=ys[j:j+2];z0,z1=levels[k:k+2]
  side=[((-1,0),[(x0,y1,z0),(x0,y0,z0),(x0,y0,z1),(x0,y1,z1)]),((1,0),[(x1,y0,z0),(x1,y1,z0),(x1,y1,z1),(x1,y0,z1)]),((0,-1),[(x0,y0,z0),(x1,y0,z0),(x1,y0,z1),(x0,y0,z1)]),((0,1),[(x1,y1,z0),(x0,y1,z0),(x0,y1,z1),(x1,y1,z1)])]
  for (di,dj),pts in side:
   if (i+di,j+dj) not in cells:faces.append(([world(*q) for q in pts],'wall'))
  if k==0 or (i,j) not in occ[k-1]:faces.append(([world(x0,y0,z0),world(x0,y1,z0),world(x1,y1,z0),world(x1,y0,z0)],'soffit'))
  if k==2 or (i,j) not in occ[k+1]:faces.append(([world(x0,y0,z1),world(x1,y0,z1),world(x1,y1,z1),world(x0,y1,z1)],'roof'))
# v2 exterior: real cut glass, merged recessed channels, no external facade rods.
if a.stage=='final':
 sys.path.insert(0,OUT)
 from load_recessed_facade import load_recessed_facade
 load_recessed_facade()
else:
 V=[];F=[];IDs=[]
 for q,kind in faces:
  base=len(V);V+=q;F.append(tuple(range(base,base+4)));IDs.append(16 if kind=='roof' else 6)
 mesh('Continuous exterior shell and curtain panels',V,F,glass+[roof],IDs)
# Site and road system, flat Beijing urban terrain.
cube('Urban ground',(0,0,-1.5),(1800,1800,2),concrete);cube('Site plinth',(0,0,-.2),(270,290,1.1),stone)
for x in [-170,165]:
 cube('North south carriageway',(x,0,-.35),(38,1200,.22),asphalt)
 for dx in [-18,18]:cube('Road sidewalk',(x+dx,0,-.13),(3,1200,.25),stone)
 for dx in [-9,0,9]:
  for y in range(-580,580,14):cube('Dashed lane marking',(x+dx,y,-.22),(.14,6,.015),white)
for y in [-180,180,440]:
 cube('East west carriageway',(0,y,-.325),(1200,30,.2),asphalt)
 for dy in [-7,7]:
  for x in range(-580,580,14):cube('Road paint',(x,y+dy,-.23),(6,.14,.012),white)
if a.stage=='final':
 for y in [-157,-145,145,157]:
  for x in range(-126,127,18):cube('Landscape planting bed',(x,y,.25),(13,6,.3),grass)
 for x,y,w,h in [(-106,-54,28,80),(12,108,65,22),(85,-108,60,20),(-90,-113,55,24),(110,45,18,90)]:
  cube('Geometric lawn',(x,y,.42),(w,h,.2),grass)
 # Angular paths form an urban landscaped platform.
 for x,y,ang in [(-92,-90,.45),(0,-120,-.38),(80,95,.5)]:
  o=cube('Diagonal granite promenade',(x,y,.6),(80,5,.22),stone);o.rotation_euler.z=ang
 for k in range(8):cube('Plaza stair',(0,-142-k*1.1,.45-k*.055),(95,1.1,.15),stone)
 # Efficient linked tree crowns.
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1);proto=bpy.context.object;proto.name='Canopy prototype';proto.data.materials.append(leaf);proto.hide_render=True;proto.hide_viewport=True
 for poly in proto.data.polygons:poly.use_smooth=True
 for idx in range(120):
  if idx<72:x=random.choice([-137,137])+random.uniform(-3,3);y=random.uniform(-145,145)
  else:x=random.uniform(-126,126);y=random.choice([-150,150])+random.uniform(-4,4)
  h=random.uniform(5,9);cube('Tree trunk',(x,y,h/2),(.4,.4,h),bark)
  o=bpy.data.objects.new('Street tree crown',proto.data);bpy.context.collection.objects.link(o);o.location=(x,y,h);o.scale=(3.5,3.5,4)
 # Context city: deliberately secondary, not surveyed replicas.
 for i in range(85):
  x=random.uniform(-650,650);y=random.uniform(-600,650)
  if (abs(x)<280 and -500<y<500) or (y<0 and abs(x)<450):continue
  h=random.uniform(20,115);w=random.uniform(18,42);d=random.uniform(18,45)
  cube('Context city building',(x,y,h/2),(w,d,h),random.choice([concrete,glass[3],glass[10]]))
  for z in range(4,int(h),5):cube('Context spandrel',(x,y,z),(w+.1,d+.1,.22),frame)
 # TVCC contextual angular mass north of CCTV.
 tv=cube('TVCC contextual volume',(-42,310,65),(60,47,130),concrete);tv.rotation_euler.y=-.10
 cube('TVCC podium',(-25,305,12),(140,65,24),glass[5])
 # Antenna dishes on lower link roof, separate exterior detail.
 for x in range(-18,65,14):
  y=49;z=46.9;cube('Dish pedestal',(x,y,z+1),(1,1,2),frame)
  bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,radius=2.6,location=(x,y,z+3));o=bpy.context.object;o.name='Satellite dish';o.scale=(1,.22,1);o.rotation_euler.x=.45;o.data.materials.append(white)
 # Circular dark soffit observation apertures.
 for x,y in [(-44,-45),(-26,-46),(-44,-25),(-43,0)]:
  bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=2.0,depth=.12,location=(x*.835,y*.835,160.88));bpy.context.object.name='Soffit circular aperture trim';bpy.context.object.data.materials.append(steel)
 # Rooftop helipad and steel support, kept within 237.5m reference envelope.
 cx,cy=-45,44
 support=Beams()
 for dx in [-6,6]:
  for dy in [-5,5]:
   support.add((cx+dx,cy+dy,228.5),(cx-dx,cy-dy,237.05),.42)
 support.finish('Rooftop platform support truss',steel)
 bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=10,depth=.35,location=(cx,cy,237.25));bpy.context.object.name='Rooftop maintenance platform';bpy.context.object.data.materials.append(roof)
if a.stage=='final':
 exec(compile(open(os.path.join(OUT,'urban_details.py')).read(),'urban_details.py','exec'))
# Physical daylight; procedural sky is packed in blend without external textures.
w=bpy.data.worlds.new('Beijing daylight');s.world=w;w.use_nodes=True;nt=w.node_tree;nt.nodes.clear();sky=nt.nodes.new('ShaderNodeTexSky');sky.sky_type='NISHITA';sky.sun_disc=False;sky.sun_elevation=math.radians(38);sky.sun_rotation=math.radians(225);sky.altitude=.05;sky.air_density=1.1;sky.dust_density=.3
bg=nt.nodes.new('ShaderNodeBackground');bg.inputs['Strength'].default_value=.3;nt.links.new(sky.outputs[0],bg.inputs[0]);wo=nt.nodes.new('ShaderNodeOutputWorld');nt.links.new(bg.outputs[0],wo.inputs[0])
bpy.ops.object.light_add(type='SUN',location=(0,0,500));sun=bpy.context.object;sun.rotation_euler=(.55,-.55,0);sun.data.energy=1.6;sun.data.angle=.06
bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam;cam.data.clip_end=5000;cam.data.lens=48
views=[('01_front_hero',(-340,-390,150),(0,0,111),48),('02_aerial',(-340,-380,340),(0,0,91),45),('03_right_oblique',(-165,-490,115),(0,0,115),48),('04_soffit',(-85,-100,5),(-10,-10,165),20)]
if a.stage=='final':
 with gzip.open(OUT+'/recessed_facade_geometry.json.gz','rt') as f:patchdata=json.load(f)['patches']
 for patch,name in zip(patchdata,['05_closeup_glass_junction','06_closeup_glass_grazing']):
  center=Vector(patch['point']);normal=Vector(patch['normal']);t=Vector(patch['tangent']);up=Vector(patch['up']);loc=center+normal*8+up if name.startswith('05') else center+normal*4+t*6+up*.5
  views.append((name,tuple(loc),tuple(center),60))
if a.stage=='massing':views=[('massing_perspective',(-340,-390,160),(0,0,115),48),('massing_north',(0,-500,117),(0,0,117),50),('massing_top',(0,0,600),(0,0,0),50)]
cameras={}
for name,pos,target,lens in views:
 data=bpy.data.cameras.new(name);ob=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(ob);ob.location=pos;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler();data.lens=lens;data.clip_end=5000;cameras[name]=ob
bpy.data.objects.remove(cam,do_unlink=True)
s.render.resolution_percentage=100
for name,pos,target,lens in views:
 cam=cameras[name];s.camera=cam
 cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens
 cam.data.type='ORTHO' if name.startswith('massing_') and name!='massing_perspective' else 'PERSP';cam.data.ortho_scale=290
 close=name.startswith(('05','06'))
 s.render.resolution_x=1000 if a.stage=='massing' else (2000 if close else 1800);s.render.resolution_y=s.render.resolution_x
 s.cycles.samples=max(96,a.samples) if close else a.samples;s.cycles.adaptive_threshold=.035 if close else .065;s.cycles.adaptive_min_samples=24 if close else 16
 s.render.filepath=os.path.join(OUT,'progress' if a.stage=='massing' else 'renders',name+'.png')
 if name==views[0][0]:bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'cctv_massing.blend' if a.stage=='massing' else 'CCTV_Headquarters.blend'))
 if a.preview:s.render.resolution_percentage=50
 bpy.ops.render.render(write_still=True)
 if a.preview:break
print('COMPLETED',a.stage,flush=True)

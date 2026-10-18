# Executed by build_cctv.py, all assets are constructed locally.
carpaints=[mat('Vehicle pearl',(.5,.53,.55),.65,.22),mat('Vehicle charcoal',(.025,.03,.04),.65,.25),mat('Vehicle red',(.3,.018,.014),.5,.22),mat('Taxi ochre',(.42,.23,.035),.5,.26)]
tyre=mat('Rubber',(.012,.014,.016),0,.8);window=mat('Vehicle tinted windows',(.015,.027,.035),.45,.13)
for k in range(38):
 x=random.choice([-179,-169,-159,157,166,175]);y=random.uniform(-400,390)
 cube('Car body',(x,y,.65),(1.9,4.5,.8),random.choice(carpaints));cube('Car glazing',(x,y+.1,1.22),(1.7,2.3,.65),window)
 for dx in [-.95,.95]:
  for dy in [-1.35,1.35]:
   bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=.37,depth=.22,location=(x+dx,y+dy,.42),rotation=(0,math.pi/2,0));bpy.context.object.name='Vehicle wheel';bpy.context.object.data.materials.append(tyre)
 for dx in [-.57,.57]:cube('Vehicle headlamp',(x+dx,y-2.26,.72),(.42,.03,.22),white)
lamps=Beams()
for x in [-146,145]:
 for y in range(-270,431,35):
  lamps.add((x,y,0),(x,y,11),.16);lamps.add((x,y,11),(x+(4 if x<0 else -4),y,11.7),.14)
  cube('Streetlight head',(x+(4 if x<0 else -4),y,11.7),(1.3,.45,.18),frame)
lamps.finish('Streetlight poles',frame)
rail=Beams()
for x in [-149,148]:
 rail.add((x,-285,1.1),(x,430,1.1),.07)
 for y in range(-285,431,3):rail.add((x,y,0),(x,y,1.1),.06)
rail.finish('Road safety railing',frame)
for x in [-169,165]:
 for j in range(8):cube('Pedestrian crossing',(x-13+j*3.3,-148,-.20),(1.7,6,.025),white)

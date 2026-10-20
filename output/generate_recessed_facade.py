"""Generate real recessed curtain-wall geometry with planar polygon unions.
Run with host Python: python -m pip install shapely; python generate_recessed_facade.py
All diagonal intersections are united BEFORE glass is cut. Depths are visual estimates.
"""
import sys, os, math, json, gzip, random
sys.path.insert(0,'/workspace/library-files/facade')
import shapely
from shapely.geometry import Polygon, LineString, box
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles, orient_polygons
OUT=os.path.dirname(os.path.abspath(__file__));random.seed(57)
def sub(a,b):return [x-y for x,y in zip(a,b)]
def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def length(a):return math.sqrt(sum(x*x for x in a))
def world(x,y,z):return [x*(1-.32*z/234),y*(1-.32*z/234),z if z<233 else 234-(x+76)/152*20.1]
xs=[-76,-32,32,76];ys=xs[:];levels=[0,46.45,161,234]
occ=[{(i,j) for i in range(3) for j in range(3) if j==2 or i==2},{(0,2),(2,0)},{(i,j) for i in range(3) for j in range(3) if i==0 or j==0}]
facades=[]
for k,cells in enumerate(occ):
 for i,j in sorted(cells):
  x0,x1=xs[i:i+2];y0,y1=ys[j:j+2];z0,z1=levels[k:k+2]
  sides=[((-1,0),[(x0,y1,z0),(x0,y0,z0),(x0,y0,z1),(x0,y1,z1)]),((1,0),[(x1,y0,z0),(x1,y1,z0),(x1,y1,z1),(x1,y0,z1)]),((0,-1),[(x0,y0,z0),(x1,y0,z0),(x1,y0,z1),(x0,y0,z1)]),((0,1),[(x1,y1,z0),(x0,y1,z0),(x0,y1,z1),(x1,y1,z1)])]
  for direction,q in sides:
   if (i+direction[0],j+direction[1]) not in cells:facades.append((list(map(lambda p:world(*p),q)),'wall',[k,i,j,*direction]))
  if k==0 or (i,j) not in occ[k-1]:facades.append(([world(x0,y0,z0),world(x0,y1,z0),world(x1,y1,z0),world(x1,y0,z0)],'soffit',[k,i,j,0,0]))
  if k==2 or (i,j) not in occ[k+1]:facades.append(([world(x0,y0,z1),world(x1,y0,z1),world(x1,y1,z1),world(x0,y1,z1)],'roof',[k,i,j,0,0]))
class Mesh:
 def __init__(self):self.v=[];self.f=[];self.ids=[]
 def poly(self,pts,idx):
  start=len(self.v);self.v.extend(pts);self.f.append(list(range(start,len(self.v))));self.ids.append(idx)
 def data(self):return {'vertices':self.v,'faces':self.f,'material_indices':self.ids}
meshes={name:Mesh() for name in ['Curtain glass and shell','Recessed diagonal channel floors','Recessed diagonal channel walls','Diagonal channel bevels','Flush curtain panel joints']}
checks=[];patches=[]
def polygons(geom):
 if geom.is_empty:return []
 if geom.geom_type=='Polygon':return [geom]
 return [p for g in geom.geoms for p in polygons(g)]
for fi,(q,kind,tag) in enumerate(facades):
 A,B,C,D=q;U=length(sub(B,A));H=length(sub(D,A));normal=cross(sub(B,A),sub(D,A));nn=length(normal);normal=[x/nn for x in normal];rect=box(0,0,U,H)
 def pt(x,y,z=0):
  u=x/U;v=y/H
  return [A[t]*(1-u)*(1-v)+B[t]*u*(1-v)+C[t]*u*v+D[t]*(1-u)*v+normal[t]*z for t in range(3)]
 def surface(geom,target,idx,z):
  total=0
  for poly in polygons(geom):
   if poly.area<1e-9:continue
   triangles=constrained_delaunay_triangles(poly)
   for tri in triangles.geoms:
    pts=list(tri.exterior.coords)[:-1]
    if not tri.exterior.is_ccw:pts.reverse()
    meshes[target].poly([pt(x,y,z(x,y) if callable(z) else z) for x,y in pts],idx);total+=tri.area
  assert abs(total-geom.area)<max(1e-5,geom.area*1e-7),(fi,target,total,geom.area)
 def walls(geom,target,idx,top,bottom):
  for poly in polygons(orient_polygons(geom,exterior_cw=False)):
   for ring in [poly.exterior,*poly.interiors]:
    coords=list(ring.coords)
    for (x0,y0),(x1,y1) in zip(coords,coords[1:]):
     if length([x1-x0,y1-y0])<1e-7:continue
     # On the facade boundary, the adjoining facade owns the closure.
     if (x0<1e-7 and x1<1e-7) or (x0>U-1e-7 and x1>U-1e-7) or (y0<1e-7 and y1<1e-7) or (y0>H-1e-7 and y1>H-1e-7):continue
     meshes[target].poly([pt(x0,y0,top),pt(x1,y1,top),pt(x1,y1,bottom),pt(x0,y0,bottom)],idx)
 if kind=='roof' or (kind=='soffit' and max(p[2] for p in q)<1):
  meshes['Curtain glass and shell'].poly(q,16 if kind=='roof' else 17);continue
 lines=[];step=18
 for slope in [-1.32,1.32]:
  for index in range(-60,65):
   b=index*step;line=LineString([(0,b),(U,slope*U+b)]).intersection(rect)
   if not line.is_empty:lines.append(line.buffer(.30,cap_style=2,join_style=2))
  for index in range(-40,50):
   b=(index+.5)*step
   # Secondary channels finish at existing primary crossings, never as free rod ends.
   candidates=sorted((other*step-b)/(2*slope) for other in range(-80,80))
   candidates=[x for x in candidates if U*.22<=x<=U*.78 and 0<=slope*x+b<=H]
   if len(candidates)<2:continue
   line=LineString([(candidates[0],slope*candidates[0]+b),(candidates[-1],slope*candidates[-1]+b)]).intersection(rect)
   if not line.is_empty:lines.append(line.buffer(.125,cap_style=2,join_style=2))
 G=unary_union(lines).intersection(rect);inner=G.buffer(-.008,join_style=2).intersection(rect);bevel=G.difference(inner)
 surface(inner,'Recessed diagonal channel floors',17,-.030)
 surface(bevel,'Diagonal channel bevels',18,lambda x,y:-min(.006,G.boundary.distance(shapely.Point(x,y))*.75))
 walls(inner,'Recessed diagonal channel walls',17,-.006,-.030)
 # Fine mullion lines are cut 3mm into the same datum instead of laid on top.
 fine=[];nu=max(1,round(U/1.65));nv=max(1,round(H/3.8))
 if kind=='wall':
  for u in range(1,nu):fine.append(box(u*U/nu-.0175,0,u*U/nu+.0175,H))
  for v in range(1,nv):fine.append(box(0,v*H/nv-.0175,U,v*H/nv+.0175))
 F=unary_union(fine).difference(G) if fine else Polygon()
 surface(F,'Flush curtain panel joints',19,-.003)
 walls(F,'Flush curtain panel joints',19,0,-.003)
 area=0
 if kind=='wall':
  for u in range(nu):
   for v in range(nv):
    lo=u*U/nu+(.0175 if u else 0);hi=(u+1)*U/nu-(.0175 if u<nu-1 else 0)
    bot=v*H/nv+(.0175 if v else 0);top=(v+1)*H/nv-(.0175 if v<nv-1 else 0)
    panel=box(lo,bot,hi,top).difference(G);area+=panel.area;surface(panel,'Curtain glass and shell',random.randrange(16),0)
 else:
  panel=rect.difference(G);area=panel.area;surface(panel,'Curtain glass and shell',17,0)
 assert abs(area+F.area+G.area-rect.area)<.0001,(fi,'coverage',area+F.area+G.area,rect.area)
 checks.append({'face':fi,'tag':tag,'glass_area':area,'channel_area':G.area,'fine_joint_area':F.area,'domain_area':rect.area,'depth_m':.030})
 if tag in [[1,0,2,-1,0],[1,2,0,0,-1]]:
  x=54/2.64;y=1.32*x+18
  patches.append({'tag':tag,'point':pt(x,y),'normal':normal,'tangent':[(B[t]-A[t])/U for t in range(3)],'up':[(D[t]-A[t])/H for t in range(3)]})
 print('face',fi,kind,flush=True)
result={'version':2,'depth_m':.030,'bevel_m':.008,'max_outward_offset_m':0,'meshes':{k:v.data() for k,v in meshes.items()},'checks':checks,'patches':patches}
with gzip.open(OUT+'/recessed_facade_geometry.json.gz','wt') as f:json.dump(result,f,separators=(',',':'))
with open(OUT+'/recessed_facade_validation.json','w') as f:json.dump({k:v for k,v in result.items() if k!='meshes'},f,indent=2)
print('COMPLETE',sum(len(m.f) for m in meshes.values()),'polygons',flush=True)

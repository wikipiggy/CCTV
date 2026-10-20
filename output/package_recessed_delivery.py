"""Verify all six new renders, then create the downloadable v2 bundle."""
from pathlib import Path
import json,zipfile,hashlib,sys,ast
sys.path.insert(0,'/workspace/library-files/oidn')
from PIL import Image
out=Path(__file__).resolve().parent
report=json.loads((out/'render_revision_report.json').read_text());assert len(report['views'])==6
for v in report['views']:
 for suffix in ['', '_denoised']:
  p=out/'renders'/(v['name']+suffix+'.png')
  assert p.stat().st_mtime>=report['started_unix']
  with Image.open(p) as im:assert im.size==(v['width'],v['height']);im.verify()
validation=json.loads((out/'validation.json').read_text());assert validation['real_recess_geometry'];assert len(validation['cameras'])==6
files=[out/n for n in ['CCTV_Headquarters.blend','build_cctv.py','urban_details.py','load_recessed_facade.py','generate_recessed_facade.py','recessed_facade_geometry.json.gz','denoise.py','requirements-render.txt','requirements-geometry.txt','README_zh.md','validation.json','recessed_facade_validation.json','render_revision_report.json','render_recessed_revision.py','validate_recessed_facade.py','package_recessed_delivery.py']]
files += [out/'renders'/(v['name']+'_denoised.png') for v in report['views']]
for f in files:
 if f.suffix=='.py':ast.parse(f.read_text())
manifest={str(f.relative_to(out)):{'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in files}
(out/'manifest.json').write_text(json.dumps(manifest,indent=2))
with zipfile.ZipFile(out/'CCTV_download.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for f in files+[out/'manifest.json']:z.write(f,f.relative_to(out))
with zipfile.ZipFile(out/'CCTV_download.zip') as z:assert z.testzip() is None
print(json.dumps({'revision':2,'rendered_views':len(report['views']),'closeups':[v['name'] for v in report['views'] if v['width']==2000],'zip_bytes':(out/'CCTV_download.zip').stat().st_size,'files':len(files)+1},indent=2))

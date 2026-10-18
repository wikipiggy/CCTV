"""Optional OIDN CPU denoising. Keeps original PNG; writes *_denoised.png.
python -m pip install -r requirements-render.txt
python denoise.py renders/*.png
"""
import sys,os,ctypes
sys.path.insert(0,'/workspace/library-files/oidn')
import numpy as np
from PIL import Image
import oidn
# Parameters use the same loaded OIDN shared library as the public wrapper.
lib=ctypes.CDLL(os.path.join(os.path.dirname(oidn.__file__),'lib.linux.x64','libOpenImageDenoise.so.1.4.3'))
setbool=lib.oidnSetFilter1b;setbool.argtypes=[ctypes.c_void_p,ctypes.c_char_p,ctypes.c_bool]
dev=oidn.NewDevice();oidn.CommitDevice(dev)
for path in sys.argv[1:]:
 if '_denoised' in path:continue
 arr=np.ascontiguousarray(np.asarray(Image.open(path).convert('RGB'),dtype=np.float32)/255);out=np.empty_like(arr);h,w=arr.shape[:2]
 filt=oidn.NewFilter(dev,'RT');oidn.SetSharedFilterImage(filt,'color',arr,oidn.FORMAT_FLOAT3,w,h);oidn.SetSharedFilterImage(filt,'output',out,oidn.FORMAT_FLOAT3,w,h);setbool(filt,b'srgb',True);oidn.CommitFilter(filt);oidn.ExecuteFilter(filt)
 err=oidn.GetDeviceError(dev)
 if err:raise RuntimeError('OIDN error '+str(err))
 dest=os.path.splitext(path)[0]+'_denoised.png';Image.fromarray((np.clip(out,0,1)*255+.5).astype('uint8')).save(dest);print(dest,flush=True);oidn.ReleaseFilter(filt)
oidn.ReleaseDevice(dev)

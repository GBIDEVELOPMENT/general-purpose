from pathlib import Path
import sys, math, json, shutil, re
import numpy as np, cv2
from scipy.ndimage import gaussian_filter1d
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
REPO = ROOT
REF = REPO / 'PocketBoard/assets/references/reference-controls-palette.jpg'
ASSETS = REPO / 'PocketBoard/assets/button-silhouettes'
ANDROID = REPO / 'PocketBoard/android/app/src/main/res/drawable'
ARCHIVE = REPO / 'PocketBoard/assets/retired-art/polygon-button-silhouettes'
BOXES = {
'search':(1142,20,229,233), 'clear':(40,473,167,165), 'microphone':(238,473,169,166),
'volume-down':(481,475,153,157),'volume-up':(641,475,149,156),'mute':(798,473,149,159),
'previous-track':(954,474,143,158),'pause':(1103,474,142,158),'next-track':(1251,473,145,159),
'apps-grid':(86,833,211,191),'overlapping-windows':(594,831,213,193),
'windows-check':(850,831,213,193),'windows-plus':(1107,831,217,193),
'escape':(54,1232,209,182),'tab':(286,1231,205,183),'enter':(514,1228,205,186)
}
print('Reference:', REF, flush=True)
image=np.asarray(Image.open(REF).convert('RGB'))
height,width=image.shape[:2]
print('Image dimensions:',width,height,flush=True)
assert 0.65 < width/1417 < 1.1 and 0.65 < height/1536 < 1.1, 'Unexpected reference dimensions'
ARCHIVE.mkdir(parents=True,exist_ok=True)
stats={}
for name, (bx,by,bw,bh) in BOXES.items():
    bx=round(bx*width/1417); by=round(by*height/1536)
    bw=round(bw*width/1417);bh=round(bh*height/1536)
    roi=image[by:by+bh,bx:bx+bw]
    hsv=cv2.cvtColor(roi,cv2.COLOR_RGB2HSV)
    binary=(np.uint8((hsv[:,:,1]>70)&(hsv[:,:,2]>80)))*255
    components, labels, sizes, centroids=cv2.connectedComponentsWithStats(binary,8)
    assert components>1, name
    largest=1+int(sizes[1:,4].argmax())
    binary=np.uint8(labels==largest)*255
    binary=cv2.morphologyEx(binary,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)))
    binary=cv2.GaussianBlur(binary,(0,0),1.2)
    _,binary=cv2.threshold(binary,127,255,cv2.THRESH_BINARY)
    contours,_=cv2.findContours(binary,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    contour=max(contours,key=cv2.contourArea)[:,0,:].astype(float)
    x,y,w,h=cv2.boundingRect(contour.astype(np.int32))
    points=contour-np.array([x,y])
    closed=np.vstack([points,points[0]])
    lengths=np.linalg.norm(np.diff(closed,axis=0),axis=1)
    arclength=np.r_[0,np.cumsum(lengths)]
    keep=np.r_[True,np.diff(arclength)>1e-6]
    arclength=arclength[keep];closed=closed[keep]
    count=int(np.clip(round(arclength[-1]/9.0),48,130))
    grid=np.linspace(0,arclength[-1],count,endpoint=False)
    sampled=np.column_stack([np.interp(grid,arclength,closed[:,d]) for d in range(2)])
    sampled=gaussian_filter1d(sampled,sigma=.95,axis=0,mode='wrap')
    tangent=(np.roll(sampled,-1,axis=0)-np.roll(sampled,1,axis=0))*.43
    point=lambda p:f'{p[0]:.2f},{p[1]:.2f}'
    segments=['M '+point(sampled[0])]
    # C1 continuous cubic, retains each button's original shoulders and aspect.
    curve=[]
    for i in range(count):
        j=(i+1)%count
        a=sampled[i]; b=sampled[j]
        c1=a+tangent[i]/3;c2=b-tangent[j]/3
        curve.append((a,c1,c2,b))
        segments.append('C '+point(c1)+' '+point(c2)+' '+point(b))
    segments.append('Z')
    path=' '.join(segments)
    assert 0.86 < w/h < 1.15, f'{name}: unexpected bounds {w}x{h}'
    dest=ASSETS/(name+'.svg')
    if not (ARCHIVE/(name+'.svg')).exists():
        shutil.copyfile(dest,ARCHIVE/(name+'.svg'))
    dest.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="{name} button silhouette"><path fill="currentColor" d="{path}"/></svg>\n',encoding='utf-8')
    vec_name='pb_shape_'+name.replace('-','_')
    (ANDROID/(vec_name+'.xml')).write_text(f'<?xml version="1.0" encoding="utf-8"?>\n<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="{w}dp" android:height="{h}dp" android:viewportWidth="{w}" android:viewportHeight="{h}">\n  <path android:fillColor="#FFFCF4E9" android:pathData="{path}"/>\n</vector>\n',encoding='utf-8')
    # Rasterize cubic Beziers with 12 points per segment for geometric comparison.
    dense=[]
    for a,c1,c2,b in curve:
        for t in np.linspace(0,1,12,endpoint=False):
            dense.append((1-t)**3*a+3*(1-t)**2*t*c1+3*(1-t)*t*t*c2+t**3*b)
    render=np.zeros((h,w),np.uint8)
    cv2.fillPoly(render,[np.round(dense).astype(np.int32)],255)
    target=np.zeros((h,w),np.uint8)
    cv2.fillPoly(target,[np.round(points).astype(np.int32)],255)
    intersection=np.count_nonzero((target>0)&(render>0))
    union=np.count_nonzero((target>0)|(render>0))
    iou=intersection/union
    assert iou>.96, f'{name} IoU too low {iou:.5f}'
    stats[name]={'segments':count,'IoU':round(iou,5),'width':w,'height':h}
    print(f'{name:24} {count:3d} cubic segments, IoU {iou:.4f}, {w}x{h}',flush=True)
# The detailed Connected path was already an excellent, smooth hand trace.
connected=(ASSETS/'connected-pill.svg').read_text(encoding='utf-8')
assert connected.count('\nC ')>=20, 'Connected original detailed path changed'

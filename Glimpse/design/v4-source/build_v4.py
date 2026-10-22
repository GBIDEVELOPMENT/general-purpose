#!/usr/bin/env python3
"""Build Glimpse v4 reel-system pitch deck from Waltz v3 with editable slide content.
Reel UI illustrations are generated from original photo assets in this workspace.
This is design research, not runnable Android code.
"""
from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.dml.color import RGBColor
import math, random, io, textwrap

BASE=Path('/mnt/data')
OUT=BASE/'glimpse_v4';OUT.mkdir(exist_ok=True)
INPUT=BASE/'Waltz_v3_Native_Android_Pitch_Deck.pptx'
OUTPUT=BASE/'Glimpse_v4_Continuous_Reel_Pitch_Deck.pptx'
PHOTOS=[BASE/'glimpse_design/assets'/f'art{i}.jpg' for i in range(1,7)]
PAPER='#F6F0E6';CREAM='#FBF7EE';DARK='#153F46';TEAL='#1D5960';CORAL='#E8876C';SUN='#F0C970';SAGE='#87B7A6';PALE='#E9E4D8';INK='#243C40';MUTED='#6B7D7A';WHITE='#FFFFFF';MID='#D9D0C0';DARKER='#0C3037';
FONT_SERIF='/usr/share/fonts/truetype/noto/NotoSerif-Regular.ttf'
FONT_REG='/usr/share/fonts/truetype/lato/Lato-Regular.ttf'
FONT_BOLD='/usr/share/fonts/truetype/lato/Lato-Bold.ttf'
FONT_HEAVY='/usr/share/fonts/truetype/lato/Lato-Heavy.ttf'
S=4  # asset antialiasing factor

def rgb(h):return RGBColor.from_string(h.lstrip('#'))
def fillshape(sl,shape,color):shape.fill.solid();shape.fill.fore_color.rgb=rgb(color);shape.line.fill.background();return shape

def shp(sl,x,y,w,h,color,r=0,line=None):
 shape=sl.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if r else MSO_SHAPE.RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(h));fillshape(sl,shape,color)
 if line:shape.line.color.rgb=rgb(line)
 if r and hasattr(shape,'adjustments'): shape.adjustments[0]=0.16
 return shape

def oval(sl,x,y,w,h,color):
 shape=sl.shapes.add_shape(MSO_SHAPE.OVAL,Inches(x),Inches(y),Inches(w),Inches(h));fillshape(sl,shape,color);return shape

def tx(sl,s,x,y,w,h,sz=16,color=INK,bold=False,face='Aptos',align=None):
 sh=sl.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h));tf=sh.text_frame;tf.word_wrap=True
 tf.margin_left=Pt(0);tf.margin_right=Pt(0);tf.margin_top=Pt(0);tf.margin_bottom=Pt(0)
 for j,line in enumerate(str(s).split('\n')):
  p=tf.paragraphs[0] if j==0 else tf.add_paragraph();p.text=line;p.font.name=face;p.font.size=Pt(sz);p.font.bold=bold;p.font.color.rgb=rgb(color);p.space_after=Pt(3)
  if align:p.alignment=align
 return sh

def photo_obj(i):return Image.open(PHOTOS[i%len(PHOTOS)]).convert('RGB')

def cropped_photo(i,size):return ImageOps.fit(photo_obj(i),size,method=Image.Resampling.LANCZOS,centering=(0.5,0.5))

def draw_shadow(canvas,box,r=36):
 layer=Image.new('RGBA',canvas.size,(0,0,0,0));d=ImageDraw.Draw(layer);d.ellipse(box,fill=(24,31,31,52));layer=layer.filter(ImageFilter.GaussianBlur(r));canvas.alpha_composite(layer)

def wedge_mask(sz,cx,cy,r0,r1,theta,span):
 mask=Image.new('L',(sz,sz),0);d=ImageDraw.Draw(mask)
 pts=[]
 for k in range(33):
  angle=math.radians(theta-span/2+k*span/32)
  pts.append((cx+math.cos(angle)*r1,cy+math.sin(angle)*r1))
 for k in range(33):
  angle=math.radians(theta+span/2-k*span/32)
  pts.append((cx+math.cos(angle)*r0,cy+math.sin(angle)*r0))
 d.polygon(pts,fill=255)
 return mask

def reel_canvas(size=1000,rotation=0,mode='paper',slots=5,photo_offset=0,shadow=True):
 sz=int(size);im=Image.new('RGBA',(sz,sz),(0,0,0,0));q=sz/1000.;cx=cy=sz/2.;R=0.474*sz
 # outer paper shadow
 if shadow:draw_shadow(im,(int(cx-R+8*q),int(cy-R+17*q),int(cx+R+8*q),int(cy+R+17*q)),int(15*q))
 d=ImageDraw.Draw(im)
 d.ellipse((cx-R,cy-R,cx+R,cy+R),fill='#E8D9C5',outline='#D4C3AD',width=max(2,int(8*q)))
 rr=.455*sz;d.ellipse((cx-rr,cy-rr,cx+rr,cy+rr),fill='#F2E7D6',outline='#FCF6ED',width=max(1,int(4*q)))
 # fine original paper tooth, intentionally nonuniform but controlled
 rand=random.Random(210)
 for n in range(int(4100*q*q)):
  x=rand.randrange(sz);y=rand.randrange(sz)
  if (x-cx)**2+(y-cy)**2 < rr**2:
   r=rand.random();d.point((x,y),fill=(210,192,166,40 if r<.7 else 64))
 # Five generous, photograph-dominant trapezoidal windows.
 r0=.154*sz;r1=.431*sz;period=360/slots;span=period-11
 for i in range(slots):
  a=-90+i*period+rotation
  m=wedge_mask(sz,cx,cy,r0,r1,a,span)
  # slightly dark edge keyline by thickening behind transparent photo
  edge=m.filter(ImageFilter.MaxFilter(max(3,round(4*q)//2*2+1)))
  im.paste(Image.new('RGBA',(sz,sz),(48,51,49,225)),(0,0),edge)
  artwork=cropped_photo((i+photo_offset)%6,(sz,sz)).convert('RGBA')
  # shifts per sector to avoid repeated exact framing
  im.paste(artwork,(0,0),m)
 # stamped central ring
 d=ImageDraw.Draw(im)
 hub=.138*sz
 d.ellipse((cx-hub,cy-hub,cx+hub,cy+hub),fill='#DECDB8',outline='#C5B39D',width=max(2,int(5*q)))
 d.ellipse((cx-.089*sz,cy-.089*sz,cx+.089*sz,cy+.089*sz),fill='#CABBA9',outline='#F9F2E9',width=max(3,int(10*q)))
 d.ellipse((cx-.069*sz,cy-.069*sz,cx+.069*sz,cy+.069*sz),fill=CREAM)
 for i in range(slots):
  a=math.radians(-90+i*360/slots+rotation+period/2);x=cx+math.cos(a)*.119*sz;y=cy+math.sin(a)*.119*sz
  d.ellipse((x-3*q,y-3*q,x+3*q,y+3*q),fill='#B7A58E')
 # tiny coral index triangle outside ring
 if mode!='noindex':d.polygon([(cx-15*q,cy-R-12*q),(cx+15*q,cy-R-12*q),(cx,cy-R+10*q)],fill=CORAL)
 return im

def reel_asset(name,size=1000,rotation=0,photo_offset=0):
 path=OUT/name;reel_canvas(size,rotation,photo_offset=photo_offset).save(path);return path

def icon_mono(name,size=600):
 im=Image.new('RGBA',(size,size),(0,0,0,0));d=ImageDraw.Draw(im);cx=cy=size/2;R=size*.45
 d.ellipse((cx-R,cy-R,cx+R,cy+R),fill=DARK)
 for i in range(5):
  m=wedge_mask(size,cx,cy,size*.16,size*.42,-90+i*72,61)
  im.paste(Image.new('RGBA',im.size,(246,240,230,255)),(0,0),m)
 d=ImageDraw.Draw(im);d.ellipse((cx-size*.078,cy-size*.078,cx+size*.078,cy+size*.078),fill=DARK)
 p=OUT/name;im.save(p);return p

asset_reel=reel_asset('reel-five-wide-windows.png',1250)
asset_turn=reel_asset('reel-next-frame.png',1250,rotation=72,photo_offset=1)
asset_small=reel_asset('reel-last-frame.png',1250,rotation=-72,photo_offset=-1)
asset_mono=icon_mono('reel-monochrome.png')

# Screen mockups generated in PNG for self-contained poster views. All captions outside images in PPTX remain editable.
def f(path,sz):return ImageFont.truetype(str(path),sz)
SER=lambda size:f(FONT_SERIF,size)
BOLD=lambda size:f(FONT_BOLD,size)
REG=lambda size:f(FONT_REG,size)
def put(d,s,x,y,sz=26,color=INK,bold=False,serif=False,anchor=None):
 d.text((x,y),s,fill=color,font=(SER(sz) if serif else (BOLD(sz) if bold else REG(sz))),anchor=anchor)

def imgcard(im,photo_index,rect,radius=24):
 x,y,w,h=rect
 crop=cropped_photo(photo_index,(w,h)).convert('RGBA');mask=Image.new('L',(w,h));ImageDraw.Draw(mask).rounded_rectangle((0,0,w,h),radius,fill=255);im.paste(crop,(x,y),mask)

def rounded(d,rect,color,rad=18,outline=None,width=1):d.rounded_rectangle(rect,radius=rad,fill=color,outline=outline,width=width)

def screen(kind='collection',selection=0):
 W,H=480,1010;im=Image.new('RGBA',(W,H),CREAM);d=ImageDraw.Draw(im)
 # Android insets
 put(d,'9:30',25,20,20,DARK,bold=True);put(d,'●  ▲  ▮',391,18,18,DARK)
 if kind=='collection':
  put(d,'‹',23,78,42,DARK);put(d,'Golden Hour',W/2,94,35,DARK,serif=True,anchor='mm')
  put(d,'50 wallpapers  ·  Shuffle on',W/2,140,18,MUTED,anchor='mm')
  imgcard(im,(selection+0)%6,(28,168,W-56,355),20)
  d=ImageDraw.Draw(im);rounded(d,(40,465,176,507),CREAM,14)
  put(d,f'{selection+1} of 50',108,486,20,DARK,bold=True,anchor='mm')
  # black fade at base? not necessary
  put(d,'BROWSE THE REEL',29,540,17,TEAL,bold=True)
  put(d,'View all',391,540,19,TEAL,bold=True)
  # five-view circular reel extends past left, right, bottom of clipped viewport
  r=reel_canvas(890,rotation=selection*72,photo_offset=selection)
  # draw within clipped browser viewport x0-480 y570-935
  pos=(-205,570);panel=Image.new('RGBA',(480,365),(0,0,0,0))
  panel.alpha_composite(r,dest=(pos[0],-10)) if pos[0]>=0 else None
  # paste clipped crop manually, preserving alpha
  src=r.crop((205,0,685,365))
  im.alpha_composite(src,(0,570))
  d=ImageDraw.Draw(im)
  # overlay index cue, main reel center half way off-screen
  d.polygon([(W/2-13,570),(W/2+13,570),(W/2,590)],fill=CORAL)
  rounded(d,(21,887,459,942),CREAM,20)
  rounded(d,(33,896,163,933),DARK,17);put(d,'Next',98,915,19,CREAM,bold=True,anchor='mm')
  rounded(d,(173,896,303,933),PALE,17);put(d,'Set now',238,915,19,DARK,bold=True,anchor='mm')
  rounded(d,(313,896,447,933),PALE,17);put(d,'Grid  ▦',380,915,19,DARK,bold=True,anchor='mm')
 elif kind=='home':
  put(d,'glimpse.',25,87,48,DARK,serif=True)
  put(d,'A new view, whenever you look.',25,150,21,MUTED)
  imgcard(im,3,(22,205,W-44,460),24)
  d=ImageDraw.Draw(im);put(d,'CURRENT WALLPAPER',29,690,16,TEAL,bold=True);put(d,'Golden Hour',29,718,28,DARK,serif=True)
  put(d,'Eligible in about 3 min',29,760,18,MUTED)
  # small reel edge in bottom-right, not dominant
  r=reel_canvas(430,rotation=36)
  src=r.crop((0,0,230,235));im.alpha_composite(src,(283,735))
  d=ImageDraw.Draw(im);rounded(d,(25,819,194,878),DARK,22);put(d,'Next',110,847,22,CREAM,bold=True,anchor='mm')
  rounded(d,(212,819,292,878),PALE,22);put(d,'Pause',253,847,18,DARK,bold=True,anchor='mm')
 elif kind=='grid':
  put(d,'‹',23,78,42,DARK);put(d,'Golden Hour',W/2,100,35,DARK,serif=True,anchor='mm')
  put(d,'50 photos  ·  3 selected',28,150,19,MUTED)
  y=193
  for row in range(3):
   for col in range(2):
    x=24+col*222
    imgcard(im,row*2+col,(x,y+row*200,208,185),19)
  d=ImageDraw.Draw(im);rounded(d,(32,831,448,904),DARK,22);put(d,'Add to rotation',240,866,24,CREAM,bold=True,anchor='mm')
 elif kind=='browse':
  put(d,'DISCOVER',25,94,17,TEAL,bold=True);put(d,'Something lovely',25,130,36,DARK,serif=True)
  put(d,'Browse your sources',25,183,20,MUTED)
  for row in range(3):
   y=242+row*200;imgcard(im,row,(26,y,428,170),21)
  d=ImageDraw.Draw(im);rounded(d,(30,853,420,906),DARK,22);put(d,'New collection',240,879,20,CREAM,bold=True,anchor='mm')
 # common bottom nav
 d=ImageDraw.Draw(im);d.rectangle((0,943,W,H),fill=CREAM)
 d.line((0,944,W,944),fill=MID,width=2)
 for j,t in enumerate(['Home','Discover','Collections','Automation']):
  x=59+j*119;d.ellipse((x-5,957,x+5,967),fill=CORAL if (kind=='home' and j==0) or (kind in ('grid','collection') and j==2) else SAGE)
  put(d,t,x,985,16,DARK if (kind=='home' and j==0) or (kind in ('grid','collection') and j==2) else MUTED,bold=True,anchor='mm')
 return im

screens={n:screen(n) for n in ['home','collection','grid','browse']}
for n,im in screens.items():im.save(OUT/f'screen-{n}.png')

# Three stages illustrating endless paper reel without lying about finite list.
def strip_states():
 W,H=1420,415;im=Image.new('RGBA',(W,H),PAPER)
 d=ImageDraw.Draw(im)
 for j in range(3):
  x=25+j*468
  rounded(d,(x,15,x+430,400),CREAM,26)
  put(d,['01  BEFORE','02  ONE NOTCH','03  WINDOWS RECYCLED'][j],x+22,33,19,TEAL,bold=True)
  r=reel_canvas(510,rotation=j*72,photo_offset=j)
  # offscreen at bottom, clipped by viewport
  src=r.crop((40,0,470,286));im.alpha_composite(src,(x,104))
  d=ImageDraw.Draw(im)
  put(d,['IMAGE 12','IMAGE 13','IMAGE 14'][j],x+22,354,17,DARK,bold=True)
  put(d,['Index remains stable','Snap advances one item','Backed by collection data'][j],x+22,374,15,MUTED)
 return im
strip_states().save(OUT/'reel-virtualization-sequence.png')

p=Presentation(INPUT)
# Update every *editable* legacy title/footer to Glimpse; legacy raster screens remain design history.
for slide in p.slides:
 for shape in slide.shapes:
  if shape.has_text_frame:
   for para in shape.text_frame.paragraphs:
    for run in para.runs:
     run.text=run.text.replace('WALTZ','GLIMPSE').replace('Waltz','Glimpse').replace('waltz','glimpse').replace('70 lives','73 lives')
# old cover: replace its headline/description under old graphics; add a new brand banner
old=p.slides[0]
for shape in old.shapes:
 if shape.has_text_frame:
  for para in shape.text_frame.paragraphs:
   if para.text.lower().strip()=='glimpse':
    for run in para.runs:run.text='glimpse.'
   if 'A little change looks good on you' in para.text:
    for run in para.runs:run.text=run.text.replace('A little change looks good on you.','Something lovely, every time you look.')
# The new identity is presented from the opening slide, not postponed to the addendum.
shp(old,0,0,SW if 'SW' in globals() else 13.333,7.5,PAPER)
old.shapes.add_picture(str(asset_reel), Inches(6.90), Inches(-.56), width=Inches(8.20),height=Inches(8.20))
tx(old,'GLIMPSE / ANDROID WALLPAPERS',.83,.72,5.9,.39,12,TEAL,True)
tx(old,'Glimpse.',.82,1.82,6.65,.92,55,DARK,False,'Georgia')
tx(old,'Something lovely,\nevery time you look.',.86,2.92,5.86,1.35,29,DARK,False,'Georgia')
tx(old,'A native Android wallpaper app that makes your screen feel like a window into somewhere else.',.88,4.87,5.37,1.10,18,MUTED)
tx(old,'THE PAPER REEL  /  CONTINUOUS BROWSING  /  V4',.88,6.68,6.2,.35,11,CORAL,True)

# section authoring helpers
SW,SH=p.slide_width/914400,p.slide_height/914400
assert abs(SW-13.3333333333)<.01

def new(tag,title,subtitle='',dark=False):
 sl=p.slides.add_slide(p.slide_layouts[0]);sl.background.fill.solid();sl.background.fill.fore_color.rgb=rgb(DARK if dark else PAPER)
 shp(sl,.38,.40,.13,.32,CORAL);tx(sl,f'GLIMPSE    /    {tag.upper()}',.69,.42,9,.34,10,CREAM if dark else TEAL,True)
 if title:tx(sl,title,.69,.94,11.98,.7,29,CREAM if dark else DARK,False,'Georgia')
 if subtitle:tx(sl,subtitle,.72,1.69,11.6,.45,14,SAGE if dark else MUTED)
 tx(sl,f'GLIMPSE / REEL SYSTEM / 2026     •     CONCEPT',.69,7.13,9,.24,9,SAGE if dark else MUTED)
 return sl

def image(sl,path,x,y,w,h):sl.shapes.add_picture(str(path),Inches(x),Inches(y),width=Inches(w),height=Inches(h))
def labelbox(sl,title,body,x,y,w,h,accent=CORAL):
 shp(sl,x,y,w,h,WHITE,1);shp(sl,x+.15,y+.21,.07,.32,accent)
 tx(sl,title,x+.38,y+.18,w-.60,.40,17,DARK,True)
 tx(sl,body,x+.28,y+.67,w-.52,h-.74,12,MUTED)

def photo_slide_icon():
 sl=new('NEW IDENTITY','A reel, freed from its old machinery.','Five generous photographic windows. Paper, light, movement, surprise.')
 image(sl,asset_reel,.60,2.07,5.20,5.20)
 tx(sl,'THE OBJECT',7.10,2.31,4.5,.38,13,TEAL,True)
 tx(sl,'The picture,\nnot the perforation.',7.10,2.82,5.6,1.23,30,DARK,False,'Georgia')
 tx(sl,'A larger opening makes the photograph legible, especially at small sizes. The circular paper shell is now a gentle framework for the imagery, not a historical constraint.',7.1,4.43,5.55,1.5,16,MUTED)
 tx(sl,'5 windows  /  72° per step  /  pure visual metaphor',7.11,6.35,5.6,.34,12,TEAL,True)
 return sl

sl=new('REEL PRINCIPLE','A circle bigger than the screen.','The reel continues beyond the viewport. Only the active arc asks for attention.')
image(sl,OUT/'screen-collection.png',.88,2.11,2.72,5.06)
image(sl,OUT/'screen-home.png',4.12,2.11,2.72,5.06)
image(sl,OUT/'screen-grid.png',7.36,2.11,2.72,5.06)
labelbox(sl,'01  BROWSE','Oversized reel extends beyond left, right and lower edges.',10.38,2.18,2.32,1.29)
labelbox(sl,'02  GLANCE','Home shows only a smaller crescent beside the current view.',10.38,3.66,2.32,1.29,SAGE)
labelbox(sl,'03  ESCAPE','View all opens the ordinary image grid for serious library work.',10.38,5.14,2.32,1.29)

photo_slide_icon()

sl=new('VISUAL DIALECT','Three expressions of one object.','Different sizes and roles; the same paper, spindle and generous windows.')
image(sl,asset_reel,.89,2.40,3.20,3.20)
image(sl,asset_mono,5.07,2.66,2.65,2.65)
image(sl,OUT/'screen-home.png',9.15,2.28,2.13,4.44)
tx(sl,'COLOUR REEL',1.60,5.73,3,.37,13,TEAL,True)
tx(sl,'MONOCHROME GLYPH',5.04,5.73,3.7,.37,13,TEAL,True)
tx(sl,'IN CONTEXT',9.30,6.81,2.6,.32,13,TEAL,True)
tx(sl,'Collection identity',1.3,6.12,3.25,.35,14,MUTED)
tx(sl,'Android themed icon',5.10,6.12,3.00,.35,14,MUTED)

sl=new('INFINITE ILLUSION','The windows move. The collection does not end at five.','One fixed focal position; a few recycled windows; a stable, durable collection behind them.')
image(sl,OUT/'reel-virtualization-sequence.png',.60,2.20,12.17,3.56)
tx(sl,'A finite collection can wrap for browsing without implying an endless source. At a queue boundary, no-repeat shuffle reseeds explicitly and avoids immediate duplicates.',.95,6.20,11.80,.65,15,MUTED)

sl=new('REAL INTERACTION','The preview stays still while the reel advances.','Touch and motion follow the user’s intent. Advancing the browser never silently changes the system wallpaper.')
image(sl,OUT/'screen-collection.png',1.02,2.16,2.43,5.11)
image(sl,asset_reel,4.42,2.57,3.20,3.20)
image(sl,asset_turn,7.77,2.57,3.20,3.20)
tx(sl,'NEXT  →',7.06,3.66,1.08,.48,16,CORAL,True)
tx(sl,'BROWSE',4.85,5.91,2.40,.36,13,TEAL,True)
tx(sl,'NEXT IMAGE',8.03,5.91,2.40,.36,13,TEAL,True)
tx(sl,'Browse = choose what to view. Set now = deliberately apply. The image count follows actual collection membership.',4.38,6.42,8.13,.65,15,MUTED)

sl=new('COLLECTIONS','The reel is a beautiful cover, not a storage format.','Each collection can show a distinctive crop of its own artwork.')
image(sl,OUT/'screen-collection.png',.72,2.21,2.52,5.29)
for i,t in enumerate([('Rainbows','240 photographs'),('Wild Places','42 photographs'),('Golden Hour','50 photographs')]):
 x=3.84+i*2.92
 image(sl,[asset_reel,asset_small,asset_turn][i],x,2.76,2.59,2.59)
 tx(sl,t[0],x,5.48,2.83,.45,20,DARK,False,'Georgia')
 tx(sl,t[1],x,6.02,2.83,.35,12,MUTED)
 tx(sl,'Open collection',x,6.41,2.83,.32,12,TEAL,True)

sl=new('HOME','Let the wallpaper take the stage.','A small reel signature on Home, not a full spinning disk on every surface.')
image(sl,OUT/'screen-home.png',.78,2.17,2.61,5.06)
labelbox(sl,'Current image first','The photograph takes the most space. Collection context stays nearby.',3.95,2.51,4.01,1.42)
labelbox(sl,'Immediate actions','Next, Pause, Share and Set now have ordinary labels and 48dp touch targets.',8.19,2.51,4.01,1.42,SAGE)
labelbox(sl,'A little reel peeks in','A cropped crescent offers recognition and continuity, not an extra navigation burden.',3.95,4.30,4.01,1.42,SAGE)
labelbox(sl,'Scheduling stays honest','“Next eligible” refers to Android scheduling; it does not claim a guaranteed exact change.',8.19,4.30,4.01,1.42)

sl=new('BROWSE / GRID','Delight to browse. Efficient to organize.','Two views for the same data. Switch instantly without losing selection or scroll position.')
image(sl,OUT/'screen-collection.png',2.18,2.11,2.45,5.15)
image(sl,OUT/'screen-grid.png',7.03,2.11,2.45,5.15)
tx(sl,'REEL VIEW',2.27,6.99,2.2,.36,13,TEAL,True)
tx(sl,'GRID VIEW',7.09,6.99,2.2,.36,13,TEAL,True)
tx(sl,'←  Immersive inspection',.86,4.47,2.2,1.03,16,DARK)
tx(sl,'Fast multi-select  →',9.82,4.47,3.0,1.03,16,DARK)

sl=new('MICROCOPY','Poetry around the edges. Clarity in the controls.','Glimpse should feel warm without ever hiding what an action actually does.')
for i,(a,b) in enumerate([('WELCOME','Something lovely, every time you look.'),('BROWSE','Browse the reel  ·  View all'),('ACTION','Next  ·  Set as wallpaper  ·  Share'),('STATE','50 wallpapers  ·  Shuffle without repeats'),('DIAGNOSTICS','Next change eligible in about 3 min'),('ERROR','Couldn’t change wallpaper. Try now  ·  Details')]):
 x=.76+(i%2)*6.14;y=2.31+(i//2)*1.32;shp(sl,x,y,5.85,1.09,WHITE,1)
 tx(sl,a,x+.26,y+.17,2.03,.27,10,TEAL,True)
 tx(sl,b,x+.27,y+.47,5.35,.51,16,DARK)

sl=new('ACCESSIBILITY','The illusion must never become an obstacle.','A carousel must remain a usable control when its shape, motion or gesture is unavailable.')
for i,(a,b) in enumerate([('Tap targets','Large Next / Previous buttons and a persistent View all option.'),('TalkBack','A linear list, labelled “Image 12 of 50”; actions in logical reading order.'),('Reduced motion','Instant image replacement, no reel turn or simulated inertia.'),('Large text','Text sits outside photographic windows; the reel can shrink or collapse.'),('Gesture conflict','Vertical scrolling scrolls the page; horizontal drag only in reel region.'),('No forced wrap','Finite “end of collection” mode or seamless browse loop; users can choose.')]):
 x=.75+(i%2)*6.14;y=2.25+(i//2)*1.39;labelbox(sl,a,b,x,y,5.81,1.25,CORAL if i%2==0 else SAGE)

sl=new('LAYOUT','Responsive by design, not by shrinking the reel.','Clip to the reel’s own container. Keep system bars, tap controls, and content accessibility independent.')
for i,(a,b,c) in enumerate([('SMALL PORTRAIT','Less visible arc','~60–70% of container width visible, with clear Next / Grid buttons.'),('LARGE PORTRAIT','Generous arc','More photograph and higher surrounding cards; no tiny windows.'),('LANDSCAPE / TABLET','Side-docked reel','Partial disk on the side, hero photograph and actions in the remaining pane.')]):
 x=.74+i*4.18;shp(sl,x,2.33,3.91,3.85,WHITE,1)
 tx(sl,a,x+.25,2.71,3.35,.36,12,TEAL,True)
 tx(sl,b,x+.24,3.38,3.37,.58,23,DARK,False,'Georgia')
 tx(sl,c,x+.24,4.22,3.39,1.48,14,MUTED)
 tx(sl,['360dp','412dp','> 600dp'][i],x+.24,5.72,2,.29,11,CORAL,True)

sl=new('ENGINEERING CONTRACT','A continuous reel is a viewport, not an infinite bitmap.','Reuse a handful of window nodes, keep position as a stable asset ID, and avoid unbounded list indexes.')
for i,(a,b) in enumerate([('Domain','collection IDs + deterministic order + shuffle queue + current index'),('Projection','current + 2 neighbours each side; recycled five-window snapshot'),('Gesture','pointer input → velocity threshold → one notch snap → selected ID'),('Rendering','Compose Canvas paths + clipped Coil image thumbnails at bounded resolution'),('Persistence','save image ID and browsing order; return after process death at same item'),('Testing','fuzz reorder/remove, empty/singleton sets, state restore, RTL, talkback')]):
 y=2.27+i*.68;shp(sl,.89,y,11.54,.57,WHITE,1)
 tx(sl,a,1.15,y+.12,2.05,.32,13,TEAL,True);tx(sl,b,3.16,y+.11,8.86,.38,13,DARK)

sl=new('UX DECISIONS','A little theatre. No deception.','The illusion represents movement through a collection, never a claim of endless new photographs.')
labelbox(sl,'End of collection','For Browse All, allow finite stop or opt-in wrap. For Shuffle, mark new cycle and avoid recent repeats.',.82,2.49,5.72,1.72)
labelbox(sl,'Large collections','Never load every bitmap. Load neighbouring previews and keep random access through Grid and Search.',6.78,2.49,5.72,1.72,SAGE)
labelbox(sl,'Active wallpaper','Browsing changes only the preview. “Set now” explicitly asks Android to apply the chosen asset.',.82,4.53,5.72,1.72,SAGE)
labelbox(sl,'Touch and motion','Reel steps are deliberate and short; no continuous spinning, auto-advance or audio by default.',6.78,4.53,5.72,1.72)

sl=new('DECISION','Keep the tactile paper. Give the photographs room.','This is Glimpse’s signature interaction; everything else stays legible, native and easy.')
image(sl,asset_reel,.72,2.16,4.52,4.52)
tx(sl,'THE DESIGN BET',6.03,2.47,5.40,.35,13,TEAL,True)
tx(sl,'A small window\ninto somewhere else.',6.03,3.08,6.18,1.25,27,DARK,False,'Georgia')
tx(sl,'Icon: five large photographic windows.\nCollection: reel as thumbnail cover.\nBrowser: oversized partial reel.\nHome: restrained reel accent.\nGrid: always one tap away.',6.03,4.63,6.2,1.58,16,MUTED)

# Divider before prior source deck slides; reposition new conceptual slides to after cover
sl=new('FOUNDATIONS','The earlier research is retained.','The following slides capture the existing Glimpse product analysis, initial exploratory UI and the Android engineering plan. Some embedded mockup screenshots reflect the pre-reel design and are superseded by the new reel concepts.')
labelbox(sl,'Previous visual explorations','Useful interaction patterns remain; old image assets are evidence of the design process, not the chosen look.',.98,2.88,5.41,2.12)
labelbox(sl,'Native architecture unchanged','Kotlin, Compose, Room, reliable wallpaper delivery, secure imports, universal sharing and signed APKs remain the implementation direction.',6.82,2.88,5.41,2.12,SAGE)

# slide IDs: original length 42, followed by N new. rearrange: original cover, new section, original slide 2-42
ids=p.slides._sldIdLst
children=list(ids)
newchildren=children[:1]+children[42:]+children[1:42]
for ch in children:ids.remove(ch)
for ch in newchildren:ids.append(ch)

p.core_properties.title='Glimpse | Continuous Paper Reel | Native Android Product Pitch'
p.core_properties.subject='Glimpse identity, immersive reel browsing and native architecture'
p.save(OUTPUT)
print('created',OUTPUT,'slides',len(p.slides),'bytes',OUTPUT.stat().st_size)
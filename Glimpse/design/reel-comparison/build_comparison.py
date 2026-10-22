#!/usr/bin/env python3
"""Generate pre-build visual comparison from controlled photo fixtures.

Design-only. No Android app or device screenshots. SVGs self-contained with embedded
image fixture JPEGs. A/B/C cases share identical source photographs and dimensions.
"""
from pathlib import Path
import base64, math, hashlib, json, html, re
import cairosvg
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image

ROOT=Path(__file__).resolve().parent
DIR=ROOT
DIR.mkdir(parents=True,exist_ok=True)
PHOTO_BASE=ROOT/'fixtures/source'
PHOTOS={i:(PHOTO_BASE/f'art{i}.jpg').read_bytes() for i in range(1,7)}
URI={i:'data:image/jpeg;base64,'+base64.b64encode(PHOTOS[i]).decode() for i in PHOTOS}
TOK={'paper':'#F6F0E6','white':'#FFFEFA','teal':'#153F46','teal2':'#27626B','muted':'#667975','coral':'#E8876C','sand':'#EAD9BD','dusk':'#8E7E6C','sage':'#88B8A8','gold':'#F0C970'}
MOCKS={}
FONT='Inter,Arial,Helvetica,sans-serif'
SERIF='Georgia,Noto Serif,serif'

def label(x,y,t,size=13,weight=400,color=None,anchor='start',family=None,opacity=1):
    return f'<text x="{x}" y="{y}" font-family="{family or FONT}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="{color or TOK["teal"]}" opacity="{opacity}">{html.escape(str(t))}</text>'

def rr(x,y,w,h,fill,r=12,stroke=None,sw=1,opacity=1):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" opacity="{opacity}"'+(f' stroke="{stroke}" stroke-width="{sw}"' if stroke else '')+'/>'

def line(x1,y1,x2,y2,c=None,width=1,opacity=1):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c or TOK["teal"]}" stroke-width="{width}" opacity="{opacity}"/>'

def button(x,y,w,h,t,fill=None,fg=None,outline=False,size=13):
    fill=fill or TOK['teal']; fg=fg or '#FFFFFF'
    if outline: fill='#FFFFFF';fg=TOK['teal']
    return rr(x,y,w,h,fill,r=12,stroke='#B8C9C3' if outline else None)+label(x+w/2,y+h/2+size*.35,t,size=size,weight=650,color=fg,anchor='middle')

def image_rect(x,y,w,h,id,rx=12):
    key=f'imgclip{int(x*10)}_{int(y*10)}_{id}'
    return f'<defs><clipPath id="{key}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}"/></clipPath></defs><image x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid slice" href="{URI[id]}" clip-path="url(#{key})"/>'

def status():
    return label(23,22,'9:41',12,700)+label(351,22,'●  ▰  ▴',12,600)

def bottom_nav(active='Collections'):
    s=rr(0,843,420,57,'#FFFEFA',r=0)+line(0,843,420,843,'#DFE4D9')
    for i,t in enumerate(['Home','Discover','Collections','Automation']):
        x=[53,156,265,366][i]
        c=TOK['teal'] if t==active else '#81908A'
        s+=f'<circle cx="{x}" cy="861" r="5" fill="{c}" opacity=".8"/>'+label(x,884,t,10.3,650 if t==active else 400,c,'middle')
    s+=rr(164,896,92,3,'#556A65',2)
    return s

def arc_wedge(cx,cy,r0,r1,deg,span=60):
    a=(deg-span/2)*math.pi/180;b=(deg+span/2)*math.pi/180
    def p(r,t):return (cx+r*math.cos(t),cy+r*math.sin(t))
    x0,y0=p(r1,a);x1,y1=p(r1,b);x2,y2=p(r0,b);x3,y3=p(r0,a)
    return f'M{x0:.3f},{y0:.3f} A{r1:.3f},{r1:.3f} 0 0 1 {x1:.3f},{y1:.3f} L{x2:.3f},{y2:.3f} A{r0:.3f},{r0:.3f} 0 0 0 {x3:.3f},{y3:.3f} Z'

def reel(cx,cy,r,ids,uid,visible=True,pointer=True,selected=0):
    # ids = five positions: image fixture ID or None; slots intentionally blank when no source.
    s=f'<g id="{uid}" aria-label="Paper reel; genuine photo slots only">'
    s+=f'<circle cx="{cx+2}" cy="{cy+4}" r="{r+2}" fill="#7B6750" opacity=".13"/>'
    s+=f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#DCC8AA" stroke="#C3B092" stroke-width="{max(1,r*.016):.1f}"/>'
    s+=f'<circle cx="{cx}" cy="{cy}" r="{r*.967}" fill="#F4E5CC" stroke="#FFF9EB" stroke-width="{max(1,r*.015):.1f}"/>'
    s+=f'<circle cx="{cx}" cy="{cy}" r="{r*.94}" fill="none" stroke="#C8AD88" stroke-width="{max(1,r*.008):.1f}" opacity=".6"/>'
    for i,photo_id in enumerate(ids):
        a=-90+i*72
        clip=f'{uid}slot{i}'
        path=arc_wedge(cx,cy,r*.32,r*.915,a,span=65)
        s+=f'<defs><clipPath id="{clip}"><path d="{path}"/></clipPath></defs>'
        if photo_id:
            # center crop is identical source pixel set; all fixtures are genuine imported test photos.
            ww=r*1.9
            s+=f'<image x="{cx-ww/2:.1f}" y="{cy-ww/2:.1f}" width="{ww:.1f}" height="{ww:.1f}" preserveAspectRatio="xMidYMid slice" href="{URI[photo_id]}" clip-path="url(#{clip})"/>'
        else:
            s+=f'<path d="{path}" fill="#E9DCC9"/>'
        s+=f'<path d="{path}" fill="none" stroke="#B99F7F" stroke-width="{max(1,r*.009):.1f}"/>'
    s+=f'<circle cx="{cx}" cy="{cy}" r="{r*.305}" fill="#D7BE9B" stroke="#B49B77" stroke-width="{max(1,r*.015):.1f}"/>'
    s+=f'<circle cx="{cx}" cy="{cy}" r="{r*.232}" fill="#F0E3CE" stroke="#FFF9EC" stroke-width="{max(1,r*.013):.1f}"/>'
    s+=f'<circle cx="{cx}" cy="{cy}" r="{r*.085}" fill="#CBB496" stroke="#BCA486" stroke-width="{max(1,r*.016):.1f}"/>'
    # dynamic looking paper edge indentations
    for k in range(10):
        angle=(k*36-90)*math.pi/180
        rad=r*.983
        x=cx+rad*math.cos(angle);y=cy+rad*math.sin(angle)
        s+=f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{max(0.7,r*.004):.2f}" fill="#C2A986" opacity=".7"/>'
    s+='</g>'
    if pointer:
        py=cy-r+1
        s+=f'<path d="M{cx-9},{py-12} L{cx+9},{py-12} L{cx},{py+5} Z" fill="{TOK["coral"]}" stroke="#FFFAE9" stroke-width="2"/>'
    return s

def header(title,sub=''):
    return status()+label(24,75,'‹',35,400)+label(65,71,title,29,600,family=SERIF)+(label(65,97,sub,12,400,TOK['muted']) if sub else '')

def svgphone(body,name,metadata):
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="420" height="900" viewBox="0 0 420 900"><title>{html.escape(name)}</title><desc>{html.escape(metadata)}</desc>'+rr(0,0,420,900,TOK['paper'],0)+body+'</svg>'
    p=DIR/(name+'.svg');p.write_text(svg)
    cairosvg.svg2png(bytestring=svg.encode(),write_to=str(ROOT/(name+'.png')),output_width=840,output_height=1800)
    MOCKS[name]={'w':420,'h':900,'svg':str(p),'png':str(ROOT/(name+'.png')),'desc':metadata}
    return p

def draw_a():
    s=header('Golden Hour','6 photographs · Previewing 3 of 6')
    s+=image_rect(22,118,376,330,1,18)
    s+=rr(36,406,117,29,'#FFFAF0',14)+label(95,425,'Selected · 3 of 6',11,650,TOK['teal'],'middle')
    s+=label(23,483,'Selected photo, not yet applied',13,500,TOK['muted'])
    s+=label(23,521,'BROWSE PHOTOS',11,760,TOK['teal'])+label(396,521,'View all →',12,650,TOK['teal'],'end')
    s+='<defs><clipPath id="wheelclipa"><rect x="0" y="532" width="420" height="241"/></clipPath></defs>'
    s+='<g clip-path="url(#wheelclipa)">'+reel(210,785,246,[1,2,3,4,5],'maina')+'</g>'
    s+=rr(0,769,420,74,'#F6F0E6',0)
    s+=button(22,778,91,45,'‹ Previous',outline=True,size=12)+button(121,778,99,45,'Next photo',outline=True,size=12)+button(228,778,170,45,'Set wallpaper',size=12)
    s+=bottom_nav()
    svgphone(s,'A_single_photo_reel','Baseline single photo reel. Six imported art fixtures; selected art1 is #3 of 6. Reel rotates to preview only; Set wallpaper is explicit.')

def draw_b():
    s=header('Golden Hour','Collection 1 of 3 · Photo 3 of 6')
    s+=label(22,131,'CHOOSE COLLECTION',11,750)
    s+=label(22,164,'Golden Hour',21,600,family=SERIF)
    s+=label(22,185,'Three collections',11,400,TOK['muted'])
    s+=button(22,199,143,36,'Choose collection ▾',outline=True,size=11)
    s+='<defs><clipPath id="parentclipb"><rect x="245" y="100" width="175" height="161"/></clipPath></defs>'
    s+='<g clip-path="url(#parentclipb)">'+reel(371,220,131,[1,2,3,None,None],'parentb',pointer=False)+'</g>'
    s+=rr(315,235,90,26,'#FFFAF0',13)+label(360,252,'Golden Hour',10.4,700,TOK['teal'],'middle')
    s+=image_rect(22,271,376,228,1,17)
    s+=rr(36,462,114,29,'#FFF8EB',13)+label(93,481,'Selected · 3 of 6',11,650,TOK['teal'],'middle')
    s+=label(22,521,'BROWSE PHOTOS',11,750)+label(396,521,'View all →',12,650,TOK['teal'],'end')
    s+='<defs><clipPath id="childclipb"><rect x="0" y="536" width="420" height="237"/></clipPath></defs>'
    s+='<g clip-path="url(#childclipb)">'+reel(166,795,247,[1,2,3,4,5],'childb')+'</g>'
    s+=rr(0,769,420,74,TOK['paper'],0)
    s+=button(22,778,91,45,'‹ Previous',outline=True,size=12)+button(121,778,99,45,'Next photo',outline=True,size=12)+button(228,778,170,45,'Set wallpaper',size=12)
    s+=bottom_nav()
    svgphone(s,'B_asymmetric_collection_photo','Nested selectors: small top-right collection reel selects CollectionId only; larger bottom-left photo reel selects ImageAssetId only. Both preview, neither applies wallpaper. Same selected photo and fixture set as A.')

def draw_b_compact():
    s=header('Golden Hour','6 photographs · Previewing 3 of 6')
    s+=rr(22,113,376,57,'#FFFDF7',14,stroke='#DAC9B0')
    s+=label(39,136,'COLLECTION',9.5,750,TOK['muted'])+label(39,157,'Golden Hour',16,600)+label(382,149,'Change ▾',12,650,TOK['teal'],'end')
    s+=image_rect(22,185,376,262,1,17)
    s+=rr(36,409,114,29,'#FFF8EB',13)+label(93,428,'Selected · 3 of 6',11,650,TOK['teal'],'middle')
    s+=label(22,483,'BROWSE PHOTOS',11,750)+label(396,483,'View all →',12,650,TOK['teal'],'end')
    s+='<defs><clipPath id="childclipbc"><rect x="0" y="505" width="420" height="264"/></clipPath></defs>'
    s+='<g clip-path="url(#childclipbc)">'+reel(210,783,250,[1,2,3,4,5],'childbc')+'</g>'
    s+=rr(0,769,420,74,TOK['paper'],0)
    s+=button(22,778,91,45,'‹ Previous',outline=True,size=12)+button(121,778,99,45,'Next photo',outline=True,size=12)+button(228,778,170,45,'Set wallpaper',size=12)
    s+=bottom_nav()
    svgphone(s,'B_compact_fallback','Asymmetric parent reel automatically replaced by a normal labeled collection picker when viewport height, font scale or density cannot support independent safe hit areas.')

def draw_c():
    s=header('Your wallpapers','Two destinations · Independent previews')
    s+=label(25,129,'HOME',11,760)+label(395,129,'LOCK  ›',11,760,TOK['muted'],'end')
    s+=rr(22,147,376,76,'#FFFEFA',15,stroke='#DDDFD4')
    s+=image_rect(33,155,54,60,2,8)+label(100,176,'Lock preview',15,600)+label(100,196,'Mountain Air',12,450,TOK['muted'])
    s+=button(277,168,107,34,'Edit Lock',outline=True,size=11)
    s+=image_rect(22,242,376,257,1,17)
    s+=rr(35,457,122,29,'#FFFAEF',12)+label(96,476,'Home · Preview',11,650,TOK['teal'],'middle')
    s+=label(22,533,'BROWSE HOME PHOTOS',11,760)+label(396,533,'View all →',12,650,TOK['teal'],'end')
    s+='<defs><clipPath id="homeclipc"><rect x="0" y="545" width="420" height="225"/></clipPath></defs>'
    s+='<g clip-path="url(#homeclipc)">'+reel(210,798,249,[1,2,3,4,5],'homec')+'</g>'
    s+=rr(0,769,420,74,TOK['paper'],0)
    s+=button(22,778,84,45,'‹ Photo',outline=True,size=12)+button(114,778,84,45,'Next photo',outline=True,size=12)+button(206,778,192,45,'Apply to Home',size=12)
    s+=bottom_nav('Home')
    svgphone(s,'C_destinations_compact','Home/Lock separately chosen wallpaper photos. One active large Home photo reel; Lock preview and labeled Edit Lock affordance, not a second large hidden interactive disk. Both selected previews remain separate from actual applied wallpaper.')


def draw_c_simple():
    s=header('Your wallpapers','Two destinations · Independent previews')
    s+=rr(22,122,376,45,'#E6EAE0',15)
    s+=rr(25,125,185,39,TOK['teal'],12)+label(117,151,'Home',13,680,'#FFF','middle')+label(299,151,'Lock screen',13,600,TOK['teal'],'middle')
    s+=image_rect(22,184,376,309,1,17)
    s+=rr(36,451,122,28,'#FFFAEF',12)+label(97,469,'Home · Preview',11,650,TOK['teal'],'middle')
    s+=label(22,519,'BROWSE HOME PHOTOS',11,760)+label(396,519,'View all →',12,650,TOK['teal'],'end')
    s+='<defs><clipPath id="homeclips"><rect x="0" y="531" width="420" height="238"/></clipPath></defs>'
    s+='<g clip-path="url(#homeclips)">'+reel(210,792,247,[1,2,3,4,5],'homes')+'</g>'
    s+=rr(0,769,420,74,TOK['paper'],0)
    s+=button(22,778,84,45,'‹ Photo',outline=True,size=12)+button(114,778,84,45,'Next photo',outline=True,size=12)+button(206,778,192,45,'Apply to Home',size=12)
    s+=bottom_nav('Home')
    svgphone(s,'C_destinations_tabs_baseline','Conventional compact baseline for per-target Home and Lock preview: two labeled tabs, one current reel; no second decorative disk.')

def svgwide():
    name='D_destinations_wide_dual'
    w,h=960,540
    s=rr(0,0,w,h,TOK['paper'],0)+label(34,49,'glimpse.',34,750,TOK['teal'])
    s+=label(925,44,'DESTINATIONS  ·  HOME + LOCK',12,700,TOK['muted'],'end')
    s+=line(30,65,930,65,'#D4D3C4')
    for ix,(name0,photo,xc,active) in enumerate([('Home',1,242,True),('Lock',2,713,False)]):
        x=30+ix*475
        s+=label(x,110,name0+' wallpaper',25,600,family=SERIF)
        s+=label(x,129,'Selected preview · Not yet applied',11,500,TOK['muted'])
        s+=image_rect(x,150,173,233,photo,13)
        s+=label(x+195,176,'BROWSE '+name0.upper(),10,750)
        s+=label(x+195,199,'3 of 6',12,650,TOK['muted'])
        s+=button(x+195,216,204,38,'Previous photo',outline=True,size=12)
        s+=button(x+195,264,204,38,'Next photo',outline=True,size=12)
        s+=button(x+195,312,204,43,'Apply to '+name0,size=12)
        s+=button(x+195,366,204,33,'View all',outline=True,size=11)
        s+=f'<defs><clipPath id="wideclip{ix}"><rect x="{x}" y="390" width="414" height="150"/></clipPath></defs>'
        s+=f'<g clip-path="url(#wideclip{ix})">'+reel(x+(125 if ix==0 else 305),573,175,[photo,3,4,5,6],f'wide{ix}')+'</g>'
        s+=label(x+195,436,'One target, one selected photo',10,500,TOK['muted'])
    s+=line(482,91,482,532,'#CFCBBE',1)
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="960" height="540" viewBox="0 0 960 540"><title>Glimpse paired Home and Lock paper reels, wide layout design exploration</title><desc>Two independent destination selectors with no automatic application. Same fixed photo set, one reel for each Android destination. Drawings are design references, not executable software.</desc>'+s+'</svg>'
    p=DIR/(name+'.svg');p.write_text(svg)
    cairosvg.svg2png(bytestring=svg.encode(),write_to=str(ROOT/(name+'.png')),output_width=1600,output_height=900)
    MOCKS[name]={'w':w,'h':h,'svg':str(p),'png':str(ROOT/(name+'.png')),'desc':'Two photo reels side by side on wide screen. Different destinations and stable independent controls; applied outcome explicit.'}

for f in (draw_a,draw_b,draw_b_compact,draw_c,draw_c_simple,svgwide):f()

# produce a curated, readable 16:9 landscape report with visual comparators
pdfmetrics.registerFont(TTFont('Lato', '/usr/share/fonts/truetype/lato/Lato-Regular.ttf'))
pdfmetrics.registerFont(TTFont('LatoBold', '/usr/share/fonts/truetype/lato/Lato-Bold.ttf'))
pdfmetrics.registerFont(TTFont('LatoItalic', '/usr/share/fonts/truetype/lato/Lato-Italic.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuSerif', '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'))
CW,CH=1152,648
C=canvas.Canvas(str(ROOT/'Glimpse_Reel_Layout_Comparison_v1.pdf'),pagesize=(CW,CH),pageCompression=1)
C.setTitle('Glimpse - Purposeful Reel Layout Comparison | 2026-10-22')

def fillrect(x,y,w,h,color,r=0):
 C.setFillColor(HexColor(color))
 if r:C.roundRect(x,y,w,h,r,stroke=0,fill=1)
 else:C.rect(x,y,w,h,stroke=0,fill=1)

def tx(x,y,s,size=18,color='#153F46',bold=False,font=None):
 C.setFillColor(HexColor(color));C.setFont(font or ('LatoBold' if bold else 'Lato'),size);C.drawString(x,y,s)

def txt(x,y,s,sz=15,color='#153F46',leading=None,maxlen=100):
 # normal word wrap on pixel width, approximates with reportlab text width
 leading=leading or sz*1.43
 width=maxlen if isinstance(maxlen,(int,float)) and maxlen>100 else 375
 words=s.split(' '); lines=[];line=''
 for w in words:
  test=(line+' '+w).strip()
  if pdfmetrics.stringWidth(test,'Lato',sz)>width and line:lines.append(line);line=w
  else:line=test
 if line:lines.append(line)
 for j,l in enumerate(lines):tx(x,y-j*leading,l,sz,color)
 return y-len(lines)*leading

def base(kicker,title,subtitle=None,n=1):
 fillrect(0,0,CW,CH,'#F6F0E6');fillrect(0,0,7,CH,'#E8876C')
 tx(42,608,'GLIMPSE / '+kicker,11,'#C56B56',True)
 tx(42,556,title,31,'#153F46',font='DejaVuSerif')
 if subtitle:tx(42,519,subtitle,15,'#667975')
 tx(42,29,'DESIGN EXPLORATION · NOT A RUNNING ANDROID APP',10,'#667975')
 tx(1101,29,f'{n:02d}',11,'#667975')

def photo_mock(name,x,y,h):
 m=MOCKS[name]; iw=h*m['w']/m['h']
 C.drawImage(m['png'],x,y,width=iw,height=h,mask='auto')
 C.setStrokeColor(HexColor('#CFD6CA'));C.setLineWidth(.7);C.rect(x,y,iw,h,stroke=1,fill=0)
 return iw

def note_card(x,y,w,h,head,body,fill='#FFFEFA'):
 fillrect(x,y,w,h,fill,12);tx(x+15,y+h-29,head,15,'#153F46',True);txt(x+15,y+h-52,body,12.5,'#50615D',leading=18,maxlen=w-30)

# cover
base('DECISION STUDY','One motif. Three legitimate jobs.','Same six photographs. Same phone canvas. Different selection meanings.',1)
photo_mock('A_single_photo_reel',77,74,408)
photo_mock('B_asymmetric_collection_photo',318,74,408)
photo_mock('C_destinations_compact',560,74,408)
note_card(794,333,321,146,'A  ·  Photograph','One dominant reel. A photo is selected, then applied separately.')
note_card(794,177,321,146,'B  ·  Collection → Photo','Smaller parent reel changes the child photo set. Neither applies wallpaper.')
note_card(794,73,321,94,'C  ·  Home ↔ Lock','Distinct destination previews. One active wheel on a compact phone.')
C.showPage()

# A and B compare with same frame and explicit cost
base('COMPARISON 01','Does the second reel earn its pixels?','Both show Golden Hour, photo 3 of 6, with precisely the same six fixture photographs.',2)
photo_mock('A_single_photo_reel',62,73,432);photo_mock('B_asymmetric_collection_photo',317,73,432)
note_card(585,332,527,155,'A: single photo reel (baseline)','Large hero; simple hierarchy; conventional collection switching. Best use of compact screen space. The reel has one meaning: browse photographs.')
note_card(585,159,527,161,'B: Collection → Photo (candidate)','Offers a tactile parent selection, but competes with hero height and swipe comfort. It only wins if switching collections is frequent enough to justify the space.')
tx(594,112,'Verdict: prototype B against A, do not replace A by assumption.',14,'#153F46',True)
C.showPage()

base('CAUSALITY','Two reels, two IDs, no accidental wallpaper change.','An asymmetrical visual arrangement is legitimate only when the hierarchy is real.',3)
photo_mock('B_asymmetric_collection_photo',67,68,442)
steps=[('1 / Parent reel','CollectionId: Golden Hour'),('2 / Child photos','ImageAssetId: selected image'),('3 / Main preview','Same ImageAssetId as child focus'),('4 / Apply boundary','Explicit Set wallpaper + target')]
for i,(title,desc) in enumerate(steps):
 y=445-i*103
 fillrect(374,y,700,86,'#FFFDF7',13)
 fillrect(391,y+17,48,48,'#153F46',24)
 tx(405,y+33,str(i+1).zfill(2),18,'#F6F0E6',True)
 tx(465,y+50,title,18,'#153F46',True)
 tx(465,y+22,desc,13,'#667975')
 if i!=3:tx(720,y-14,'↓',17,'#E8876C',True)
C.showPage()

base('COMPARISON 02','Two destinations. One active reel on a phone.','Home and Lock have separate preview IDs, but the user must not lose hero prominence.',4)
photo_mock('C_destinations_tabs_baseline',90,73,429)
photo_mock('C_destinations_compact',362,73,429)
note_card(639,321,478,163,'C0: destination tabs (control)','Unambiguous selection, full hero photograph, no duplicate wheel costs. A strong compact-phone baseline.')
note_card(639,132,478,175,'C1: paired preview (candidate)','The secondary destination is shown as a compact preview and explicit Edit Lock action. A full second rotating wheel would crowd the primary controls.')
C.showPage()

base('ADAPTIVE','Wide windows can support two genuinely independent reels.','On tablets or landscape, two destination choices become legible without shrinking buttons.',5)
C.drawImage(MOCKS['D_destinations_wide_dual']['png'],58,80,width=760,height=427.5)
note_card(840,351,276,169,'Home selector','Own ImageAssetId, image preview, Browse and Apply Home. No coupling to Lock unless user explicitly links selections.')
note_card(840,174,276,164,'Lock selector','Same fixture set, separate state, separate result. If Android cannot set Lock independently, say so and disable apply.')
tx(73,60,'Asymmetry: opposite lower arcs; separation: no shared hitbox.',13,'#667975')
C.showPage()

base('RESPONSIVE','The second reel should be the first thing to disappear.','Compact and large-text layouts preserve one useful wheel plus ordinary named controls.',6)
photo_mock('B_asymmetric_collection_photo',86,75,432)
photo_mock('B_compact_fallback',341,75,432)
note_card(604,310,511,168,'Choose collection is a legitimate fallback','When available height, text scale or insets make two reels cramped, replace the parent with a labeled collection selector. Keep selection semantics exactly the same.')
note_card(604,138,511,157,'What must never collapse','Image identity; Previous / Next photo; View all; explicit Apply destination; OS insets; accessibility semantics. Those are more important than the paper object.')
C.showPage()

base('RISK REVIEW','Where the reel helps, and where it becomes theatre.','Question each interaction from the human goal backward to the exact state changed.',7)
items=[
 ('DO / Photo reel','Browse neighboring photos; focus changes preview only.'),
 ('TEST / Collection reel','Switch named collections; child reel rebinds; rotation unchanged.'),
 ('TEST / Destination pair','Compare Home and Lock with independently applied outcomes.'),
 ('MAYBE / Variant reel','Compare 3–7 alternate crop recipes, not numeric crop controls.'),
 ('NO / General settings','Switches, percentages, permissions, priority and time use native controls.'),
 ('NO / Fake infinity','Show real count and endpoints; five visible holes are not five items.'),
]
for i,(head,body) in enumerate(items):
 col=i%2;row=i//2;x=49+col*547;y=361-row*142
 note_card(x,y,507,126,head,body)
C.showPage()

base('RECOMMENDATION','Start with the simple reel. Earn the second.','Design decisions can remain playful without demanding more animation or navigation.',8)
for y,rank,title,body in [
 (370,'01','Default now: one large Photo reel','Strongest match for browsing; leaves room for hero, Grid and explicit Set wallpaper.'),
 (244,'02','Experiment: Collection → Photo','Genuine hierarchical selector; compare against a normal collection chooser.'),
 (118,'03','Destination view: tabs first, paired reels on wide','Keep two independent preview/application states; promote dual reels only if easier to use.')]:
 fillrect(50,y,1044,112,'#FFFDF7',16)
 fillrect(68,y+24,70,66,'#EBD6B8',18)
 tx(89,y+45,rank,22,'#153F46',True)
 tx(163,y+69,title,20,'#153F46',True)
 txt(163,y+42,body,14,'#5A6F6A',maxlen=880)
C.showPage();C.save()

meta={'document':'Glimpse purposeful reel layout comparison','created':'2026-10-22','status':'visual mockups not app screenshots','fixtures':{f'art{i}.jpg':hashlib.sha256(PHOTOS[i]).hexdigest() for i in range(1,7)},'phoneDimensions':{'width':420,'height':900,'unit':'design units, not device dp'},'scenarios':{k:{'svg':Path(v['svg']).name,'png':Path(v['png']).name,'semantic_note':v['desc']} for k,v in MOCKS.items()},'totalPhotos':6,'collectionCount':3,'canChangeActualWallpaperFromReel':False}
(ROOT/'COMPARISON-MANIFEST.json').write_text(json.dumps(meta,indent=2))
print('Wrote PDF and mockups',len(MOCKS))
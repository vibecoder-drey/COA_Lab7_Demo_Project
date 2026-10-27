"""Static *previews* rendered from the actual HTML form markup.
These are not browser captures or proof of live validation; see README.
"""
from pathlib import Path
import fitz
from bs4 import BeautifulSoup
from weasyprint import HTML
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent
src=BeautifulSoup((P/'static/index.html').read_text(),'html.parser')
OUT=P/'screenshots';OUT.mkdir(exist_ok=True)
labels={'dependent':('Dependent Registration','Major form 01'),'appointment':('Dental Appointment Request','Major form 02'),'search':('Record Search & Filter','Supporting form 01'),'profile':('Employee Profile Update','Supporting form 02')}
errors={'dependent':'Please correct: Dependent full name; Relationship; Date of birth; Contact email; Mobile number; Contact address; Confirmation.','appointment':'Please correct: Registered dependent; Requested dental service; Preferred date; Preferred time; Preferred dentist; Reason for dental visit.','search':'Start date cannot be later than end date.','profile':'Please correct: Email address (enter a valid email format).'}
css='''@page {size:1280px 1100px;margin:0}*{box-sizing:border-box}body{font-family:Arial,sans-serif;margin:0;color:#263d52;background:#f3f6fa;font-size:14px}.sidebar{background:#0b2b3d;color:#fff;width:222px;height:1100px;position:absolute;left:0;top:0;padding:30px 20px}.sidebar h2{font-size:22px;margin:0 0 55px}.sidebar small{font-size:11px;color:#9bd9c9;letter-spacing:2px}.nav{padding:15px 12px;color:#c2d8e5;margin-top:8px;border-radius:8px;font-weight:bold}.active{background:#175866;color:#fff}.main{margin-left:222px;padding:30px 40px}.eyebrow{color:#248d7d;font-size:11px;font-weight:bold;letter-spacing:2px}.main h1{font-size:28px;margin:10px 0}.subtitle{color:#71899c;font-size:13px;margin:0 0 18px}.panel{background:#fff;border:1px solid #dce7ed;border-radius:12px;padding:21px 28px}.type{font-weight:bold;letter-spacing:1px;color:#159a81;font-size:10px}.panel h2{font-size:25px;margin:7px 0}.panel-head p{line-height:1.4;color:#728797;font-size:12px}.notice{background:#e9f7f2;border-left:4px solid #16a185;padding:12px;font-size:12px;color:#336d62;margin:14px 0 20px}.fields{column-count:2;column-gap:18px}.field{break-inside:avoid;display:block;margin:0 0 13px;min-height:61px}.field.wide{column-span:all;min-height:auto}.field label,legend{display:block;font-size:12px;font-weight:bold;margin:0 0 5px}fieldset{border:0;padding:0}.field input:not([type=checkbox]):not([type=radio]),.field select,.field textarea{width:100%;height:39px;border:1px solid #cddde6;border-radius:6px;background:#fff;padding:9px 10px;color:#34495e}.field textarea{height:55px}.field input[type=file]{height:40px}.field input[readonly]{background:#f0f3f6}.field small{display:block;font-size:10px;color:#91a1ad;margin-top:4px}.field.check{min-height:25px}.field.check label{font-weight:normal}.field.check input{vertical-align:middle}.radio-field .inline label{display:inline-block;margin:0 30px 0 0;font-weight:normal}.form-alert{margin:16px 0;padding:14px;background:#fff0f0;border:1px solid #e8b6bd;border-radius:6px;color:#a3313b;font-size:12px}.actions{border-top:1px solid #e3ebf0;margin-top:18px;padding-top:19px}.primary,.secondary{display:inline-block;background:#18967f;color:white;border-radius:7px;padding:12px 19px;font-size:12px;font-weight:bold;border:0;margin-right:12px}.secondary{background:#fff;color:#526879;border:1px solid #ccdbe3}.badge{background:#e8f4ed;color:#2d7f69;border-radius:8px;padding:6px 10px;font-weight:bold;font-size:10px;float:right}.footer{position:absolute;bottom:16px;right:30px;color:#9cabb5;font-size:10px}.invalid{border-color:#e25261!important;background:#fffafa!important}.search-results{font-size:11px;background:#effaf7;padding:9px;color:#237962}.mini{color:#7b8a94;margin-top:8px}'''
nav=''.join(f'<div class="nav {"active" if i==j else ""}">{j+1:02d} &nbsp; {v[0]}</div>' for i,j in [] for v in [])
for idx,(key,(title,cat)) in enumerate(labels.items()):
    sec=src.find(id='panel-'+key)
    form=sec.find('form')
    info=sec.find('div',class_='panel-head')
    notice=sec.find('div',class_='notice')
    form_html=str(form)
    # remove hidden form-alert and ensure print-style button types don't affect screenshot
    for variant in ('form','validation'):
        fh=BeautifulSoup(form_html,'html.parser')
        box=fh.select_one('.form-alert')
        if box:
            if variant=='validation':box.attrs.pop('hidden',None);box.string=errors[key]
            else:box.decompose()
        if variant=='validation':
            for required in fh.select('[required]')[:3]:required['class']=required.get('class',[])+['invalid']
        # WeasyPrint processes actual form HTML to static PDF; JavaScript not executed
        ni=''.join(f'<div class="nav {"active" if j==idx else ""}">{j+1:02d} &nbsp; {v[0]}</div>' for j,(k,v) in enumerate(labels.items()))
        html=f'''<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>
        <aside class="sidebar"><h2>✚ &nbsp;COA Clinic</h2><small>LABORATORY 07</small>{ni}<p style="font-size:11px;color:#9eafbd;margin-top:50px">Fictional test records only</p></aside>
        <div class="main"><span class="eyebrow">CS 301 - SOFTWARE ENGINEERING 1</span><h1>Form Controls Laboratory</h1><p class="subtitle">Four accessible HTML forms with client and server validation</p><span class="badge">{cat.upper()}</span><div class="panel">{str(info)}{str(notice) if notice else ''}{str(fh)}</div></div>
        <div class="footer">STATIC LAYOUT PREVIEW (not a browser screenshot) · {variant.upper()}</div>
        </body></html>'''
        pdf=HTML(string=html,base_url=str(P/'static')).write_pdf()
        doc=fitz.open(stream=pdf,filetype='pdf');page=doc[0]
        pix=page.get_pixmap(matrix=fitz.Matrix(1,1),alpha=False)
        pix.save(str(OUT/f'{idx+1:02d}_{key}_{variant}_PREVIEW.png'))
        print(key,variant,'pages=',len(doc),'size=',pix.width,pix.height)
# Screenshot-like image of actual directory listing, clearly labeled
texts=['COA_Lab7_Forms/', '├── server.py                (Python JSON API + SQLite)', '├── static/', '│   ├── index.html          (4 forms / labeled controls)', '│   ├── styles.css          (accessible styling)', '│   └── app.js              (client-side validation)', '├── data/', '│   └── coa_demo.sqlite3    (fictional demo records)', '├── screenshots/             (layout/error previews)', '├── README.md', '├── test_api.py             (13 automated tests)', '└── DOCUMENTATION.pdf']
img=Image.new('RGB',(1170,650),'#0c1b29');d=ImageDraw.Draw(img)
try:font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',22);heading=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',25)
except:font=ImageFont.load_default();heading=font
d.text((38,22),'PROJECT DIRECTORY STRUCTURE (generated from files)',fill='#75d6c4',font=heading)
for i,s in enumerate(texts):d.text((45,88+i*44),s,fill='#dbe6ee' if i else '#fff',font=font)
img.save(OUT/'09_directory_structure.png')

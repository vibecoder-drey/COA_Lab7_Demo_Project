from pathlib import Path
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,Image,KeepTogether
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.enums import TA_LEFT,TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
BASE=Path(__file__).resolve().parent
O=BASE/'DOCUMENTATION.pdf'
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'; BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
pdfmetrics.registerFont(TTFont('DVS',FONT));pdfmetrics.registerFont(TTFont('DVS-Bold',BOLD))
INK=colors.HexColor('#123346'); TEAL=colors.HexColor('#0E8E7C'); PALE=colors.HexColor('#EAF7F3');GRAY=colors.HexColor('#617485')
styles={
'title':ParagraphStyle('T',fontName='DVS-Bold',fontSize=22,leading=28,textColor=INK,spaceAfter=13),
'h1':ParagraphStyle('H',fontName='DVS-Bold',fontSize=15,leading=20,textColor=INK,spaceAfter=9,spaceBefore=11),
'h2':ParagraphStyle('H2',fontName='DVS-Bold',fontSize=11,leading=15,textColor=TEAL,spaceAfter=7,spaceBefore=7),
'body':ParagraphStyle('B',fontName='DVS',fontSize=9,leading=15,textColor=INK,spaceAfter=8),
'small':ParagraphStyle('S',fontName='DVS',fontSize=7.5,leading=12,textColor=GRAY,spaceAfter=6),
'table':ParagraphStyle('C',fontName='DVS',fontSize=7.7,leading=12,textColor=INK),
'head':ParagraphStyle('TH',fontName='DVS-Bold',fontSize=8,leading=12,textColor=colors.white),
'caption':ParagraphStyle('Cap',fontName='DVS-Bold',fontSize=8,leading=12,textColor=INK,alignment=TA_CENTER,spaceBefore=5),
}
def p(s,style='body'):return Paragraph(s,styles[style])
def tab(data,widths,headers=True):
 rows=[]
 for i,row in enumerate(data):rows.append([p(str(x),'head' if i==0 and headers else 'table') for x in row])
 t=Table(rows,colWidths=widths,repeatRows=1 if headers else 0,hAlign='LEFT')
 cmds=[('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),('LINEBELOW',(0,-1),(-1,-1),.5,colors.HexColor('#DDE6ED'))]
 if headers:cmds += [('BACKGROUND',(0,0),(-1,0),INK),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F5F8FA')])]
 t.setStyle(TableStyle(cmds));return t

def page(canvas,doc):
 canvas.setStrokeColor(colors.HexColor('#DFE8EC'));canvas.line(19*mm,18*mm,190*mm,18*mm)
 canvas.setFont('DVS',7);canvas.setFillColor(GRAY)
 canvas.drawString(19*mm,13*mm,'CS 301 | COA Clinic Form Controls | Demo prototype - fictional data only')
 canvas.drawRightString(190*mm,13*mm,f'{doc.page}')

doc=SimpleDocTemplate(str(O),pagesize=A4,topMargin=19*mm,bottomMargin=25*mm,leftMargin=19*mm,rightMargin=19*mm)
W=172*mm
story=[]
story.append(Spacer(1,23*mm))
story.append(p('CS 301 | LABORATORY ACTIVITY 7','h2'))
story.append(p('Implementing Form Controls<br/>in the Final Project','title'))
story.append(p('<b>Project:</b> Medical and Dental Clinic Management System for the Commission on Audit'))
story.append(p('<b>Team:</b> De Celis, Kurt Renzo E.; Manila, Chelsey C.; Marcellana, Marc Matthew M.; Rodenas, Chad Andrew A.'))
story.append(Spacer(1,5*mm))
story.append(p('<b>Delivered:</b> A standalone, runnable demonstration with two major and two supporting forms; client-side and server-side validation; data handling through Python/SQLite; and rendered form-layout previews.'))
story.append(p('<b>Important boundary:</b> The demo is not merged into the team’s planned Angular / ASP.NET Core codebase, does not use real COA accounts, and must not be used to process actual clinical or payment information.'))
story.append(Spacer(1,4*mm))
story.append(tab([['Form category','Implemented form','Controls'],['Major 1','Employee-linked Dependent Registration','10'],['Major 2','Dental Treatment Appointment Request','10 groups / 11 controls counting both radio buttons'],['Supporting 1','Clinic Record Search &amp; Filter','10'],['Supporting 2','Employee Contact Profile Update','10']],[31*mm,82*mm,59*mm]))
story.append(Spacer(1,7*mm))
story.append(p('What the user must still supply','h2'))
story.append(p('The instructor requires <b>actual screenshots from the running app</b>, a <b>2–4 minute live demo recording</b>, and an assigned <b>GitHub repository with real commits from every group member</b>. Static previews in this package are not substitutes for those items. Use the included demo guide and capture helper on your computer.'))
story.append(PageBreak())
story.append(p('1. Technology and data handling','h1'))
story.append(p('The demonstration uses native HTML inputs, semantic field labels, accessible browser controls and JavaScript client validation. A Python standard-library HTTP server receives JSON API requests, independently validates them, and stores approved demonstration records in an SQLite database.'))
story.append(tab([['Layer','Files / responsibilities'],['User interface','static/index.html and styles.css: four forms, explicit labels, help text, keyboard navigation, visible errors and actions.'],['Client processing','static/app.js: check required fields, valid formats, dates, file size; prevent submission; show errors and database-driven results.'],['Server processing','server.py: API endpoints /api/dependents, /api/appointments, /api/search, and /api/profile, each with backend validation.'],['Storage','data/coa_demo.sqlite3: fictional linked dependent records, appointments and employee contact profile. Created automatically on first run.']],[37*mm,135*mm]))
story.append(Spacer(1,6*mm))
story.append(p('2. Form purpose and implemented controls','h1'))
forms={
'Dependent Registration':('Major 1','Link qualified dependents under an authorized employee account (up to four).',['Employee ID (read-only text)','Dependent full name (text)','Relationship (select)','Date of birth (date)','Eligibility review status (select)','Contact email (email)','Mobile number (telephone)','Eligibility document (file)','Contact address (textarea)','Eligibility confirmation (checkbox)']),
'Dental Appointment Request':('Major 2','Request dental treatment for linked dependents; staff must confirm the request.',['Registered dependent (select)','Treatment type (select)','Preferred date (date)','Preferred time (select)','Preferred dentist (select)','Contact mobile (telephone)','Notification channel (radio group: Email or SMS)','Reason for visit (textarea)','Special assistance (checkbox)','Acknowledgement of staff confirmation (checkbox)']),
'Clinic Record Search':('Supporting 1','Filter saved fictional dependents and dental appointments.',['Search keywords (search input)','Record type (select)','Beneficiary category (select)','Record status (select)','Provider (select)','Date from (date)','Date to (date)','Sort order (select)','Include pending (checkbox)','Exact full-name match (checkbox)']),
'Employee Profile Update':('Supporting 2','Save edited fictional employee contact and emergency-contact information.',['Employee ID (read-only text)','Display name (text)','Email address (email)','Mobile number (telephone)','Department (text)','Office location (text)','Preferred contact channel (select)','Emergency contact name (text)','Emergency mobile (telephone)','Accessibility / communication notes (textarea)'])
}
for name,(category,purpose,fields) in forms.items():
 story.append(p(f'{category}: {name}','h2'));story.append(p(purpose))
 story.append(p('; '.join(fields)+'.','small'))
story.append(PageBreak())
story.append(p('3. Validation rules and anticipated behavior','h1'))
story.append(tab([['Form','Validation / prevented errors','Effect on valid submission'],['Dependent registration','Required fields, email and mobile formats, date range, relationship status, four-dependent cap, file extension, actual file signature and 1 MB maximum.','The linked dependent is saved in SQLite for clinic eligibility review.'],['Dental appointment request','Linked dependent, valid treatment/clinician/time, future date within 90 days, contact number, reason, acknowledgement, conflicting confirmed slot.','Saved as Pending clinic confirmation, not as an automatically confirmed appointment.'],['Record search','Valid optional dates and date-range ordering; filter values are applied on the server.','Filtered records display in a results table and activity log.'],['Profile update','Required name/email/mobile/department/office/emergency fields, valid mobile formats, contact method.','SQLite profile is updated; updated values appear on refresh.']],[37*mm,82*mm,53*mm]))
story.append(Spacer(1,8*mm))
story.append(p('4. Accessibility and usability','h1'))
for x in ['Every visible input has an associated text label (or fieldset legend for the radio group).','Text placeholders and small helper messages explain expected values and upload restrictions.','The page has a skip link, logical navigation order, focus-visible styling and keyboard-operable controls.','Invalid submissions are blocked; the form identifies invalid controls, gives a visible alert, and moves focus to the first invalid field.','Buttons use explicit action labels, and success/error messages are exposed through accessible status regions.']:
 story.append(p('• '+x))
story.append(PageBreak())
for i,(slug, name) in enumerate([('dependent','Dependent Registration'),('appointment','Dental Appointment Request'),('search','Clinic Record Search'),('profile','Employee Profile Update')],start=1):
 story.append(p(f'5.{i} Layout previews — {name}','h1'))
 story.append(p('The previews below are rendered directly from the form HTML. They illustrate layout and validation messaging, but are <b>not</b> screenshots of a live browser session. Capture live states on your own computer for the instructor.','small'))
 cells=[]
 for state in ('form','validation'):
  path=BASE/'screenshots'/f'{i:02d}_{slug}_{state}_PREVIEW.png'
  cells.append(Image(str(path),width=81*mm,height=69.6*mm))
 imgs=Table([cells],colWidths=[86*mm,86*mm],hAlign='LEFT');imgs.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),2),('RIGHTPADDING',(0,0),(-1,-1),2)]));story.append(imgs)
 story.append(p('Left: initial form layout. Right: illustrative required-field or validation-error state.','caption'))
 story.append(Spacer(1,5*mm))
 if slug=='dependent':s='The backend enforces the four-dependent limit and only links records to the demo employee. A proof-file input is validated; only file metadata is retained in this prototype.'
 elif slug=='appointment':s='The backend rejects a slot already confirmed for a selected dentist and saves valid requests as pending clinic confirmation.'
 elif slug=='search':s='Search inputs are sent to the server. Optional filters control which sample records appear in the results table.'
 else:s='Invalid email and telephone fields are rejected. A valid profile change persists to the fictional employee record in SQLite.'
 story.append(p(s))
 story.append(PageBreak())
story.append(p('6. Actual backend verification','h1'))
story.append(p('<b>13 automated Python tests passed.</b> The test suite checks: seeded fictional data, valid/invalid dependent registration, max-four restriction, invalid phone, pending appointment status, slot conflicts, unacknowledged request, record searching, impossible date ranges, profile edits, bad email, and a forged file signature.'))
story.append(p('<b>To rerun:</b> <font name="DVS-Bold">python -m unittest -v test_api.py</font> from the project directory. Browser layout previews are static renders and do not replace live browser tests.'))
story.append(Spacer(1,4*mm))
story.append(p('7. Screenshot of project directory structure','h1'))
img=Image(str(BASE/'screenshots/09_directory_structure.png'),width=155*mm,height=86.1*mm)
story.append(img)
story.append(p('Directory listing generated from the actual submitted source files.','caption'))
story.append(Spacer(1,5*mm))
story.append(p('8. How to run and capture real submission evidence','h1'))
story.append(p('1. Run <b>python server.py</b> (Python 3.9 or newer).<br/>2. Open <b>http://127.0.0.1:8765</b> in Chrome, Firefox or Edge.<br/>3. Capture all four visible forms and each validation state using your browser’s screenshot tool.<br/>4. Record an actual 2–4 minute browser session following DEMO_VIDEO_GUIDE.md.<br/>5. Push the actual team contributions to your assigned GitHub repository. Supply the real URL and each member’s commits.'))
story.append(p('A standalone prototype is not a substitute for integration into the team’s final Angular/ASP.NET Core project. Include integration evidence only if the group has actually completed it.','small'))
doc.build(story,onFirstPage=page,onLaterPages=page)
print(O,O.stat().st_size)

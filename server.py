"""COA Lab 7 form-control demonstration. Fictional test data only.
Run: python server.py | Open: http://127.0.0.1:8765
Uses only Python standard library (SQLite + HTTP server).
NOT production authentication, medical records, or payment processing.
"""
from __future__ import annotations
import base64, binascii, datetime as dt, json, mimetypes, re, sqlite3, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

BASE = Path(__file__).resolve().parent
DB = BASE / 'data' / 'coa_demo.sqlite3'
EMPLOYEE = 'COA-DEMO-001'
MAX_BODY = 2_300_000
lock = threading.Lock()

def db():
    con=sqlite3.connect(DB, timeout=10)
    con.row_factory=sqlite3.Row
    con.execute('PRAGMA foreign_keys=ON')
    return con

def init_db():
    DB.parent.mkdir(exist_ok=True)
    with db() as c:
        c.executescript('''
        CREATE TABLE IF NOT EXISTS profile (employee_id TEXT PRIMARY KEY, full_name TEXT NOT NULL, email TEXT NOT NULL, phone TEXT NOT NULL, department TEXT NOT NULL, office TEXT NOT NULL, contact_method TEXT NOT NULL, emergency_name TEXT NOT NULL, emergency_phone TEXT NOT NULL, accessibility_notes TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS dependents (id INTEGER PRIMARY KEY AUTOINCREMENT, employee_id TEXT NOT NULL, full_name TEXT NOT NULL, relationship TEXT NOT NULL, birth_date TEXT NOT NULL, eligibility TEXT NOT NULL, email TEXT NOT NULL, phone TEXT NOT NULL, address TEXT NOT NULL, proof_filename TEXT NOT NULL, proof_bytes INTEGER NOT NULL, accepted INTEGER NOT NULL, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS appointments (id INTEGER PRIMARY KEY AUTOINCREMENT, employee_id TEXT NOT NULL, dependent_id INTEGER NOT NULL, treatment TEXT NOT NULL, day TEXT NOT NULL, slot TEXT NOT NULL, dentist TEXT NOT NULL, notes TEXT NOT NULL, phone TEXT NOT NULL, notify TEXT NOT NULL, assistance INTEGER NOT NULL, status TEXT NOT NULL, created_at TEXT NOT NULL, FOREIGN KEY(dependent_id) REFERENCES dependents(id));
        ''')
        if not c.execute('SELECT 1 FROM profile WHERE employee_id=?', (EMPLOYEE,)).fetchone():
            c.execute('INSERT INTO profile VALUES (?,?,?,?,?,?,?,?,?,?)', (EMPLOYEE,'Alex Rivera (Demo)','alex@example.test','09170000000','Operations','COA Central Office','Email','Jordan Rivera (Demo)','09171111111','None'))
        if not c.execute('SELECT 1 FROM dependents').fetchone():
            today=dt.datetime.now().isoformat(timespec='seconds')
            for name, rel, dob in [('Jamie Rivera (Demo)','Child','2014-02-15'),('Taylor Rivera (Demo)','Spouse','1994-05-24')]:
                c.execute('INSERT INTO dependents (employee_id,full_name,relationship,birth_date,eligibility,email,phone,address,proof_filename,proof_bytes,accepted,created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)', (EMPLOYEE,name,rel,dob,'For clinic verification','demo@example.test','09170000000','Fictional example address','','0',1,today))
        if not c.execute('SELECT 1 FROM appointments').fetchone():
            tomorrow = (dt.date.today()+dt.timedelta(days=1)).isoformat()
            depid=c.execute('SELECT id FROM dependents ORDER BY id LIMIT 1').fetchone()['id']
            c.execute('INSERT INTO appointments (employee_id, dependent_id,treatment,day,slot,dentist,notes,phone,notify,assistance,status,created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)', (EMPLOYEE,depid,'Dental examination',tomorrow,'09:00','Dr. Santos (Demo)','Seeded confirmed slot','09170000000','Email',0,'Confirmed',dt.datetime.now().isoformat(timespec='seconds')))

def clean(x, maxlen=200):
    return str(x or '').strip()[:maxlen]

def required(data, fields):
    names=[f for f in fields if not clean(data.get(f))]
    if names: raise ValueError('Please complete: '+', '.join(names).replace('_',' ')+'.')

def valid_email(v): return bool(re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+',v))
def valid_phone(v): return bool(re.fullmatch(r'(?:\+63|0)9\d{9}',v))

def record_dependent(data):
    required(data,['full_name','relationship','birth_date','eligibility','email','phone','address'])
    if data.get('employee_id')!=EMPLOYEE: raise ValueError('Unknown demo employee account.')
    if not data.get('accepted'): raise ValueError('Eligibility information confirmation is required.')
    if len(clean(data['full_name'],100))<3: raise ValueError('Dependent name must have at least 3 characters.')
    if data['relationship'] not in ('Child','Spouse','Parent','Other qualified dependent'): raise ValueError('Select a valid relationship.')
    if data['eligibility'] not in ('For clinic verification','Verified by clinic'): raise ValueError('Select an eligibility status.')
    try: dob=dt.date.fromisoformat(data['birth_date'])
    except: raise ValueError('Provide a valid birth date.')
    if dob>dt.date.today() or dob<dt.date.today()-dt.timedelta(days=120*366): raise ValueError('Birth date is out of range.')
    if not valid_email(clean(data['email'])) or not valid_phone(clean(data['phone'])): raise ValueError('Enter a valid email and Philippine mobile number.')
    fname=''; raw=b''
    if data.get('proof_file'):
        obj=data['proof_file'];fname=clean(obj.get('name'),100)
        try:raw=base64.b64decode(obj.get('data',''),validate=True)
        except (binascii.Error,ValueError):raise ValueError('Invalid uploaded file.')
        if len(raw)>1024*1024: raise ValueError('Proof file cannot exceed 1 MB.')
        if not (fname.lower().endswith(('.pdf','.png','.jpg','.jpeg')) and (raw.startswith(b'%PDF-') or raw.startswith(b'\x89PNG\r\n\x1a\n') or raw.startswith(b'\xff\xd8\xff'))): raise ValueError('Proof must be a valid PDF, PNG, or JPEG file.')
    with lock,db() as c:
        count=c.execute('SELECT COUNT(*) FROM dependents WHERE employee_id=?',(EMPLOYEE,)).fetchone()[0]
        if count>=4: raise ValueError('Maximum of four registered dependents has been reached.')
        cur=c.execute('INSERT INTO dependents (employee_id,full_name,relationship,birth_date,eligibility,email,phone,address,proof_filename,proof_bytes,accepted,created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)', (EMPLOYEE,clean(data['full_name'],100),data['relationship'],data['birth_date'],data['eligibility'],clean(data['email']),clean(data['phone']),clean(data['address'],400),fname,len(raw),1,dt.datetime.now().isoformat(timespec='seconds')))
        return {'message':'Dependent added for clinic review (demo).','dependent_id':cur.lastrowid}

def request_appointment(data):
    required(data,['dependent_id','treatment','day','slot','dentist','notes','phone','notify'])
    if not data.get('acknowledge'): raise ValueError('Please acknowledge that requests require staff confirmation.')
    if data['treatment'] not in ('Dental examination','Oral prophylaxis','Tooth restoration','Tooth extraction'): raise ValueError('Unsupported proposed treatment type.')
    if data['dentist'] not in ('Dr. Santos (Demo)','Dr. Cruz (Demo)') or data['slot'] not in ('09:00','10:00','11:00','13:00','14:00','15:00'): raise ValueError('Invalid clinician or time slot.')
    if data['notify'] not in ('Email','SMS'): raise ValueError('Choose a notification method.')
    if not valid_phone(clean(data['phone'])): raise ValueError('Provide a valid Philippine mobile number.')
    try:day=dt.date.fromisoformat(data['day'])
    except:raise ValueError('Provide a valid appointment date.')
    if not dt.date.today()<day<=dt.date.today()+dt.timedelta(days=90):raise ValueError('Choose a future date within 90 days.')
    with lock,db() as c:
        if not c.execute('SELECT 1 FROM dependents WHERE id=? AND employee_id=?',(data['dependent_id'],EMPLOYEE)).fetchone():raise ValueError('Select a dependent registered under the demo account.')
        if c.execute("SELECT 1 FROM appointments WHERE day=? AND slot=? AND dentist=? AND status='Confirmed'",(data['day'],data['slot'],data['dentist'])).fetchone():raise ValueError('That dentist already has a confirmed appointment at the selected time.')
        cur=c.execute('INSERT INTO appointments (employee_id,dependent_id,treatment,day,slot,dentist,notes,phone,notify,assistance,status,created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)', (EMPLOYEE,int(data['dependent_id']),data['treatment'],data['day'],data['slot'],data['dentist'],clean(data['notes'],700),data['phone'],data['notify'],int(bool(data.get('assistance'))),'Pending clinic confirmation',dt.datetime.now().isoformat(timespec='seconds')))
        return {'message':'Appointment request saved as PENDING clinic confirmation.','appointment_id':cur.lastrowid}

def search_records(data):
    with db() as c:
        ds=[dict(x) for x in c.execute('SELECT * FROM dependents WHERE employee_id=?',(EMPLOYEE,)).fetchall()]
        apps=[dict(x) for x in c.execute('''SELECT appointments.*, dependents.full_name AS name FROM appointments JOIN dependents ON dependents.id=appointments.dependent_id WHERE appointments.employee_id=?''',(EMPLOYEE,)).fetchall()]
    rows=[{'type':'Dependent','name':d['full_name'],'detail':d['relationship'],'date':d['created_at'][:10],'status':d['eligibility'],'provider':'Clinic staff'} for d in ds]
    rows +=[{'type':'Appointment','name':a['name'],'detail':a['treatment']+' · '+a['slot'],'date':a['day'],'status':a['status'],'provider':a['dentist']} for a in apps]
    q=clean(data.get('query'),100).lower()
    if q: rows=[r for r in rows if q in ' '.join(map(str,r.values())).lower()]
    if data.get('record_type') in ('Dependent','Appointment'):rows=[r for r in rows if r['type']==data['record_type']]
    if data.get('status','All') not in ('','All'):rows=[r for r in rows if r['status']==data['status']]
    if data.get('provider','All') not in ('','All'):rows=[r for r in rows if r['provider']==data['provider']]
    try:
        if data.get('date_from'):dt.date.fromisoformat(data['date_from']);rows=[r for r in rows if r['date']>=data['date_from']]
        if data.get('date_to'):dt.date.fromisoformat(data['date_to']);rows=[r for r in rows if r['date']<=data['date_to']]
    except ValueError:raise ValueError('Invalid search date.')
    if data.get('date_from') and data.get('date_to') and data['date_from']>data['date_to']:raise ValueError('Start date cannot be later than end date.')
    if data.get('beneficiary')=='Dependent only':rows=[r for r in rows if r['type']=='Dependent']
    if not data.get('include_pending'):rows=[r for r in rows if r['status']!='Pending clinic confirmation']
    if data.get('exact_match') and q:rows=[r for r in rows if r['name'].lower()==q]
    rows.sort(key=lambda r:r['date'],reverse=data.get('sort')!='Oldest first')
    return {'message':f'{len(rows)} record(s) match the filters.','records':rows[:50]}

def update_profile(data):
    required(data,['full_name','email','phone','department','office','contact_method','emergency_name','emergency_phone'])
    if data.get('employee_id')!=EMPLOYEE:raise ValueError('Employee account cannot be changed in demo.')
    if not valid_email(clean(data['email'])):raise ValueError('Provide a valid email address.')
    if not valid_phone(clean(data['phone'])) or not valid_phone(clean(data['emergency_phone'])):raise ValueError('Provide valid Philippine mobile numbers.')
    if data['contact_method'] not in ('Email','SMS','Phone call'):raise ValueError('Select a valid contact preference.')
    with lock,db() as c:
        c.execute('UPDATE profile SET full_name=?,email=?,phone=?,department=?,office=?,contact_method=?,emergency_name=?,emergency_phone=?,accessibility_notes=? WHERE employee_id=?',tuple(clean(data[f],400 if f=='accessibility_notes' else 100) for f in ('full_name','email','phone','department','office','contact_method','emergency_name','emergency_phone','accessibility_notes'))+(EMPLOYEE,))
    return {'message':'Demo profile updated in SQLite successfully.'}

def state():
    with db() as c:
        prof=dict(c.execute('SELECT * FROM profile WHERE employee_id=?',(EMPLOYEE,)).fetchone())
        deps=[dict(x) for x in c.execute('SELECT id,full_name,relationship,eligibility FROM dependents WHERE employee_id=? ORDER BY id',(EMPLOYEE,))]
        apps=[dict(x) for x in c.execute('SELECT id,treatment,day,slot,dentist,status FROM appointments WHERE employee_id=? ORDER BY id DESC LIMIT 5',(EMPLOYEE,))]
        return {'profile':prof,'dependents':deps,'appointments':apps,'max_dependents':4}

class Handler(BaseHTTPRequestHandler):
    def log_message(self,fmt,*args): pass
    def send_json(self,obj,status=200):
        body=json.dumps(obj).encode('utf-8')
        self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
    def do_GET(self):
        path=urlparse(self.path).path
        if path=='/api/state':return self.send_json(state())
        static={'/':'index.html','/index.html':'index.html','/styles.css':'styles.css','/app.js':'app.js'}
        if path not in static:return self.send_json({'error':'Not found.'},404)
        f=BASE/'static'/static[path]
        body=f.read_bytes();self.send_response(200);self.send_header('Content-Type',mimetypes.guess_type(str(f))[0] or 'text/html');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
    def do_POST(self):
        path=urlparse(self.path).path
        handlers={'/api/dependents':record_dependent,'/api/appointments':request_appointment,'/api/search':search_records,'/api/profile':update_profile}
        if path not in handlers:return self.send_json({'error':'Not found.'},404)
        try:
            ln=int(self.headers.get('Content-Length','0'))
            if not 0<ln<=MAX_BODY:raise ValueError('Request is empty or too large.')
            data=json.loads(self.rfile.read(ln))
            if not isinstance(data,dict):raise ValueError('Invalid request body.')
            ans=handlers[path](data)
            self.send_json({'ok':True,**ans})
        except (ValueError,TypeError,KeyError) as e:self.send_json({'ok':False,'error':str(e)},400)
        except Exception:self.send_json({'ok':False,'error':'Unexpected demo server error.'},500)

if __name__=='__main__':
    init_db()
    print('COA Lab 7 (fictional records only): http://127.0.0.1:8765',flush=True)
    ThreadingHTTPServer(('127.0.0.1',8765),Handler).serve_forever()

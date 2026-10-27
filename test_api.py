"""Standard-library unit tests for the lab backend (fictional demo only)."""
import tempfile, unittest
from pathlib import Path
import server

class FormTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        server.DB=Path(self.tmp.name)/'test.sqlite3'
        server.init_db()
    def tearDown(self):self.tmp.cleanup()
    def dep(self, n='Morgan Rivera (Demo)'):
        return {'employee_id':server.EMPLOYEE,'full_name':n,'relationship':'Child','birth_date':'2016-06-18','eligibility':'For clinic verification','email':'morgan@example.test','phone':'09178888888','address':'Fictional demo address','accepted':True}
    def appt(self):
        from datetime import date,timedelta
        return {'dependent_id':server.state()['dependents'][0]['id'],'treatment':'Dental examination','day':(date.today()+timedelta(days=3)).isoformat(),'slot':'10:00','dentist':'Dr. Cruz (Demo)','notes':'Routine evaluation demo','phone':'09178888888','notify':'Email','acknowledge':True,'assistance':False}
    def test_initial_seed(self):
        r=server.state();self.assertEqual(len(r['dependents']),2);self.assertEqual(len(r['appointments']),1)
    def test_dependent_valid(self):
        r=server.record_dependent(self.dep());self.assertEqual(r['dependent_id'],3)
    def test_dependent_required_fields(self):
        with self.assertRaisesRegex(ValueError,'Please complete'):server.record_dependent({'employee_id':server.EMPLOYEE})
    def test_dependent_phone(self):
        d=self.dep();d['phone']='555';
        with self.assertRaisesRegex(ValueError,'valid email'):server.record_dependent(d)
    def test_dependent_max_four(self):
        server.record_dependent(self.dep('Morgan Rivera (Demo)'))
        server.record_dependent(self.dep('Robin Rivera (Demo)'))
        with self.assertRaisesRegex(ValueError,'Maximum of four'):server.record_dependent(self.dep('Pat Rivera (Demo)'))
    def test_dental_request_pending(self):
        r=server.request_appointment(self.appt());self.assertTrue(r['appointment_id']);self.assertIn('PENDING',r['message'])
    def test_dental_confirmed_collision(self):
        from datetime import date,timedelta
        d=self.appt();d.update(day=(date.today()+timedelta(days=1)).isoformat(),slot='09:00',dentist='Dr. Santos (Demo)')
        with self.assertRaisesRegex(ValueError,'confirmed appointment'):server.request_appointment(d)
    def test_dental_staff_confirmation_required(self):
        d=self.appt();d['acknowledge']=False
        with self.assertRaisesRegex(ValueError,'acknowledge'):server.request_appointment(d)
    def test_search(self):
        r=server.search_records({'query':'rivera','include_pending':True});self.assertGreaterEqual(len(r['records']),3)
    def test_search_bad_date(self):
        with self.assertRaisesRegex(ValueError,'Start date'):server.search_records({'date_from':'2026-11-12','date_to':'2026-11-01','include_pending':True})
    def test_profile_valid(self):
        p=server.state()['profile'];p['email']='updated@example.test';r=server.update_profile(p);self.assertIn('updated',r['message']);self.assertEqual(server.state()['profile']['email'],'updated@example.test')
    def test_profile_reject_bad_email(self):
        p=server.state()['profile'];p['email']='invalid'
        with self.assertRaisesRegex(ValueError,'valid email'):server.update_profile(p)
    def test_unsupported_file(self):
        import base64
        d=self.dep();d['proof_file']={'name':'fake.pdf','data':base64.b64encode(b'not pdf').decode()}
        with self.assertRaisesRegex(ValueError,'valid PDF'):server.record_dependent(d)

if __name__=='__main__':unittest.main(verbosity=2)

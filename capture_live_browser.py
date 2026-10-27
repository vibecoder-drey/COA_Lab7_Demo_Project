"""OPTIONAL: run locally after installing Playwright and browser to capture real screenshots.

Requires: pip install playwright; python -m playwright install chromium
Must have server.py running at localhost:8765.
"""
from datetime import date,timedelta
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image
BASE=Path(__file__).resolve().parent
S=BASE/'screenshots'; S.mkdir(exist_ok=True)
valid_day=(date.today()+timedelta(days=3)).isoformat()
conflict_day=(date.today()+timedelta(days=1)).isoformat()
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True)
 p=b.new_page(viewport={'width':1440,'height':900}, device_scale_factor=1)
 p.goto('http://127.0.0.1:8765/',wait_until='networkidle')
 p.screenshot(path=str(S/'01_dependent_form.png'),full_page=True)
 p.locator('#form-dependent button[type=submit]').click()
 assert p.locator('#dependent-alert').is_visible()
 p.screenshot(path=str(S/'02_dependent_validation.png'),full_page=True)
 p.fill('#d-name','Morgan Rivera (Demo)');p.select_option('#d-rel','Child');p.fill('#d-dob','2016-06-18');p.select_option('#d-elig','For clinic verification');p.fill('#d-email','morgan@example.test');p.fill('#d-phone','09178888888');p.fill('#d-address','Fictional Avenue, Quezon City');p.check('#d-ack')
 p.locator('#form-dependent button[type=submit]').click();p.wait_for_timeout(350)
 assert 'Dependent added' in p.locator('#dependent-alert').inner_text(),p.locator('#dependent-alert').inner_text()
 p.screenshot(path=str(S/'03_dependent_saved.png'),full_page=True)
 p.locator('[data-target=appointment]').click()
 p.screenshot(path=str(S/'04_appointment_form.png'),full_page=True)
 p.locator('#form-appointment button[type=submit]').click();assert p.locator('#appointment-alert').is_visible()
 p.screenshot(path=str(S/'05_appointment_validation.png'),full_page=True)
 p.select_option('#a-dep',label='Morgan Rivera (Demo)');p.select_option('#a-treatment','Dental examination');p.fill('#a-day',valid_day);p.select_option('#a-slot','10:00');p.select_option('#a-dentist','Dr. Cruz (Demo)');p.fill('#a-phone','09178888888');p.check('input[name=notify][value=Email]');p.fill('#a-notes','Routine dental examination for test data.');p.check('input[name=acknowledge]')
 p.locator('#form-appointment button[type=submit]').click();p.wait_for_timeout(300)
 assert 'PENDING' in p.locator('#appointment-alert').inner_text(),p.locator('#appointment-alert').inner_text()
 p.screenshot(path=str(S/'06_appointment_saved_pending.png'),full_page=True)
 p.select_option('#a-dep',label='Morgan Rivera (Demo)');p.select_option('#a-treatment','Oral prophylaxis');p.fill('#a-day',conflict_day);p.select_option('#a-slot','09:00');p.select_option('#a-dentist','Dr. Santos (Demo)');p.fill('#a-phone','09178888888');p.check('input[name=notify][value=Email]');p.fill('#a-notes','Test booked slot rejection');p.check('input[name=acknowledge]')
 p.locator('#form-appointment button[type=submit]').click();p.wait_for_timeout(200)
 assert 'confirmed appointment' in p.locator('#appointment-alert').inner_text(),p.locator('#appointment-alert').inner_text()
 p.screenshot(path=str(S/'07_appointment_conflict_error.png'),full_page=True)
 p.locator('[data-target=search]').click();p.screenshot(path=str(S/'08_search_form.png'),full_page=True)
 p.locator('#form-search button[type=submit]').click();p.wait_for_timeout(200)
 assert 'record(s)' in p.locator('#search-alert').inner_text()
 p.screenshot(path=str(S/'09_search_results.png'),full_page=True)
 p.fill('#s-from',valid_day);p.fill('#s-to',conflict_day)
 p.locator('#form-search button[type=submit]').click()
 assert p.locator('#search-alert').is_visible()
 p.screenshot(path=str(S/'10_search_date_error.png'),full_page=True)
 p.locator('[data-target=profile]').click();p.screenshot(path=str(S/'11_profile_form.png'),full_page=True)
 p.fill('#p-email','not-an-email');p.locator('#form-profile button[type=submit]').click()
 assert p.locator('#profile-alert').is_visible()
 p.screenshot(path=str(S/'12_profile_validation.png'),full_page=True)
 p.fill('#p-email','alex.updated@example.test');p.fill('#p-name','Alex Rivera (Demo - Updated)')
 p.locator('#form-profile button[type=submit]').click();p.wait_for_timeout(250)
 assert 'updated' in p.locator('#profile-alert').inner_text(),p.locator('#profile-alert').inner_text()
 p.screenshot(path=str(S/'13_profile_saved.png'),full_page=True)
 print('PASS: 4 normal forms, 4 error states, 4 UI persistence outcomes and seeded booking conflict')
 b.close()

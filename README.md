# CS 301 Laboratory 7 — Form Controls Prototype

**Project:** Medical and Dental Clinic Management System for the Commission on Audit (COA)

## Important status
This is a **standalone working laboratory prototype**, not the existing team's Angular/ASP.NET Core implementation. It uses HTML/CSS/JavaScript, Python's built-in HTTP server, and SQLite to demonstrate real form handling without installing packages. All seeded data is **fictional**. There is NO real authentication, medical-record system, cashier integration, payment handling, or production deployment security. **Do not enter real personal or medical data.**

## Run
Requirements: Python 3.9+.

```bash
python server.py
```

Open <http://127.0.0.1:8765>. The database is initialized automatically at `data/coa_demo.sqlite3`. Delete it while the server is stopped to reset fictional demo data. No internet or external packages are required.

## Four forms, ten input controls each

| Form | Category | Fields |
|---|---|---|
| Employee-linked Dependent Registration | Major 1 | Employee ID (read-only), full name, relationship, birth date, eligibility status, contact email, mobile number, eligibility document upload, contact address, confirmation checkbox |
| Dental Treatment Appointment Request | Major 2 | Dependent, treatment, preferred date, time, dentist, mobile, notification radio buttons, visit reason, special assistance checkbox, staff-confirmation acknowledgement checkbox |
| Record Search and Filter | Supporting 1 | Keywords, record type, beneficiary, status, provider, date from, date to, sort, include pending checkbox, exact match checkbox |
| Employee Profile Update | Supporting 2 | Employee ID (read-only), display name, email, phone, department, office, contact channel, emergency contact name, emergency mobile, accessibility notes |

Each form also has descriptive submit/reset actions. Native input types, visible labels, helper text, keyboard focus, and accessible alert/status areas are implemented.

## Validation and behavior

- Browser: required fields, valid email, phone pattern (`09XXXXXXXXX` / `+639XXXXXXXXX`), date selection, text lengths, 1 MB image/PDF file limit, missing checkboxes, invalid date range. Errors prevent submission and focus an invalid field.
- Server: repeat validations for dependent eligibility, maximum of four linked dependents, malformed birthdates, invalid phone/email/file signatures, invalid appointment dates and slots, assignment to linked dependent, collision against **confirmed** dentist bookings, invalid record date ranges, and authorization placeholder for employee account.
- Database: successful dependent registrations, appointment requests (`Pending clinic confirmation`), and profile changes persist in SQLite. Search sends filters to backend and displays matching records. The side panel refreshes with saved rows. New appointments are **not automatically confirmed**.
- File data: a valid file's **name and byte count** are recorded; the file contents are not retained. This is sufficient to demonstrate HTML file input, validation and backend handling but **not a production secure upload feature**. Do not assert that actual clinic documents have been uploaded or retained.

## Screenshots and video
See `screenshots/` for captures of each form, validation errors, and successful interactions. If included, `demo.mp4` is a captioned demonstration assembled from actual browser captures and tests.

## Directory structure

```
COA_Lab7_Forms/
├── server.py                  # HTTP endpoints, validation, and SQLite
├── static/
│   ├── index.html             # Four accessible form controls
│   ├── styles.css             # Responsive UI
│   └── app.js                 # Client validation, submissions, UI
├── data/
│   └── coa_demo.sqlite3       # Automatically created from fictional seed data
├── screenshots/
│   └── *.png                  # Form / validation captures
├── demo.mp4                   # Demonstration (if supplied)
├── DOCUMENTATION.pdf          # Submission writeup
└── README.md
```

## GitHub team-commit requirement (team must complete)

This ZIP has no authentic GitHub repository URL or group member commit history. Use your **assigned repository**, have each member commit a real contribution, and then include the actual repository link in the submitted answer sheet or Canvas comments. Do not claim fictional commits.

Suggested division: member A (dependent form), B (appointment form), C (search + accessibility), D (profile + documentation + testing). Merge using pull requests if your team already uses them.

## Integration into final Angular / ASP.NET Core project

The HTML forms demonstrate inputs and user flow. To incorporate them into the project, recreate their controls as Angular reactive forms (`FormGroup` / validators), adapt these API payloads to ASP.NET Core controller DTOs with server-side ModelState validation, and use your project's authorized EF Core/SQL Server tables, JWT identity and role rules. No repository integration is claimed here.

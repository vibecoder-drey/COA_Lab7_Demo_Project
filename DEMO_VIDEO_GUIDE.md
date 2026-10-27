# 2–4 Minute Demo Recording Guide (real screen capture)

**Record the live browser on your own machine.** The included preview images and optional video storyboard are not evidence of live behavior.

1. Start the app: `python server.py`; open `http://127.0.0.1:8765`.
2. Use a screen recorder (e.g., built-in Windows Snipping Tool recorder, macOS Screenshot Shift-Command-5, OBS, or Google Meet recording where permitted).
3. Target **2:45 total**, with the following narrated timeline:

| Timeline | What to demonstrate | Narration |
|---|---|---|
| 0:00–0:20 | Open app, four forms, SQLite status panel | “These are two major and two supporting COA clinic forms. We use fictional data only.” |
| 0:20–0:55 | Dependent: submit empty → error, complete fictional fields → save | “Required fields and formats are checked; records are linked to the employee and restricted to four dependents.” |
| 0:55–1:30 | Dental appointment: submit empty → error, then submit valid request | “The request is pending, not automatically confirmed; confirmed-slot conflicts are rejected.” |
| 1:30–1:55 | Search and filters: find fictitious records; show date error | “Search fields are processed by the server and results are displayed in the interface.” |
| 1:55–2:15 | Profile: invalid email → error, valid change → save | “Client and server validation block invalid entries; updates persist in SQLite.” |
| 2:15–2:35 | Refresh browser to confirm saved data; open code directory | “Data is stored in the local database. The project has separated HTML, CSS, JavaScript, and Python code.” |
| 2:35–2:45 | GitHub assigned repository, show real contributor commits | “Each team member committed their contributions to our assigned repository.” *(Only say this if true.)* |

**Important:** Record the actual interaction and resulting behavior, not the static layout preview. Use a real assigned GitHub repository URL and genuine commits from every student before uploading to Canvas. The prototype is not yet merged with the actual Angular / ASP.NET Core app.

Export to MP4 (preferred) and check the runtime is between 2 and 4 minutes. Upload all requested items and list members in the submission comments.

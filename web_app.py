from flask import Flask, request, redirect, Response
import json
from pathlib import Path

app = Flask(__name__)
DATA_FILE = Path(__file__).with_name("students.json")


# -------------------------
# Data helpers
# -------------------------
def load_students():
    if DATA_FILE.exists():
        try:
            data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except json.JSONDecodeError:
            return []
    return []


def save_students(students):
    DATA_FILE.write_text(json.dumps(students, indent=2), encoding="utf-8")


def find_by_id(students, sid: str):
    sid = sid.strip()
    for s in students:
        if str(s.get("id", "")).strip() == sid:
            return s
    return None


def h(text):
    """Tiny HTML escape"""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


# -------------------------
# Stats helpers
# -------------------------
def to_int(x, default=0):
    try:
        return int(x)
    except Exception:
        return default


def compute_stats(students):
    total = len(students)

    ages = [to_int(s.get("age", 0), 0) for s in students]
    ages = [a for a in ages if a > 0]

    avg_age = round(sum(ages) / len(ages), 1) if ages else 0
    min_age = min(ages) if ages else 0
    max_age = max(ages) if ages else 0

    degree_counts = {}
    for s in students:
        deg = str(s.get("degree", "")).strip() or "Unknown"
        degree_counts[deg] = degree_counts.get(deg, 0) + 1

    degree_sorted = sorted(degree_counts.items(), key=lambda x: x[1], reverse=True)

    return {
        "total": total,
        "avg_age": avg_age,
        "min_age": min_age,
        "max_age": max_age,
        "degrees": degree_sorted,
    }


# -------------------------
# UI layout
# -------------------------
def layout(title, content, msg=""):
    alert = f"""<div class="alert">{h(msg)}</div>""" if msg else ""
    return f"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{h(title)}</title>
  <style>
    :root {{
      --bg: #0b1220;
      --card: rgba(16,26,51,.75);
      --line: rgba(255,255,255,.10);
      --text: #eaf0ff;
      --muted: #9fb0d0;
      --accent: #6aa6ff;
      --ok: #22c55e;
      --danger: #ef4444;
    }}
    * {{ box-sizing:border-box; }}
    body {{
      margin:0;
      font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial;
      background: radial-gradient(1200px 600px at 15% 10%, #14234a 0%, var(--bg) 55%),
                  radial-gradient(900px 500px at 90% 30%, #1a2c5f 0%, var(--bg) 55%);
      color: var(--text);
    }}
    .wrap {{ max-width: 1100px; margin: 28px auto; padding: 0 16px 40px; }}
    .top {{
      display:flex; justify-content:space-between; align-items:flex-end; gap:12px;
      margin-bottom: 16px;
    }}
    h1 {{ margin:0; font-size:28px; }}
    .sub {{ margin-top:6px; color:var(--muted); font-size:14px; }}
    .badge {{
      display:inline-block; padding:8px 12px; border-radius:999px;
      background: rgba(106,166,255,.15);
      border:1px solid rgba(106,166,255,.28);
      color: #dbe8ff; font-size:12px;
    }}
    .grid {{ display:grid; grid-template-columns:1fr; gap:14px; }}
    @media (min-width: 960px) {{ .grid {{ grid-template-columns: 420px 1fr; }} }}
    .card {{
      background: var(--card);
      border:1px solid var(--line);
      border-radius:18px;
      padding:16px;
      backdrop-filter: blur(10px);
      box-shadow: 0 18px 40px rgba(0,0,0,.35);
    }}
    .card h2 {{ margin:0 0 12px; font-size:16px; color:#dfe8ff; }}
    label {{ display:block; margin-bottom:6px; color:var(--muted); font-size:12px; }}
    input {{
      width:100%; padding:10px 12px; border-radius:12px;
      border:1px solid rgba(255,255,255,.12);
      background: rgba(8,12,24,.55);
      color: var(--text);
      outline:none;
    }}
    input:focus {{
      border-color: rgba(106,166,255,.55);
      box-shadow: 0 0 0 4px rgba(106,166,255,.15);
    }}
    .row {{ display:grid; gap:10px; }}
    .two {{ grid-template-columns:1fr 1fr; }}
    @media (max-width: 520px) {{ .two {{ grid-template-columns: 1fr; }} }}
    .btns {{ display:flex; gap:10px; flex-wrap:wrap; margin-top:10px; }}
    .btn {{
      display:inline-flex; align-items:center; justify-content:center;
      padding:10px 12px; border-radius:12px; text-decoration:none;
      border:1px solid rgba(255,255,255,.14);
      background: rgba(255,255,255,.06);
      color: var(--text);
      font-weight:600; font-size:14px;
      cursor:pointer;
    }}
    .btn.primary {{ background: rgba(106,166,255,.18); border-color: rgba(106,166,255,.35); }}
    .btn.ok {{ background: rgba(34,197,94,.15); border-color: rgba(34,197,94,.35); }}
    .btn.danger {{ background: rgba(239,68,68,.12); border-color: rgba(239,68,68,.35); }}

    table {{
      width:100%;
      border-collapse: collapse;
      overflow:hidden;
      border-radius:16px;
      border:1px solid var(--line);
    }}
    thead th {{
      text-align:left; font-size:12px; color:var(--muted);
      padding:12px; background: rgba(255,255,255,.05);
    }}
    tbody td {{ padding:12px; border-top:1px solid var(--line); }}
    tbody tr:hover {{ background: rgba(255,255,255,.04); }}
    .actions {{ display:flex; gap:8px; flex-wrap:wrap; }}

    .alert {{
      margin: 0 0 14px;
      padding: 10px 12px;
      border-radius: 14px;
      border: 1px solid rgba(239,68,68,.45);
      background: rgba(239,68,68,.12);
      color: #ffd2d2;
      font-weight: 600;
    }}
    .muted {{ color: var(--muted); font-size: 13px; }}
    .footer {{ margin-top:14px; color:var(--muted); font-size:12px; text-align:center; }}

    /* -------------------------
       Graph styles (Degree Chart)
       ------------------------- */
    .chart {{
      display: grid;
      gap: 10px;
      margin: 10px 0 14px;
    }}
    .chart-row {{
      display: grid;
      grid-template-columns: 180px 1fr 48px;
      gap: 10px;
      align-items: center;
    }}
    @media (max-width: 700px) {{
      .chart-row {{ grid-template-columns: 1fr; }}
    }}
    .chart-label {{ color: var(--text); font-weight: 600; }}
    .bar-wrap {{
      height: 14px;
      border-radius: 999px;
      background: rgba(255,255,255,.08);
      border: 1px solid rgba(255,255,255,.10);
      overflow: hidden;
    }}
    .bar {{
      height: 100%;
      width: var(--w);
      border-radius: 999px;
      background: linear-gradient(90deg, rgba(106,166,255,.55), rgba(34,197,94,.45));
    }}
    .chart-count {{ color: var(--muted); font-weight: 700; text-align: right; }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="top">
      <div>
        <h1>Student Management System</h1>
        <div class="sub">Python + Flask • JSON storage • CRUD Web App</div>
      </div>
      <div class="badge">Local: 127.0.0.1:5000</div>
    </div>

    {alert}

    {content}

    <div class="footer">Portfolio Project</div>
  </div>
</body>
</html>
"""


# -------------------------
# Routes
# -------------------------
@app.get("/")
def home():
    students = load_students()

    q = request.args.get("q", "").strip().lower()
    if q:
        students = [
            s for s in students
            if q in str(s.get("id", "")).lower()
            or q in str(s.get("name", "")).lower()
            or q in str(s.get("degree", "")).lower()
        ]

    stats = compute_stats(students)
    msg = request.args.get("msg", "").strip()

    # Build degree chart (bars)
    max_count = max([c for _, c in stats["degrees"]], default=1)
    chart_rows = ""
    for deg, count in stats["degrees"]:
        width = int((count / max_count) * 100) if max_count else 0
        chart_rows += f"""
          <div class="chart-row">
            <div class="chart-label">{h(deg)}</div>
            <div class="bar-wrap"><div class="bar" style="--w:{width}%"></div></div>
            <div class="chart-count">{count}</div>
          </div>
        """
    degree_chart = f'<div class="chart">{chart_rows}</div>' if chart_rows else '<div class="muted">No degree data</div>'

    rows = ""
    for s in students:
        sid = h(s.get("id", ""))
        rows += f"""
        <tr>
          <td><span class="badge">{sid}</span></td>
          <td>{h(s.get("name",""))}</td>
          <td>{h(s.get("age",""))}</td>
          <td>{h(s.get("degree",""))}</td>
          <td>
            <div class="actions">
              <a class="btn primary" href="/edit/{sid}">Edit</a>
              <a class="btn danger" href="/delete/{sid}" onclick="return confirm('Delete this student?')">Delete</a>
            </div>
          </td>
        </tr>
        """

    if not rows:
        rows = "<tr><td colspan='5' class='muted'>No students found.</td></tr>"

    degree_rows = "".join(
        [f"<tr><td>{h(deg)}</td><td>{count}</td></tr>" for deg, count in stats["degrees"]]
    ) or "<tr><td colspan='2' class='muted'>No data</td></tr>"

    content = f"""
    <div class="grid">

      <div class="card">
        <h2>Add Student</h2>
        <form method="post" action="/add">
          <div class="row two">
            <div>
              <label>Student ID (unique)</label>
              <input name="id" placeholder="e.g. 001454242" required>
            </div>
            <div>
              <label>Name</label>
              <input name="name" placeholder="e.g. Qasim" required>
            </div>
          </div>

          <div class="row two" style="margin-top:10px;">
            <div>
              <label>Age</label>
              <input name="age" type="number" min="0" max="120" placeholder="e.g. 18">
            </div>
            <div>
              <label>Degree</label>
              <input name="degree" placeholder="e.g. Computing (AI)">
            </div>
          </div>

          <div class="btns">
            <button class="btn ok" type="submit">Add Student</button>
          </div>
          <p class="muted" style="margin:10px 0 0;">Tip: Student ID must be unique.</p>
        </form>
      </div>

      <div class="card">
        <h2>Students</h2>

        <form method="get" action="/" style="margin-bottom:12px;">
          <div class="row two">
            <div>
              <label>Search (Name / ID / Degree)</label>
              <input name="q" placeholder="Type to search..." value="{h(request.args.get('q',''))}">
            </div>
            <div style="display:flex; gap:10px; align-items:flex-end;">
              <button class="btn primary" type="submit">Search</button>
              <a class="btn" href="/">Clear</a>
            </div>
          </div>
        </form>

        <div class="btns" style="margin-bottom:10px;">
          <a class="btn ok" href="/export.csv">Export CSV</a>
        </div>

        <div class="row two" style="margin-bottom:12px;">
          <div class="badge">Total Students: {stats["total"]}</div>
          <div class="badge">Avg Age: {stats["avg_age"]} | Min: {stats["min_age"]} | Max: {stats["max_age"]}</div>
        </div>

        <div style="margin: 10px 0 12px;" class="muted"><b>Students by Degree</b></div>
        {degree_chart}

        <table style="margin-bottom:14px;">
          <thead>
            <tr>
              <th>Degree</th>
              <th style="width:110px;">Count</th>
            </tr>
          </thead>
          <tbody>
            {degree_rows}
          </tbody>
        </table>

        <table>
          <thead>
            <tr>
              <th style="width:170px;">ID</th>
              <th>Name</th>
              <th style="width:90px;">Age</th>
              <th>Degree</th>
              <th style="width:230px;">Actions</th>
            </tr>
          </thead>
          <tbody>
            {rows}
          </tbody>
        </table>
      </div>

    </div>
    """
    return layout("Student Management System", content, msg=msg)


@app.get("/export.csv")
def export_csv():
    students = load_students()
    lines = ["id,name,age,degree"]
    for s in students:
        sid = str(s.get("id", "")).replace(",", " ")
        name = str(s.get("name", "")).replace(",", " ")
        age = str(s.get("age", ""))
        degree = str(s.get("degree", "")).replace(",", " ")
        lines.append(f"{sid},{name},{age},{degree}")

    csv_data = "\n".join(lines)
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=students_export.csv"},
    )


@app.post("/add")
def add():
    students = load_students()

    sid = request.form.get("id", "").strip()
    name = request.form.get("name", "").strip()
    age_raw = request.form.get("age", "").strip()
    degree = request.form.get("degree", "").strip()

    if not sid or not name:
        return redirect("/?msg=ID+and+Name+are+required")

    if find_by_id(students, sid):
        return redirect("/?msg=Student+ID+already+exists.+Use+a+unique+ID")

    age = int(age_raw) if age_raw.isdigit() else 0
    students.append({"id": sid, "name": name, "age": age, "degree": degree})
    save_students(students)
    return redirect("/")


@app.get("/edit/<sid>")
def edit_form(sid):
    students = load_students()
    s = find_by_id(students, sid)
    if not s:
        return redirect("/?msg=Student+not+found")

    content = f"""
    <div class="card" style="max-width:720px; margin:0 auto;">
      <h2>Edit Student</h2>
      <p class="muted"><b>ID:</b> {h(sid)}</p>

      <form method="post" action="/edit/{h(sid)}">
        <div class="row two">
          <div>
            <label>Name</label>
            <input name="name" value="{h(s.get('name',''))}" required>
          </div>
          <div>
            <label>Age</label>
            <input name="age" type="number" min="0" max="120" value="{h(s.get('age',0))}">
          </div>
        </div>

        <div class="row" style="margin-top:10px;">
          <div>
            <label>Degree</label>
            <input name="degree" value="{h(s.get('degree',''))}">
          </div>
        </div>

        <div class="btns">
          <button class="btn ok" type="submit">Save Changes</button>
          <a class="btn" href="/">Cancel</a>
        </div>
      </form>
    </div>
    """
    return layout("Edit Student", content)


@app.post("/edit/<sid>")
def edit_save(sid):
    students = load_students()
    s = find_by_id(students, sid)
    if not s:
        return redirect("/?msg=Student+not+found")

    name = request.form.get("name", "").strip()
    age_raw = request.form.get("age", "").strip()
    degree = request.form.get("degree", "").strip()

    if not name:
        return redirect("/?msg=Name+cannot+be+empty")

    s["name"] = name
    s["age"] = int(age_raw) if age_raw.isdigit() else 0
    s["degree"] = degree

    save_students(students)
    return redirect("/")


@app.get("/delete/<sid>")
def delete(sid):
    students = load_students()
    students = [s for s in students if str(s.get("id", "")).strip() != sid.strip()]
    save_students(students)
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)

import dash
from dash import dcc, html, Input, Output, State, ALL
import requests
from dash.exceptions import PreventUpdate

API_BASE = "http://localhost:5000"  # ✅ use localhost (matches your working PowerShell)

app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server  # for deployment later


# -----------------------
# Helpers
# -----------------------
def auth_headers(token: str | None):
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


def fetch_me(token: str):
    r = requests.get(f"{API_BASE}/auth/me", headers=auth_headers(token), timeout=5)
    if r.status_code != 200:
        return None
    return r.json()


def safe_json(resp):
    try:
        return resp.json()
    except Exception:
        return {}


# -----------------------
# Pages (Layouts)
# -----------------------
def register_page():
    return html.Div(
        style={"maxWidth": "420px", "margin": "40px auto", "fontFamily": "Arial"},
        children=[
            html.H2("Register"),
            html.Label("Name"),
            dcc.Input(id="reg-name", type="text", style={"width": "100%"}, debounce=True),
            html.Br(), html.Br(),

            html.Label("Email"),
            dcc.Input(id="reg-email", type="email", style={"width": "100%"}, debounce=True),
            html.Br(), html.Br(),

            html.Label("Password"),
            dcc.Input(id="reg-password", type="password", style={"width": "100%"}),
            html.Br(), html.Br(),

            html.Button("Create account", id="reg-submit", n_clicks=0),
            html.Div(id="reg-msg", style={"marginTop": "12px"}),

            html.Hr(),
            dcc.Link("Already have an account? Login", href="/login"),
        ],
    )


def login_page():
    return html.Div(
        style={"maxWidth": "420px", "margin": "40px auto", "fontFamily": "Arial"},
        children=[
            html.H2("Login"),
            html.Label("Email"),
            dcc.Input(id="login-email", type="email", style={"width": "100%"}, debounce=True),
            html.Br(), html.Br(),

            html.Label("Password"),
            dcc.Input(id="login-password", type="password", style={"width": "100%"}),
            html.Br(), html.Br(),

            html.Button("Login", id="login-submit", n_clicks=0),
            html.Div(id="login-msg", style={"marginTop": "12px"}),

            html.Hr(),
            dcc.Link("New here? Register", href="/register"),
        ],
    )


def top_nav(user):
    links = [
        dcc.Link("Dashboard", href="/dashboard"),
        dcc.Link("Courses", href="/courses"),
        dcc.Link("My Courses", href="/my-courses"),
    ]

    if user.get("role") in ("instructor", "admin"):
        links.append(dcc.Link("Instructor", href="/instructor"))

    return html.Div(
        style={"display": "flex", "gap": "16px", "alignItems": "center"},
        children=[
            *links,
            html.Div(style={"marginLeft": "auto"}, children=[
                html.Span(f"{user.get('name')} ({user.get('role')})", style={"opacity": 0.8}),
                html.Span("  "),
                html.Button("Logout", id="logout-btn", n_clicks=0),
            ])
        ],
    )



def dashboard_page(user):
    return html.Div(
        style={"maxWidth": "900px", "margin": "30px auto", "fontFamily": "Arial"},
        children=[
            top_nav(user),
            html.Hr(),
            html.H2("Dashboard"),
            html.Div(f"Logged in as: {user.get('name')} ({user.get('email')}) — role: {user.get('role')}"),
            html.Br(),
            html.Div([
                html.Div("✅ Auth + JWT working"),
                html.Div("✅ Courses/Lessons/Enrollments/Progress backend ready"),
                html.Div("➡️ Now frontend pages are wired to APIs"),
            ]),
        ],
    )


def courses_page(user):
    return html.Div(
        style={"maxWidth": "900px", "margin": "30px auto", "fontFamily": "Arial"},
        children=[
            top_nav(user),
            html.Hr(),
            html.H2("Course Catalog"),
            html.Div(id="courses-msg", style={"marginBottom": "10px"}),
            html.Div(id="courses-list"),
        ],
    )


def course_detail_page(user, course_id: int):
    return html.Div(
        style={"maxWidth": "900px", "margin": "30px auto", "fontFamily": "Arial"},
        children=[
            top_nav(user),
            html.Hr(),
            dcc.Link("← Back to Courses", href="/courses"),
            html.H2(f"Course #{course_id}"),
            html.Div(id="course-detail"),
            html.Br(),
            html.Div(id="course-actions"),
            html.Hr(),
            html.H3("Lessons"),
            html.Div(id="course-lessons"),
            html.Div(id="course-detail-msg", style={"marginTop": "10px"}),
        ],
    )


def lesson_page(user, lesson_id: int):
    return html.Div(
        style={"maxWidth": "900px", "margin": "30px auto", "fontFamily": "Arial"},
        children=[
            top_nav(user),
            html.Hr(),
            dcc.Link("← Back", href="/courses"),
            html.H2(f"Lesson #{lesson_id}"),
            html.Div(id="lesson-detail"),
            html.Br(),
            html.Button("Mark Complete", id="mark-complete-btn", n_clicks=0),
            html.Div(id="lesson-msg", style={"marginTop": "10px"}),
            dcc.Store(id="current-lesson-id", data=lesson_id),
        ],
    )


def my_courses_page(user):
    return html.Div(
        style={"maxWidth": "900px", "margin": "30px auto", "fontFamily": "Arial"},
        children=[
            top_nav(user),
            html.Hr(),
            html.H2("My Courses"),
            html.Div(id="my-courses-msg", style={"marginBottom": "10px"}),
            html.Div(id="my-courses-list"),
        ],
    )


# -----------------------
# App Layout
# -----------------------
app.layout = html.Div([
    dcc.Location(id="url"),
    dcc.Store(id="auth-store", storage_type="session"),
    html.Div(id="page-content")
])


# -----------------------
# Router
# -----------------------
@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname"),
    Input("auth-store", "data"),
)
def route(pathname, auth_data):
    auth_data = auth_data or {}
    token = auth_data.get("access_token")

    # Public routes
    if pathname == "/register":
        return register_page()
    if pathname == "/login":
        # If already logged in, go dashboard
        if token:
            return dcc.Location(pathname="/dashboard", id="redir-login")
        return login_page()

    # Everything else requires auth
    if not token:
        return login_page()

    # ✅ Always fetch user BEFORE any role checks
    try:
        user = fetch_me(token)
        if not user:
            return login_page()
    except Exception:
        return html.Div("Backend not reachable. Is Flask running on :5000?", style={"padding": "20px"})
    if pathname and pathname.startswith("/instructor/course/"):
        if user.get("role") not in ("instructor", "admin"):
            return html.Div("403 - Instructor access only", style={"padding": "20px", "color": "crimson"})
        try:
            course_id = int(pathname.split("/instructor/course/")[1])
        except Exception:
            return html.Div("Invalid instructor course URL", style={"padding": "20px", "color": "crimson"})

        return instructor_course_page(user, course_id)
    # Routes
    if pathname in ["/", "/dashboard"]:
        return dashboard_page(user)

    if pathname == "/courses":
        return courses_page(user)

    if pathname == "/my-courses":
        return my_courses_page(user)

    if pathname == "/instructor":
        if user.get("role") not in ("instructor", "admin"):
            return html.Div("403 - Instructor access only", style={"padding": "20px", "color": "crimson"})
        return instructor_page(user)

    if pathname and pathname.startswith("/course/"):
        try:
            course_id = int(pathname.split("/course/")[1])
            return course_detail_page(user, course_id)
        except Exception:
            return html.Div("Invalid course URL", style={"padding": "20px", "color": "crimson"})

    if pathname and pathname.startswith("/lesson/"):
        try:
            lesson_id = int(pathname.split("/lesson/")[1])
            return lesson_page(user, lesson_id)
        except Exception:
            return html.Div("Invalid lesson URL", style={"padding": "20px", "color": "crimson"})

    return html.Div("404 - Page not found", style={"padding": "20px"})

@app.callback(
    Output("il-course-dd", "options"),
    Input("url", "pathname"),
    State("auth-store", "data"),
)
def load_instructor_courses(pathname, auth_data):
    if pathname != "/instructor":
        raise PreventUpdate

    token = (auth_data or {}).get("access_token")
    if not token:
        raise PreventUpdate

    # Fetch all courses and filter by instructor_id (simple approach)
    me = fetch_me(token)
    if not me:
        return []

    r = requests.get(f"{API_BASE}/courses", timeout=5)
    if r.status_code != 200:
        return []

    courses = r.json()
    my_courses = [c for c in courses if c.get("instructor_id") == me.get("id")]
    return [{"label": f"{c['title']} (id={c['id']})", "value": c["id"]} for c in my_courses]

@app.callback(
    Output("ic-msg", "children"),
    Input("ic-submit", "n_clicks"),
    State("ic-title", "value"),
    State("ic-desc", "value"),
    State("ic-level", "value"),
    State("auth-store", "data"),
    prevent_initial_call=True,
)
def instructor_create_course(n, title, desc, level, auth_data):
    if not n or n < 1:
        raise PreventUpdate

    token = (auth_data or {}).get("access_token")
    if not token:
        return html.Div("Please login first.", style={"color": "crimson"})

    if not title:
        return html.Div("Title is required.", style={"color": "crimson"})

    r = requests.post(
        f"{API_BASE}/courses",
        json={"title": title, "description": desc, "level": level},
        headers=auth_headers(token),
        timeout=5,
    )

    if r.status_code == 201:
        return html.Div("Course created ✅", style={"color": "green"})

    msg = safe_json(r).get("error", r.text)
    return html.Div(f"Create failed: {msg}", style={"color": "crimson"})

@app.callback(
    Output("il-msg", "children"),
    Input("il-submit", "n_clicks"),
    State("il-course-dd", "value"),
    State("il-title", "value"),
    State("il-content", "value"),
    State("il-order", "value"),
    State("auth-store", "data"),
    prevent_initial_call=True,
)
def instructor_add_lesson(n, course_id, title, content, order_index, auth_data):
    if not n or n < 1:
        raise PreventUpdate

    token = (auth_data or {}).get("access_token")
    if not token:
        return html.Div("Please login first.", style={"color": "crimson"})

    if not course_id:
        return html.Div("Select a course first.", style={"color": "crimson"})
    if not title:
        return html.Div("Lesson title is required.", style={"color": "crimson"})

    payload = {
        "title": title,
        "content": content,
        "order_index": int(order_index or 1),
    }

    r = requests.post(
        f"{API_BASE}/courses/{course_id}/lessons",
        json=payload,
        headers=auth_headers(token),
        timeout=5,
    )

    if r.status_code == 201:
        return html.Div("Lesson added ✅", style={"color": "green"})

    msg = safe_json(r).get("error", r.text)
    return html.Div(f"Add lesson failed: {msg}", style={"color": "crimson"})

# -----------------------
# Register
# -----------------------
@app.callback(
    Output("reg-msg", "children"),
    Input("reg-submit", "n_clicks"),
    State("reg-name", "value"),
    State("reg-email", "value"),
    State("reg-password", "value"),
    prevent_initial_call=True,
)
def do_register(n, name, email, password):
    if not name or not email or not password:
        return html.Div("Please fill all fields.", style={"color": "crimson"})

    try:
        r = requests.post(
            f"{API_BASE}/auth/register",
            json={"name": name, "email": email, "password": password},
            timeout=5,
        )
        if r.status_code == 201:
            return html.Div("Registered! Now login.", style={"color": "green"})
        msg = safe_json(r).get("error", "Registration failed")
        return html.Div(msg, style={"color": "crimson"})
    except Exception:
        return html.Div("Backend not reachable. Is Flask running on :5000?", style={"color": "crimson"})


# -----------------------
# Login
# -----------------------
@app.callback(
    Output("auth-store", "data"),
    Output("login-msg", "children"),
    Output("url", "pathname", allow_duplicate=True),
    Input("login-submit", "n_clicks"),
    State("login-email", "value"),
    State("login-password", "value"),
    prevent_initial_call=True,
)
def do_login(n, email, password):
    if not email or not password:
        return dash.no_update, html.Div("Enter email + password.", style={"color": "crimson"}), dash.no_update

    try:
        r = requests.post(
            f"{API_BASE}/auth/login",
            json={"email": email, "password": password},
            timeout=5,
        )
        if r.status_code == 200:
            data = r.json()
            token = data.get("access_token")
            return {"access_token": token}, html.Div("Login successful!", style={"color": "green"}), "/dashboard"

        msg = safe_json(r).get("error", "Login failed")
        return dash.no_update, html.Div(msg, style={"color": "crimson"}), dash.no_update
    except Exception:
        return dash.no_update, html.Div("Backend not reachable. Is Flask running on :5000?", style={"color": "crimson"}), dash.no_update


# -----------------------
# Logout
# -----------------------
@app.callback(
    Output("auth-store", "clear_data"),
    Output("url", "pathname", allow_duplicate=True),
    Input("logout-btn", "n_clicks"),
    prevent_initial_call=True,
)
def logout(n):
    if not n or n < 1:
        raise PreventUpdate
    return True, "/login"


# -----------------------
# Courses: load catalog
# -----------------------
@app.callback(
    Output("courses-list", "children"),
    Output("courses-msg", "children"),
    Input("url", "pathname"),
    State("auth-store", "data"),
)
def load_courses(pathname, auth_data):
    if pathname != "/courses":
        raise PreventUpdate

    auth_data = auth_data or {}
    token = auth_data.get("access_token")

    try:
        r = requests.get(f"{API_BASE}/courses", timeout=5)
        if r.status_code != 200:
            return [], html.Div("Failed to load courses.", style={"color": "crimson"})

        courses = r.json()
        if not courses:
            return [html.Div("No courses yet.")], ""

        cards = []
        for c in courses:
            cards.append(html.Div(
                style={"border": "1px solid #ddd", "borderRadius": "8px", "padding": "12px", "marginBottom": "10px"},
                children=[
                    html.H4(c["title"], style={"margin": "0 0 6px 0"}),
                    html.Div(c.get("description", "")),
                    html.Small(f"Level: {c.get('level','')} | Instructor ID: {c.get('instructor_id')}"),
                    html.Br(), html.Br(),
                    html.Div(style={"display": "flex", "gap": "10px"}, children=[
                        dcc.Link("View", href=f"/course/{c['id']}"),
                        html.Button("Enroll", id={"type": "enroll-btn", "course_id": c["id"]}, n_clicks=0),
                    ]),
                ]
            ))
        return cards, ""
    except Exception:
        return [], html.Div("Backend not reachable. Is Flask running on :5000?", style={"color": "crimson"})


# -----------------------
# Courses: enroll button
# -----------------------
@app.callback(
    Output("courses-msg", "children", allow_duplicate=True),
    Input({"type": "enroll-btn", "course_id": ALL}, "n_clicks"),
    State("auth-store", "data"),
    prevent_initial_call=True,
)
def enroll_course(n_clicks_list, auth_data):
    if not n_clicks_list or max(n_clicks_list) < 1:
        raise PreventUpdate

    auth_data = auth_data or {}
    token = auth_data.get("access_token")
    if not token:
        return html.Div("Please login first.", style={"color": "crimson"})

    # Find which button was clicked
    ctx = dash.callback_context
    trigger = ctx.triggered[0]["prop_id"].split(".")[0]
    course_id = eval(trigger).get("course_id")

    try:
        r = requests.post(f"{API_BASE}/courses/{course_id}/enroll", headers=auth_headers(token), timeout=5)
        if r.status_code in (200, 201):
            return html.Div(f"Enrolled in course {course_id} ✅", style={"color": "green"})
        msg = safe_json(r).get("error", r.text)
        return html.Div(f"Enroll failed: {msg}", style={"color": "crimson"})
    except Exception:
        return html.Div("Backend not reachable. Is Flask running on :5000?", style={"color": "crimson"})


# -----------------------
# Course Detail: load course + lessons
# -----------------------
@app.callback(
    Output("course-detail", "children"),
    Output("course-actions", "children"),
    Output("course-lessons", "children"),
    Input("url", "pathname"),
    State("auth-store", "data"),
)
def load_course_detail(pathname, auth_data):
    if not pathname or not pathname.startswith("/course/"):
        raise PreventUpdate

    auth_data = auth_data or {}
    token = auth_data.get("access_token")
    if not token:
        raise PreventUpdate

    try:
        course_id = int(pathname.split("/course/")[1])
    except Exception:
        return html.Div("Invalid course id.", style={"color": "crimson"}), "", ""

    try:
        # Course info
        rc = requests.get(f"{API_BASE}/courses/{course_id}", timeout=5)
        if rc.status_code != 200:
            return html.Div("Course not found.", style={"color": "crimson"}), "", ""

        c = rc.json()
        course_info = html.Div([
            html.H3(c["title"], style={"marginTop": "0"}),
            html.Div(c.get("description", "")),
            html.Small(f"Level: {c.get('level','')} | Instructor ID: {c.get('instructor_id')}"),
        ])

        # Actions
        actions = html.Div([
            html.Button("Enroll in this course", id="enroll-course-detail-btn", n_clicks=0),
            dcc.Store(id="current-course-id", data=course_id),
        ])

        # Lessons
        rl = requests.get(f"{API_BASE}/courses/{course_id}/lessons", timeout=5)
        lessons = rl.json() if rl.status_code == 200 else []
        if not lessons:
            lessons_view = html.Div("No lessons yet.")
        else:
            lessons_view = html.Ul([
                html.Li([
                    dcc.Link(f"{l['order_index']}. {l['title']}", href=f"/lesson/{l['id']}")
                ])
                for l in lessons
            ])

        return course_info, actions, lessons_view

    except Exception:
        return html.Div("Backend not reachable. Is Flask running on :5000?", style={"color": "crimson"}), "", ""


# Enroll button on course detail page
@app.callback(
    Output("course-detail-msg", "children"),
    Input("enroll-course-detail-btn", "n_clicks"),
    State("current-course-id", "data"),
    State("auth-store", "data"),
    prevent_initial_call=True,
)
def enroll_from_course_detail(n, course_id, auth_data):
    if not n or n < 1:
        raise PreventUpdate

    auth_data = auth_data or {}
    token = auth_data.get("access_token")
    if not token:
        return html.Div("Please login first.", style={"color": "crimson"})

    try:
        r = requests.post(f"{API_BASE}/courses/{course_id}/enroll", headers=auth_headers(token), timeout=5)
        if r.status_code in (200, 201):
            return html.Div("Enrolled successfully ✅", style={"color": "green"})
        msg = safe_json(r).get("error", r.text)
        return html.Div(f"Enroll failed: {msg}", style={"color": "crimson"})
    except Exception:
        return html.Div("Backend not reachable. Is Flask running on :5000?", style={"color": "crimson"})


# -----------------------
# Lesson: load lesson content
# -----------------------
@app.callback(
    Output("lesson-detail", "children"),
    Input("url", "pathname"),
)
def load_lesson(pathname):
    if not pathname or not pathname.startswith("/lesson/"):
        raise PreventUpdate

    try:
        lesson_id = int(pathname.split("/lesson/")[1])
    except Exception:
        return html.Div("Invalid lesson id.", style={"color": "crimson"})

    try:
        r = requests.get(f"{API_BASE}/lessons/{lesson_id}", timeout=5)
        if r.status_code != 200:
            return html.Div("Lesson not found.", style={"color": "crimson"})
        l = r.json()
        return html.Div([
            html.H3(l["title"], style={"marginTop": "0"}),
            html.Div(l.get("content", "") or "", style={"whiteSpace": "pre-wrap"}),
            html.Br(),
            html.Small(f"Course ID: {l.get('course_id')} | Order: {l.get('order_index')}"),
        ])
    except Exception:
        return html.Div("Backend not reachable. Is Flask running on :5000?", style={"color": "crimson"})


# Lesson: mark complete
@app.callback(
    Output("lesson-msg", "children"),
    Input("mark-complete-btn", "n_clicks"),
    State("current-lesson-id", "data"),
    State("auth-store", "data"),
    prevent_initial_call=True,
)
def mark_complete(n, lesson_id, auth_data):
    if not n or n < 1:
        raise PreventUpdate

    auth_data = auth_data or {}
    token = auth_data.get("access_token")
    if not token:
        return html.Div("Please login first.", style={"color": "crimson"})

    try:
        r = requests.post(
            f"{API_BASE}/lessons/{lesson_id}/complete",
            headers=auth_headers(token),
            timeout=5
        )
        if r.status_code == 200:
            return html.Div("Marked complete ✅", style={"color": "green"})
        msg = safe_json(r).get("error", r.text)
        return html.Div(f"Failed: {msg}", style={"color": "crimson"})
    except Exception:
        return html.Div("Backend not reachable. Is Flask running on :5000?", style={"color": "crimson"})


# -----------------------
# My Courses: list enrollments + progress
# -----------------------
@app.callback(
    Output("my-courses-list", "children"),
    Output("my-courses-msg", "children"),
    Input("url", "pathname"),
    State("auth-store", "data"),
)
def load_my_courses(pathname, auth_data):
    if pathname != "/my-courses":
        raise PreventUpdate

    token = (auth_data or {}).get("access_token")
    if not token:
        return [], html.Div("Please login first.", style={"color": "crimson"})

    me = fetch_me(token)
    if not me:
        return [], html.Div("Session expired. Please login again.", style={"color": "crimson"})

    # ✅ Instructor/Admin view: courses I teach
    if me.get("role") in ("instructor", "admin"):
        r = requests.get(f"{API_BASE}/courses", timeout=5)
        if r.status_code != 200:
            return [], html.Div("Failed to load courses.", style={"color": "crimson"})

        courses = r.json()
        my_courses = [c for c in courses if c.get("instructor_id") == me.get("id")]

        if not my_courses:
            return [html.Div("You haven’t created any courses yet. Go to Instructor tab.")], ""

        cards = []
        for c in my_courses:
            cards.append(html.Div(
                style={"border": "1px solid #ddd", "borderRadius": "8px", "padding": "12px", "marginBottom": "10px"},
                children=[
                    html.H4(c["title"], style={"margin": "0 0 6px 0"}),
                    html.Div(c.get("description", "")),
                    html.Small(f"Level: {c.get('level','')}"),
                    html.Br(), html.Br(),
                    html.Div(style={"display": "flex", "gap": "10px"}, children=[
                        dcc.Link("View", href=f"/course/{c['id']}"),
                        dcc.Link("Manage Lessons", href=f"/instructor/course/{c['id']}"), 
                    ]),
                ]
            ))
        return cards, html.Div("Showing courses you teach.", style={"color": "#444"})

    # ✅ Student view: enrolled courses + progress (your existing behavior)
    try:
        r = requests.get(f"{API_BASE}/me/enrollments", headers=auth_headers(token), timeout=5)
        if r.status_code != 200:
            msg = safe_json(r).get("error", r.text)
            return [], html.Div(f"Failed to load enrollments: {msg}", style={"color": "crimson"})

        enrollments = r.json()
        if not enrollments:
            return [html.Div("You are not enrolled in any courses yet.")], ""

        rows = []
        for e in enrollments:
            c = e["course"]
            course_id = c["id"]

            progress_percent = None
            pr = requests.get(f"{API_BASE}/courses/{course_id}/progress", headers=auth_headers(token), timeout=5)
            if pr.status_code == 200:
                progress_percent = pr.json().get("completion_percent")

            rows.append(html.Div(
                style={"border": "1px solid #ddd", "borderRadius": "8px", "padding": "12px", "marginBottom": "10px"},
                children=[
                    html.H4(c["title"], style={"margin": "0 0 6px 0"}),
                    html.Div(c.get("description", "")),
                    html.Small(f"Level: {c.get('level','')}"),
                    html.Br(),
                    html.Div(f"Progress: {progress_percent if progress_percent is not None else '—'}%"),
                    html.Br(),
                    dcc.Link("Open course", href=f"/course/{course_id}"),
                ]
            ))

        return rows, ""
    except Exception:
        return [], html.Div("Backend not reachable. Is Flask running on :5000?", style={"color": "crimson"})

def instructor_page(user):
    return html.Div(
        style={"maxWidth": "900px", "margin": "30px auto", "fontFamily": "Arial"},
        children=[
            top_nav(user),
            html.Hr(),
            html.H2("Instructor Panel"),

            html.H3("Create a Course"),
            html.Label("Title"),
            dcc.Input(id="ic-title", type="text", style={"width": "100%"}, debounce=True),
            html.Br(), html.Br(),
            html.Label("Description"),
            dcc.Textarea(id="ic-desc", style={"width": "100%", "height": "80px"}),
            html.Br(), html.Br(),
            html.Label("Level"),
            dcc.Input(id="ic-level", type="text", placeholder="Beginner / Intermediate", style={"width": "100%"}, debounce=True),
            html.Br(), html.Br(),
            html.Button("Create Course", id="ic-submit", n_clicks=0),
            html.Div(id="ic-msg", style={"marginTop": "10px"}),

            html.Hr(),

            html.H3("Add Lesson to a Course"),
            html.Div("Select course:"),
            dcc.Dropdown(id="il-course-dd", placeholder="Choose a course"),
            html.Br(),
            html.Label("Lesson Title"),
            dcc.Input(id="il-title", type="text", style={"width": "100%"}, debounce=True),
            html.Br(), html.Br(),
            html.Label("Lesson Content"),
            dcc.Textarea(id="il-content", style={"width": "100%", "height": "120px"}),
            html.Br(), html.Br(),
            html.Label("Order Index"),
            dcc.Input(id="il-order", type="number", value=1, style={"width": "120px"}),
            html.Br(), html.Br(),
            html.Button("Add Lesson", id="il-submit", n_clicks=0),
            html.Div(id="il-msg", style={"marginTop": "10px"}),
        ],
    )

def instructor_course_page(user, course_id: int):
    return html.Div(
        style={"maxWidth": "900px", "margin": "30px auto", "fontFamily": "Arial"},
        children=[
            top_nav(user),
            html.Hr(),
            dcc.Link("← Back to My Courses", href="/my-courses"),
            html.H2(f"Manage Course #{course_id}"),
            dcc.Store(id="manage-course-id", data=course_id),

            html.Div(id="ic-course-info"),
            html.Hr(),

            html.H3("Lessons"),
            html.Div(id="ic-lessons-list"),
            html.Div(id="ic-lessons-msg", style={"marginTop": "10px"}),

            html.Hr(),
            html.H3("Add a Lesson"),
            html.Label("Lesson Title"),
            dcc.Input(id="ic-lesson-title", type="text", style={"width": "100%"}, debounce=True),
            html.Br(), html.Br(),

            html.Label("Lesson Content"),
            dcc.Textarea(id="ic-lesson-content", style={"width": "100%", "height": "140px"}),
            html.Br(), html.Br(),

            html.Label("Order Index"),
            dcc.Input(id="ic-lesson-order", type="number", value=1, style={"width": "120px"}),
            html.Br(), html.Br(),

            html.Button("Add Lesson", id="ic-add-lesson-btn", n_clicks=0),
            html.Div(id="ic-add-lesson-msg", style={"marginTop": "10px"}),
        ],
    )

@app.callback(
    Output("ic-course-info", "children"),
    Output("ic-lessons-list", "children"),
    Input("url", "pathname"),
    State("auth-store", "data"),
)
def load_instructor_course_data(pathname, auth_data):
    if not pathname or not pathname.startswith("/instructor/course/"):
        raise PreventUpdate

    token = (auth_data or {}).get("access_token")
    if not token:
        raise PreventUpdate

    try:
        course_id = int(pathname.split("/instructor/course/")[1])
    except Exception:
        return html.Div("Invalid course id.", style={"color": "crimson"}), ""

    me = fetch_me(token)
    if not me:
        return html.Div("Session expired. Please login again.", style={"color": "crimson"}), ""

    # Fetch course
    rc = requests.get(f"{API_BASE}/courses/{course_id}", timeout=5)
    if rc.status_code != 200:
        return html.Div("Course not found.", style={"color": "crimson"}), ""

    course = rc.json()

    # Frontend ownership check (backend will enforce too)
    if me.get("role") != "admin" and course.get("instructor_id") != me.get("id"):
        return html.Div("403 - You don’t own this course.", style={"color": "crimson"}), ""

    course_info = html.Div([
        html.H3(course.get("title", ""), style={"marginTop": "0"}),
        html.Div(course.get("description", "")),
        html.Small(f"Level: {course.get('level','')} | Instructor ID: {course.get('instructor_id')}"),
    ])

    # Fetch lessons
    rl = requests.get(f"{API_BASE}/courses/{course_id}/lessons", timeout=5)
    lessons = rl.json() if rl.status_code == 200 else []

    if not lessons:
        lessons_view = html.Div("No lessons yet.")
    else:
        lessons_view = html.Ul([
            html.Li([
                html.Span(f"{l['order_index']}. {l['title']} "),
                html.Small(" "),
                dcc.Link("View", href=f"/lesson/{l['id']}"),
                # Edit/Delete will come later once backend supports it
            ])
            for l in lessons
        ])

    return course_info, lessons_view

@app.callback(
    Output("ic-add-lesson-msg", "children"),
    Input("ic-add-lesson-btn", "n_clicks"),
    State("manage-course-id", "data"),
    State("ic-lesson-title", "value"),
    State("ic-lesson-content", "value"),
    State("ic-lesson-order", "value"),
    State("auth-store", "data"),
    prevent_initial_call=True,
)
def add_lesson_from_manage_page(n, course_id, title, content, order_index, auth_data):
    if not n or n < 1:
        raise PreventUpdate

    token = (auth_data or {}).get("access_token")
    if not token:
        return html.Div("Please login first.", style={"color": "crimson"})

    if not course_id:
        return html.Div("Missing course id.", style={"color": "crimson"})
    if not title:
        return html.Div("Lesson title is required.", style={"color": "crimson"})

    payload = {
        "title": title,
        "content": content,
        "order_index": int(order_index or 1),
    }

    r = requests.post(
        f"{API_BASE}/courses/{course_id}/lessons",
        json=payload,
        headers=auth_headers(token),
        timeout=5,
    )

    if r.status_code == 201:
        return html.Div("Lesson added ✅ (refresh page to see it)", style={"color": "green"})

    msg = safe_json(r).get("error", r.text)
    return html.Div(f"Add lesson failed: {msg}", style={"color": "crimson"})

if __name__ == "__main__":
    app.run(debug=True, port=8050)



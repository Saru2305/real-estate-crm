
from flask import Flask, render_template, request, redirect, session, flash
from database import init_db, get_db

app = Flask(__name__)

# Secret key for login session
app.secret_key = "real-estate-crm-secret-key"

# Create database and tables
init_db()


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    if "user_id" in session:
        return redirect("/dashboard")

    return redirect("/login")


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        conn = get_db()

        user = conn.execute("""
            SELECT *
            FROM users
            WHERE email = ?
            AND password = ?
        """, (email, password)).fetchone()

        conn.close()

        if user:

            session["user_id"] = user["id"]
            session["name"] = user["name"]
            session["role"] = user["role"]

            return redirect("/dashboard")

        return render_template(
            "login.html",
            error="Invalid email or password"
        )

    return render_template("login.html")


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()

    # Total leads
    total_leads = conn.execute("""
        SELECT COUNT(*)
        FROM leads
    """).fetchone()[0]

    # Follow-ups
    follow_ups = conn.execute("""
        SELECT COUNT(*)
        FROM leads
        WHERE follow_up_date IS NOT NULL
        AND follow_up_date != ''
    """).fetchone()[0]

    # Confirmed bookings
    total_bookings = conn.execute("""
        SELECT COUNT(*)
        FROM bookings
        WHERE status = 'Confirmed'
    """).fetchone()[0]

    # Sales value
    sales_value = conn.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM bookings
        WHERE status = 'Confirmed'
    """).fetchone()[0]

    # Recent leads
    recent_leads = conn.execute("""
        SELECT
            leads.*,
            users.name AS employee_name
        FROM leads
        LEFT JOIN users
        ON leads.assigned_to = users.id
        ORDER BY leads.id DESC
        LIMIT 5
    """).fetchall()

    # Upcoming follow-ups
    upcoming_followups = conn.execute("""
        SELECT *
        FROM leads
        WHERE follow_up_date IS NOT NULL
        AND follow_up_date != ''
        ORDER BY follow_up_date ASC
        LIMIT 5
    """).fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        name=session["name"],
        role=session["role"],
        total_leads=total_leads,
        follow_ups=follow_ups,
        total_bookings=total_bookings,
        sales_value=sales_value,
        recent_leads=recent_leads,
        upcoming_followups=upcoming_followups
    )


# =========================================================
# LEADS
# =========================================================

@app.route("/leads")
def leads():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()

    # Admin can see all leads
    if session["role"] == "Admin":

        leads = conn.execute("""
            SELECT
                leads.*,
                users.name AS employee_name
            FROM leads
            LEFT JOIN users
            ON leads.assigned_to = users.id
            ORDER BY leads.id DESC
        """).fetchall()

    # Sales Employee sees only assigned leads
    else:

        leads = conn.execute("""
            SELECT
                leads.*,
                users.name AS employee_name
            FROM leads
            LEFT JOIN users
            ON leads.assigned_to = users.id
            WHERE leads.assigned_to = ?
            ORDER BY leads.id DESC
        """, (session["user_id"],)).fetchall()

    # Employees for assignment
    employees = conn.execute("""
        SELECT *
        FROM users
        WHERE role = 'Sales Employee'
    """).fetchall()

    conn.close()

    return render_template(
        "leads.html",
        leads=leads,
        employees=employees,
        name=session["name"],
        role=session["role"]
    )


# =========================================================
# ADD LEAD
# =========================================================

@app.route("/add-lead", methods=["POST"])
def add_lead():

    if "user_id" not in session:
        return redirect("/login")

    name = request.form.get("name")
    phone = request.form.get("phone")
    email = request.form.get("email")
    source = request.form.get("source")
    assigned_to = request.form.get("assigned_to")
    notes = request.form.get("notes")
    follow_up_date = request.form.get("follow_up_date")

    if not name or not phone:

        flash(
            "Name and phone are required.",
            "error"
        )

        return redirect("/leads")

    # Sales employee can only create lead for themselves
    if session["role"] == "Sales Employee":

        assigned_to = session["user_id"]

    conn = get_db()

    conn.execute("""
        INSERT INTO leads
        (
            name,
            phone,
            email,
            source,
            stage,
            assigned_to,
            notes,
            follow_up_date
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        name,
        phone,
        email,
        source,
        "New",
        assigned_to if assigned_to else None,
        notes,
        follow_up_date
    ))

    conn.commit()
    conn.close()

    flash(
        "Lead added successfully!",
        "success"
    )

    return redirect("/leads")


# =========================================================
# EDIT LEAD
# =========================================================

@app.route("/edit-lead/<int:lead_id>", methods=["POST"])
def edit_lead(lead_id):

    if "user_id" not in session:
        return redirect("/login")

    name = request.form.get("name")
    phone = request.form.get("phone")
    email = request.form.get("email")
    source = request.form.get("source")
    stage = request.form.get("stage")
    assigned_to = request.form.get("assigned_to")
    notes = request.form.get("notes")
    follow_up_date = request.form.get("follow_up_date")

    if not name or not phone or not stage:

        flash(
            "Name, phone and stage are required.",
            "error"
        )

        return redirect("/leads")

    conn = get_db()

    # Check whether lead exists
    lead = conn.execute("""
        SELECT *
        FROM leads
        WHERE id = ?
    """, (lead_id,)).fetchone()

    if not lead:

        conn.close()

        flash(
            "Lead not found.",
            "error"
        )

        return redirect("/leads")

    # Sales employee can edit only their assigned lead
    if (
        session["role"] == "Sales Employee"
        and lead["assigned_to"] != session["user_id"]
    ):

        conn.close()

        flash(
            "You are not allowed to edit this lead.",
            "error"
        )

        return redirect("/leads")

    # Sales employee cannot reassign leads
    if session["role"] == "Sales Employee":

        assigned_to = lead["assigned_to"]

    conn.execute("""
        UPDATE leads
        SET
            name = ?,
            phone = ?,
            email = ?,
            source = ?,
            stage = ?,
            assigned_to = ?,
            notes = ?,
            follow_up_date = ?
        WHERE id = ?
    """, (
        name,
        phone,
        email,
        source,
        stage,
        assigned_to if assigned_to else None,
        notes,
        follow_up_date,
        lead_id
    ))

    conn.commit()
    conn.close()

    flash(
        "Lead updated successfully!",
        "success"
    )

    return redirect("/leads")


# =========================================================
# PROPERTIES
# =========================================================

@app.route("/properties")
def properties():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()

    properties = conn.execute("""
        SELECT *
        FROM properties
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "properties.html",
        properties=properties,
        name=session["name"],
        role=session["role"]
    )


# =========================================================
# ADD PROPERTY
# =========================================================

@app.route("/add-property", methods=["POST"])
def add_property():

    if "user_id" not in session:
        return redirect("/login")

    # Only Admin can add properties
    if session["role"] != "Admin":

        flash(
            "Only Admin can add properties.",
            "error"
        )

        return redirect("/properties")

    project_name = request.form.get("project_name")
    building_name = request.form.get("building_name")
    unit_number = request.form.get("unit_number")
    property_type = request.form.get("property_type")
    price = request.form.get("price")
    status = request.form.get("status", "Available")

    if (
        not project_name
        or not unit_number
        or not property_type
        or not price
    ):

        flash(
            "Please fill all required property fields.",
            "error"
        )

        return redirect("/properties")

    conn = get_db()

    conn.execute("""
        INSERT INTO properties
        (
            project_name,
            building_name,
            unit_number,
            property_type,
            price,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        project_name,
        building_name,
        unit_number,
        property_type,
        price,
        status
    ))

    conn.commit()
    conn.close()

    flash(
        "Property added successfully!",
        "success"
    )

    return redirect("/properties")


# =========================================================
# BOOKINGS
# =========================================================

@app.route("/bookings")
def bookings():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()

    # Admin sees all bookings
    if session["role"] == "Admin":

        bookings = conn.execute("""
            SELECT
                bookings.id,
                bookings.amount,
                bookings.status,
                bookings.booking_date,
                leads.name AS lead_name,
                properties.project_name,
                properties.building_name,
                properties.unit_number,
                properties.property_type,
                users.name AS employee_name
            FROM bookings
            JOIN leads
                ON bookings.lead_id = leads.id
            JOIN properties
                ON bookings.property_id = properties.id
            JOIN users
                ON bookings.booked_by = users.id
            ORDER BY bookings.id DESC
        """).fetchall()

    # Sales Employee sees only their bookings
    else:

        bookings = conn.execute("""
            SELECT
                bookings.id,
                bookings.amount,
                bookings.status,
                bookings.booking_date,
                leads.name AS lead_name,
                properties.project_name,
                properties.building_name,
                properties.unit_number,
                properties.property_type,
                users.name AS employee_name
            FROM bookings
            JOIN leads
                ON bookings.lead_id = leads.id
            JOIN properties
                ON bookings.property_id = properties.id
            JOIN users
                ON bookings.booked_by = users.id
            WHERE bookings.booked_by = ?
            ORDER BY bookings.id DESC
        """, (session["user_id"],)).fetchall()

    # Sales Employee can book only their assigned leads
    if session["role"] == "Admin":

        leads = conn.execute("""
            SELECT *
            FROM leads
            WHERE stage != 'Lost'
            ORDER BY id DESC
        """).fetchall()

    else:

        leads = conn.execute("""
            SELECT *
            FROM leads
            WHERE stage != 'Lost'
            AND assigned_to = ?
            ORDER BY id DESC
        """, (session["user_id"],)).fetchall()

    # Available properties
    available_properties = conn.execute("""
        SELECT *
        FROM properties
        WHERE status = 'Available'
        ORDER BY id DESC
    """).fetchall()

    # Total bookings
    total_bookings = conn.execute("""
        SELECT COUNT(*)
        FROM bookings
        WHERE status = 'Confirmed'
    """).fetchone()[0]

    # Total booking value
    total_value = conn.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM bookings
        WHERE status = 'Confirmed'
    """).fetchone()[0]

    # Available units
    available_units = conn.execute("""
        SELECT COUNT(*)
        FROM properties
        WHERE status = 'Available'
    """).fetchone()[0]

    conn.close()

    return render_template(
        "bookings.html",
        bookings=bookings,
        leads=leads,
        properties=available_properties,
        total_bookings=total_bookings,
        total_value=total_value,
        available_units=available_units,
        name=session["name"],
        role=session["role"]
    )


# =========================================================
# ADD BOOKING
# =========================================================

@app.route("/add-booking", methods=["POST"])
def add_booking():

    if "user_id" not in session:
        return redirect("/login")

    lead_id = request.form.get("lead_id")
    property_id = request.form.get("property_id")
    amount = request.form.get("amount")

    if not lead_id or not property_id:

        flash(
            "Please select a customer and property.",
            "error"
        )

        return redirect("/bookings")

    conn = get_db()

    try:

        # Start transaction
        conn.execute("BEGIN IMMEDIATE")

        # -------------------------------------------------
        # CHECK LEAD
        # -------------------------------------------------

        lead = conn.execute("""
            SELECT *
            FROM leads
            WHERE id = ?
        """, (lead_id,)).fetchone()

        if not lead:

            conn.rollback()

            flash(
                "Customer lead not found.",
                "error"
            )

            return redirect("/bookings")

        # Sales employee can book only assigned leads
        if (
            session["role"] == "Sales Employee"
            and lead["assigned_to"] != session["user_id"]
        ):

            conn.rollback()

            flash(
                "You can only book your assigned leads.",
                "error"
            )

            return redirect("/bookings")

        # -------------------------------------------------
        # CHECK PROPERTY
        # -------------------------------------------------

        property_data = conn.execute("""
            SELECT *
            FROM properties
            WHERE id = ?
        """, (property_id,)).fetchone()

        if not property_data:

            conn.rollback()

            flash(
                "Property not found.",
                "error"
            )

            return redirect("/bookings")

        # Check availability
        if property_data["status"] != "Available":

            conn.rollback()

            flash(
                "This property unit is already booked.",
                "error"
            )

            return redirect("/bookings")

        # -------------------------------------------------
        # DOUBLE BOOKING CHECK
        # -------------------------------------------------

        existing_booking = conn.execute("""
            SELECT id
            FROM bookings
            WHERE property_id = ?
            AND status = 'Confirmed'
        """, (property_id,)).fetchone()

        if existing_booking:

            conn.rollback()

            flash(
                "This property unit is already booked.",
                "error"
            )

            return redirect("/bookings")

        # -------------------------------------------------
        # BOOKING AMOUNT
        # -------------------------------------------------

        if not amount:
            amount = property_data["price"]

        # -------------------------------------------------
        # CREATE BOOKING
        # -------------------------------------------------

        conn.execute("""
            INSERT INTO bookings
            (
                lead_id,
                property_id,
                booked_by,
                amount,
                status
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            lead_id,
            property_id,
            session["user_id"],
            amount,
            "Confirmed"
        ))

        # -------------------------------------------------
        # UPDATE PROPERTY STATUS
        # -------------------------------------------------

        conn.execute("""
            UPDATE properties
            SET status = 'Booked'
            WHERE id = ?
        """, (property_id,))

        # -------------------------------------------------
        # UPDATE LEAD STAGE
        # -------------------------------------------------

        conn.execute("""
            UPDATE leads
            SET stage = 'Booked'
            WHERE id = ?
        """, (lead_id,))

        # Save transaction
        conn.commit()

        flash(
            "Booking created successfully!",
            "success"
        )

    except Exception as e:

        conn.rollback()

        print("Booking Error:", e)

        flash(
            "Booking failed. Please try again.",
            "error"
        )

    finally:

        conn.close()

    return redirect("/bookings")


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

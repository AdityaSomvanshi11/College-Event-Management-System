
import tkinter as tk
from tkinter import ttk, messagebox
from database import get_connection


# =========================================================
# COMMON WINDOW SETTINGS
# =========================================================

def center_window(window, width, height):
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")


def create_treeview(parent, columns, headings):
    frame = ttk.Frame(parent)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    tree = ttk.Treeview(frame, columns=columns, show="headings")

    for column, heading in zip(columns, headings):
        tree.heading(column, text=heading)
        tree.column(column, width=140, anchor="center")

    scrollbar = ttk.Scrollbar(
        frame, orient="vertical", command=tree.yview
    )
    tree.configure(yscrollcommand=scrollbar.set)

    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    return tree


# =========================================================
# STUDENT REGISTRATION
# =========================================================

def register_new_student(parent=None):
    window = tk.Toplevel(parent) if parent else tk.Tk()
    window.title("CampusConnect - Student Registration")
    center_window(window, 550, 700)
    window.resizable(False, False)

    main_frame = ttk.Frame(window, padding=20)
    main_frame.pack(fill="both", expand=True)

    ttk.Label(
        main_frame,
        text="NEW STUDENT REGISTRATION",
        font=("Arial", 16, "bold")
    ).pack(pady=(0, 15))

    form = ttk.Frame(main_frame)
    form.pack(fill="x")

    fields = [
        ("Name", "name"),
        ("University UID", "uid"),
        ("Course", "course"),
        ("Mobile Number", "phone"),
        ("Email", "email"),
        ("Semester", "semester"),
        ("Username", "username"),
        ("Password", "password")
    ]

    entries = {}

    for row, (label_text, key) in enumerate(fields):
        ttk.Label(
            form, text=label_text + ":"
        ).grid(row=row, column=0, padx=8, pady=7, sticky="w")

        entry = ttk.Entry(
            form,
            width=32,
            show="*" if key == "password" else ""
        )
        entry.grid(
            row=row, column=1, padx=8, pady=7, sticky="ew"
        )
        entries[key] = entry

    ttk.Label(form, text="Event Name:").grid(
        row=8, column=0, padx=8, pady=7, sticky="w"
    )

    event_box = ttk.Combobox(form, width=30, state="readonly")
    event_box.grid(
        row=8, column=1, padx=8, pady=7, sticky="ew"
    )

    form.columnconfigure(1, weight=1)
    event_map = {}

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT event_id, event_name
            FROM event
            ORDER BY event_id
        """)

        for event_id, event_name in cursor.fetchall():
            event_map[event_name] = event_id

        event_box["values"] = list(event_map.keys())

    except Exception as error:
        messagebox.showerror(
            "Database Error",
            f"Unable to load events.\n\n{error}",
            parent=window
        )
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    def submit_registration():
        values = {
            key: entry.get().strip()
            for key, entry in entries.items()
        }

        for key, value in values.items():
            if not value:
                messagebox.showwarning(
                    "Missing Information",
                    f"Please enter {key.replace('_', ' ').title()}.",
                    parent=window
                )
                entries[key].focus_set()
                return

        if not event_box.get():
            messagebox.showwarning(
                "Missing Event",
                "Please select an event.",
                parent=window
            )
            return

        if not values["uid"].isalnum():
            messagebox.showwarning(
                "Invalid UID",
                "University UID must contain letters and numbers only.",
                parent=window
            )
            return

        if not values["phone"].isdigit() or len(values["phone"]) != 10:
            messagebox.showwarning(
                "Invalid Mobile Number",
                "Please enter a valid 10-digit mobile number.",
                parent=window
            )
            return

        try:
            semester = int(values["semester"])
            if not 1 <= semester <= 12:
                raise ValueError
        except ValueError:
            messagebox.showwarning(
                "Invalid Semester",
                "Semester must be between 1 and 12.",
                parent=window
            )
            return

        if "@" not in values["email"] or "." not in values["email"]:
            messagebox.showwarning(
                "Invalid Email",
                "Please enter a valid email address.",
                parent=window
            )
            return

        conn = None
        cursor = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT COUNT(*)
                FROM student
                WHERE UPPER(username) = UPPER(:username)
            """, {"username": values["username"]})

            if cursor.fetchone()[0] > 0:
                messagebox.showerror(
                    "Duplicate Username",
                    "This username already exists.",
                    parent=window
                )
                return

            cursor.execute("""
                SELECT COUNT(*)
                FROM student
                WHERE UPPER(university_uid) = UPPER(:uid)
            """, {"uid": values["uid"]})

            if cursor.fetchone()[0] > 0:
                messagebox.showerror(
                    "Duplicate UID",
                    "This University UID already exists.",
                    parent=window
                )
                return

            cursor.execute("""
                SELECT student_seq.NEXTVAL FROM dual
            """)
            student_id = cursor.fetchone()[0]

            cursor.execute("""
                INSERT INTO student (
                    student_id, name, email, phone, course,
                    semester, username, password, university_uid
                )
                VALUES (
                    :student_id, :name, :email, :phone, :course,
                    :semester, :username, :password, :uid
                )
            """, {
                "student_id": student_id,
                "name": values["name"],
                "email": values["email"],
                "phone": values["phone"],
                "course": values["course"],
                "semester": semester,
                "username": values["username"],
                "password": values["password"],
                "uid": values["uid"]
            })

            selected_event_id = event_map[event_box.get()]

            cursor.execute("""
                INSERT INTO registration (
                    registration_id, student_id,
                    event_id, registration_date
                )
                VALUES (
                    registration_seq.NEXTVAL,
                    :student_id, :event_id, SYSDATE
                )
            """, {
                "student_id": student_id,
                "event_id": selected_event_id
            })

            conn.commit()

            messagebox.showinfo(
                "Registration Successful",
                f"Student account created successfully!\n\n"
                f"Student ID: {student_id}\n"
                f"Username: {values['username']}\n"
                f"Event: {event_box.get()}",
                parent=window
            )
            window.destroy()

        except Exception as error:
            if conn:
                conn.rollback()
            messagebox.showerror(
                "Registration Failed",
                str(error),
                parent=window
            )
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    ttk.Button(
        main_frame,
        text="Register Student",
        command=submit_registration
    ).pack(pady=15)

    ttk.Button(
        main_frame,
        text="Close",
        command=window.destroy
    ).pack()


# =========================================================
# STUDENT DASHBOARD
# =========================================================

def open_student_dashboard(student_id, student_name, on_logout=None):
    dashboard = tk.Toplevel()
    dashboard.title("CampusConnect - Student Dashboard")
    center_window(dashboard, 900, 600)

    ttk.Label(
        dashboard,
        text=f"Welcome, {student_name}",
        font=("Arial", 20, "bold")
    ).pack(pady=20)

    ttk.Label(
        dashboard,
        text="College Event Management & Student Participation System",
        font=("Arial", 11)
    ).pack(pady=5)

    button_frame = ttk.Frame(dashboard, padding=20)
    button_frame.pack(fill="both", expand=True)

    ttk.Button(
        button_frame,
        text="View Events",
        command=lambda: view_events(dashboard, student_id)
    ).pack(fill="x", pady=8, ipady=8)

    ttk.Button(
        button_frame,
        text="My Registrations",
        command=lambda: my_registrations(dashboard, student_id)
    ).pack(fill="x", pady=8, ipady=8)

    ttk.Button(
        button_frame,
        text="My Attendance",
        command=lambda: my_attendance(dashboard, student_id)
    ).pack(fill="x", pady=8, ipady=8)

    def logout():
        dashboard.destroy()
        if on_logout:
            on_logout()

    ttk.Button(
        button_frame,
        text="Logout",
        command=logout
    ).pack(fill="x", pady=8, ipady=8)

    dashboard.protocol("WM_DELETE_WINDOW", logout)


# =========================================================
# VIEW EVENTS AND REGISTER
# =========================================================

def view_events(parent, student_id):
    window = tk.Toplevel(parent)
    window.title("CampusConnect - Available Events")
    center_window(window, 950, 500)

    ttk.Label(
        window,
        text="AVAILABLE COLLEGE EVENTS",
        font=("Arial", 16, "bold")
    ).pack(pady=10)

    columns = (
        "event_id", "event_name", "event_date",
        "venue", "description"
    )
    headings = (
        "Event ID", "Event Name", "Event Date",
        "Venue", "Description"
    )

    tree = create_treeview(window, columns, headings)

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT event_id, event_name, event_date,
                   venue, description
            FROM event
            ORDER BY event_date
        """)

        for row in cursor.fetchall():
            tree.insert(
                "", "end",
                values=tuple(
                    "" if value is None else str(value)
                    for value in row
                )
            )

    except Exception as error:
        messagebox.showerror(
            "Database Error", str(error), parent=window
        )
        return
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    def register_for_event():
        selected = tree.selection()

        if not selected:
            messagebox.showwarning(
                "Select Event",
                "Please select an event first.",
                parent=window
            )
            return

        row = tree.item(selected[0], "values")
        event_id = int(row[0])
        event_name = row[1]

        conn = None
        cursor = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT COUNT(*)
                FROM registration
                WHERE student_id = :student_id
                  AND event_id = :event_id
            """, {
                "student_id": student_id,
                "event_id": event_id
            })

            if cursor.fetchone()[0] > 0:
                messagebox.showinfo(
                    "Already Registered",
                    f"You are already registered for {event_name}.",
                    parent=window
                )
                return

            cursor.execute("""
                INSERT INTO registration (
                    registration_id, student_id,
                    event_id, registration_date
                )
                VALUES (
                    registration_seq.NEXTVAL,
                    :student_id, :event_id, SYSDATE
                )
            """, {
                "student_id": student_id,
                "event_id": event_id
            })

            conn.commit()
            messagebox.showinfo(
                "Success",
                f"Registration successful for {event_name}.",
                parent=window
            )

        except Exception as error:
            if conn:
                conn.rollback()
            messagebox.showerror(
                "Registration Error", str(error), parent=window
            )
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    ttk.Button(
        window,
        text="Register for Selected Event",
        command=register_for_event
    ).pack(pady=10)


# =========================================================
# MY REGISTRATIONS AND CANCELLATION
# =========================================================

def my_registrations(parent, student_id):
    window = tk.Toplevel(parent)
    window.title("CampusConnect - My Registrations")
    center_window(window, 900, 500)

    ttk.Label(
        window,
        text="MY EVENT REGISTRATIONS",
        font=("Arial", 16, "bold")
    ).pack(pady=10)

    columns = (
        "registration_id", "event_id", "event_name",
        "event_date", "registration_date"
    )
    headings = (
        "Registration ID", "Event ID", "Event Name",
        "Event Date", "Registration Date"
    )

    tree = create_treeview(window, columns, headings)

    def load_registrations():
        for item in tree.get_children():
            tree.delete(item)

        conn = None
        cursor = None

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT r.registration_id, r.event_id,
                       e.event_name, e.event_date,
                       r.registration_date
                FROM registration r
                JOIN event e ON r.event_id = e.event_id
                WHERE r.student_id = :student_id
                ORDER BY r.registration_date DESC
            """, {"student_id": student_id})

            for row in cursor.fetchall():
                tree.insert(
                    "", "end",
                    values=tuple(
                        "" if value is None else str(value)
                        for value in row
                    )
                )

        except Exception as error:
            messagebox.showerror(
                "Database Error", str(error), parent=window
            )
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def cancel_registration():
        selected = tree.selection()

        if not selected:
            messagebox.showwarning(
                "Select Registration",
                "Please select a registration to cancel.",
                parent=window
            )
            return

        row = tree.item(selected[0], "values")
        registration_id = int(row[0])
        event_name = row[2]

        confirm = messagebox.askyesno(
            "Confirm Cancellation",
            f"Do you want to cancel your registration for {event_name}?",
            parent=window
        )

        if not confirm:
            return

        conn = None
        cursor = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            # ATTENDANCE is linked to REGISTRATION_ID.
            cursor.execute("""
                SELECT COUNT(*)
                FROM attendance
                WHERE registration_id = :registration_id
            """, {"registration_id": registration_id})

            if cursor.fetchone()[0] > 0:
                messagebox.showwarning(
                    "Cancellation Not Allowed",
                    "Attendance has already been recorded. "
                    "This registration cannot be cancelled.",
                    parent=window
                )
                return

            cursor.execute("""
                DELETE FROM registration
                WHERE registration_id = :registration_id
                  AND student_id = :student_id
            """, {
                "registration_id": registration_id,
                "student_id": student_id
            })

            if cursor.rowcount == 0:
                conn.rollback()
                messagebox.showwarning(
                    "Registration Not Found",
                    "The selected registration was not found.",
                    parent=window
                )
                return

            conn.commit()
            messagebox.showinfo(
                "Success",
                f"Registration for {event_name} cancelled successfully.",
                parent=window
            )
            load_registrations()

        except Exception as error:
            if conn:
                conn.rollback()
            messagebox.showerror(
                "Cancellation Error", str(error), parent=window
            )
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    button_frame = ttk.Frame(window)
    button_frame.pack(pady=10)

    ttk.Button(
        button_frame,
        text="Cancel Selected Registration",
        command=cancel_registration
    ).pack(side="left", padx=5)

    ttk.Button(
        button_frame,
        text="Refresh",
        command=load_registrations
    ).pack(side="left", padx=5)

    load_registrations()


# =========================================================
# MY ATTENDANCE
# =========================================================

def my_attendance(parent, student_id):
    window = tk.Toplevel(parent)
    window.title("CampusConnect - My Attendance")
    center_window(window, 900, 500)

    ttk.Label(
        window,
        text="MY EVENT ATTENDANCE",
        font=("Arial", 16, "bold")
    ).pack(pady=10)

    columns = (
        "attendance_id", "event_name",
        "attendance_date", "status"
    )
    headings = (
        "Attendance ID", "Event Name",
        "Attendance Date", "Status"
    )

    tree = create_treeview(window, columns, headings)

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Attendance schema: ATTENDANCE_ID, REGISTRATION_ID,
        # STATUS, ATTENDANCE_DATE.
        cursor.execute("""
            SELECT a.attendance_id,
                   e.event_name,
                   a.attendance_date,
                   a.status
            FROM attendance a
            JOIN registration r
              ON a.registration_id = r.registration_id
            JOIN event e
              ON r.event_id = e.event_id
            WHERE r.student_id = :student_id
            ORDER BY a.attendance_date DESC
        """, {"student_id": student_id})

        rows = cursor.fetchall()

        for row in rows:
            tree.insert(
                "", "end",
                values=tuple(
                    "" if value is None else str(value)
                    for value in row
                )
            )

        if not rows:
            ttk.Label(
                window,
                text="No attendance records found."
            ).pack(pady=5)

    except Exception as error:
        messagebox.showerror(
            "Database Error", str(error), parent=window
        )
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# =========================================================
# ADMIN: MANAGE STUDENTS
# =========================================================

def manage_students():
    window = tk.Toplevel()
    window.title("CampusConnect - Manage Students")
    center_window(window, 1000, 500)

    ttk.Label(
        window,
        text="MANAGE STUDENTS",
        font=("Arial", 16, "bold")
    ).pack(pady=10)

    columns = (
        "student_id", "name", "university_uid", "course",
        "phone", "email", "semester", "username"
    )
    headings = (
        "Student ID", "Name", "University UID", "Course",
        "Phone", "Email", "Semester", "Username"
    )

    tree = create_treeview(window, columns, headings)

    def load_students():
        for item in tree.get_children():
            tree.delete(item)

        conn = None
        cursor = None

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT student_id, name, university_uid, course,
                       phone, email, semester, username
                FROM student
                ORDER BY student_id
            """)

            for row in cursor.fetchall():
                tree.insert(
                    "", "end",
                    values=tuple(
                        "" if value is None else str(value)
                        for value in row
                    )
                )

        except Exception as error:
            messagebox.showerror(
                "Database Error", str(error), parent=window
            )
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    ttk.Button(
        window,
        text="Refresh Students",
        command=load_students
    ).pack(pady=10)

    load_students()


# =========================================================
# RUN THIS FILE DIRECTLY FOR TESTING
# =========================================================

if __name__ == "__main__":
    root = tk.Tk()
    root.title("CampusConnect - Student Module")
    center_window(root, 400, 250)

    ttk.Label(
        root,
        text="CampusConnect Student Module",
        font=("Arial", 14, "bold")
    ).pack(pady=20)

    ttk.Button(
        root,
        text="New Student Registration",
        command=lambda: register_new_student(root)
    ).pack(pady=10)

    ttk.Button(
        root,
        text="Close",
        command=root.destroy
    ).pack(pady=10)

    root.mainloop()

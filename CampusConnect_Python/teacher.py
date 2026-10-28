
import tkinter as tk
from tkinter import messagebox, ttk
from database import get_connection


# ==========================================
# ADMIN: MANAGE TEACHERS
# ==========================================

def manage_teachers():
    window = tk.Toplevel()
    window.title("CampusConnect - Manage Teachers")
    window.geometry("900x600")

    tk.Label(
        window,
        text="MANAGE TEACHERS",
        font=("Arial", 20, "bold")
    ).pack(pady=15)

    form = tk.Frame(window)
    form.pack(pady=10)

    fields = [
        ("Name", 0),
        ("Email", 1),
        ("Phone", 2),
        ("Department", 3),
        ("Username", 4),
        ("Password", 5)
    ]

    entries = {}

    for label_text, row in fields:
        tk.Label(form, text=label_text).grid(
            row=row, column=0, padx=10, pady=5
        )

        entry = tk.Entry(
            form,
            width=30,
            show="*" if label_text == "Password" else ""
        )
        entry.grid(row=row, column=1, padx=10, pady=5)
        entries[label_text] = entry

    columns = (
        "ID", "Name", "Email", "Phone",
        "Department", "Username"
    )

    table_frame = tk.Frame(window)
    table_frame.pack(fill="both", expand=True, padx=15, pady=10)

    table = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings",
        height=10
    )

    for column in columns:
        table.heading(column, text=column)
        table.column(column, width=125, anchor="center")

    scrollbar = ttk.Scrollbar(
        table_frame,
        orient="vertical",
        command=table.yview
    )
    table.configure(yscrollcommand=scrollbar.set)

    table.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def clear_fields():
        for entry in entries.values():
            entry.delete(0, tk.END)

    def load_teachers():
        table.delete(*table.get_children())

        conn = None
        cursor = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT teacher_id, name, email, phone,
                       department, username
                FROM teacher
                ORDER BY teacher_id
            """)

            for row in cursor.fetchall():
                table.insert("", tk.END, values=row)

        except Exception as e:
            messagebox.showerror(
                "Database Error", str(e), parent=window
            )

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def add_teacher():
        name = entries["Name"].get().strip()
        email = entries["Email"].get().strip()
        phone = entries["Phone"].get().strip()
        department = entries["Department"].get().strip()
        username = entries["Username"].get().strip()
        password = entries["Password"].get()

        if not all([
            name, email, phone,
            department, username, password
        ]):
            messagebox.showwarning(
                "Missing Information",
                "Please fill in all fields.",
                parent=window
            )
            return

        conn = None
        cursor = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO teacher (
                    teacher_id, name, email, phone,
                    department, username, password
                )
                VALUES (
                    teacher_seq.NEXTVAL, :name, :email,
                    :phone, :department, :username, :password
                )
            """, {
                "name": name,
                "email": email,
                "phone": phone,
                "department": department,
                "username": username,
                "password": password
            })

            conn.commit()

            messagebox.showinfo(
                "Success",
                "Teacher added successfully!",
                parent=window
            )

            clear_fields()
            load_teachers()

        except Exception as e:
            if conn:
                conn.rollback()

            messagebox.showerror(
                "Database Error", str(e), parent=window
            )

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    buttons = tk.Frame(window)
    buttons.pack(pady=10)

    tk.Button(
        buttons,
        text="ADD TEACHER",
        width=18,
        command=add_teacher
    ).pack(side="left", padx=5)

    tk.Button(
        buttons,
        text="CLEAR FIELDS",
        width=18,
        command=clear_fields
    ).pack(side="left", padx=5)

    load_teachers()


# ==========================================
# TEACHER DASHBOARD
# ==========================================

def open_teacher_dashboard(
    teacher_id,
    teacher_name,
    on_logout=None
):
    dashboard = tk.Toplevel()
    dashboard.title("CampusConnect - Teacher Dashboard")
    dashboard.geometry("500x480")

    tk.Label(
        dashboard,
        text="TEACHER DASHBOARD",
        font=("Arial", 20, "bold")
    ).pack(pady=20)

    tk.Label(
        dashboard,
        text="Welcome " + teacher_name,
        font=("Arial", 13)
    ).pack(pady=5)

    tk.Label(
        dashboard,
        text="Teacher ID: " + str(teacher_id),
        font=("Arial", 11)
    ).pack(pady=5)

    tk.Button(
        dashboard,
        text="My Events",
        width=25,
        command=lambda: show_my_events(teacher_id)
    ).pack(pady=8)

    tk.Button(
        dashboard,
        text="Registered Students",
        width=25,
        command=lambda: show_registered_students(teacher_id)
    ).pack(pady=8)

    tk.Button(
        dashboard,
        text="Mark Attendance",
        width=25,
        command=lambda: mark_attendance(teacher_id)
    ).pack(pady=8)

    tk.Button(
        dashboard,
        text="View Attendance",
        width=25,
        command=lambda: view_attendance(teacher_id)
    ).pack(pady=8)

    def logout():
        dashboard.destroy()

        if on_logout:
            on_logout()

    tk.Button(
        dashboard,
        text="Logout",
        width=25,
        command=logout
    ).pack(pady=15)


# ==========================================
# TEACHER: MY ASSIGNED EVENTS
# ==========================================

def show_my_events(teacher_id):
    window = tk.Toplevel()
    window.title("CampusConnect - My Events")
    window.geometry("850x400")

    tk.Label(
        window,
        text="MY ASSIGNED EVENTS",
        font=("Arial", 18, "bold")
    ).pack(pady=15)

    columns = (
        "Event ID",
        "Event Name",
        "Description",
        "Event Date",
        "Venue"
    )

    table = ttk.Treeview(
        window,
        columns=columns,
        show="headings"
    )

    for column in columns:
        table.heading(column, text=column)
        table.column(column, width=150, anchor="center")

    table.pack(fill="both", expand=True, padx=10, pady=10)

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT event_id, event_name, description,
                   event_date, venue
            FROM event
            WHERE teacher_id = :teacher_id
            ORDER BY event_date
        """, {"teacher_id": teacher_id})

        for row in cursor.fetchall():
            event_id, name, description, event_date, venue = row

            date_text = (
                event_date.strftime("%d-%m-%Y")
                if event_date else ""
            )

            table.insert(
                "",
                tk.END,
                values=(
                    event_id,
                    name,
                    description or "",
                    date_text,
                    venue or ""
                )
            )

    except Exception as e:
        messagebox.showerror(
            "Database Error", str(e), parent=window
        )

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# ==========================================
# TEACHER: REGISTERED STUDENTS
# ==========================================

def show_registered_students(teacher_id):
    window = tk.Toplevel()
    window.title("CampusConnect - Registered Students")
    window.geometry("900x450")

    tk.Label(
        window,
        text="REGISTERED STUDENTS",
        font=("Arial", 18, "bold")
    ).pack(pady=15)

    columns = (
        "Student ID",
        "Student Name",
        "Course",
        "Event Name",
        "Registration Date"
    )

    table = ttk.Treeview(
        window,
        columns=columns,
        show="headings"
    )

    for column in columns:
        table.heading(column, text=column)
        table.column(column, width=165, anchor="center")

    table.pack(fill="both", expand=True, padx=10, pady=10)

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT s.student_id, s.name, s.course,
                   e.event_name, r.registration_date
            FROM registration r
            JOIN student s
                ON s.student_id = r.student_id
            JOIN event e
                ON e.event_id = r.event_id
            WHERE e.teacher_id = :teacher_id
            ORDER BY e.event_name, s.name
        """, {"teacher_id": teacher_id})

        rows = cursor.fetchall()

        for student_id, name, course, event_name, reg_date in rows:
            date_text = (
                reg_date.strftime("%d-%m-%Y")
                if reg_date else ""
            )

            table.insert(
                "",
                tk.END,
                values=(
                    student_id,
                    name,
                    course or "",
                    event_name,
                    date_text
                )
            )

        if not rows:
            messagebox.showinfo(
                "No Registrations",
                "No students are registered for your events yet.",
                parent=window
            )

    except Exception as e:
        messagebox.showerror(
            "Database Error", str(e), parent=window
        )

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# ==========================================
# TEACHER: MARK ATTENDANCE
# ==========================================

def mark_attendance(teacher_id):
    window = tk.Toplevel()
    window.title("CampusConnect - Mark Attendance")
    window.geometry("950x450")

    tk.Label(
        window,
        text="MARK ATTENDANCE",
        font=("Arial", 18, "bold")
    ).pack(pady=15)

    columns = (
        "Registration ID",
        "Student Name",
        "Event Name",
        "Status"
    )

    table = ttk.Treeview(
        window,
        columns=columns,
        show="headings",
        height=12
    )

    for column in columns:
        table.heading(column, text=column)
        table.column(column, width=200, anchor="center")

    table.pack(fill="both", expand=True, padx=10, pady=10)

    controls = tk.Frame(window)
    controls.pack(pady=10)

    tk.Label(
        controls,
        text="Attendance Status:"
    ).pack(side="left", padx=5)

    status_var = tk.StringVar(value="Present")

    status_box = ttk.Combobox(
        controls,
        textvariable=status_var,
        values=["Present", "Absent"],
        state="readonly",
        width=12
    )
    status_box.pack(side="left", padx=5)

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT r.registration_id, s.name,
                   e.event_name, a.status
            FROM registration r
            JOIN student s
                ON s.student_id = r.student_id
            JOIN event e
                ON e.event_id = r.event_id
            LEFT JOIN attendance a
                ON a.registration_id = r.registration_id
            WHERE e.teacher_id = :teacher_id
            ORDER BY e.event_name, s.name
        """, {"teacher_id": teacher_id})

        for row in cursor.fetchall():
            table.insert(
                "",
                tk.END,
                values=(
                    row[0],
                    row[1],
                    row[2],
                    row[3] or "Not Marked"
                )
            )

    except Exception as e:
        messagebox.showerror(
            "Database Error", str(e), parent=window
        )

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    def save_attendance():
        selected = table.selection()

        if not selected:
            messagebox.showwarning(
                "Select Student",
                "Please select a registered student first.",
                parent=window
            )
            return

        values = table.item(selected[0], "values")
        registration_id = int(values[0])
        status = status_var.get()

        if status not in ("Present", "Absent"):
            messagebox.showwarning(
                "Invalid Status",
                "Select Present or Absent.",
                parent=window
            )
            return

        conn = None
        cursor = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Verify that this registration belongs
            # to an event assigned to the logged-in teacher.
            cursor.execute("""
                SELECT r.registration_id
                FROM registration r
                JOIN event e
                    ON e.event_id = r.event_id
                WHERE r.registration_id = :registration_id
                  AND e.teacher_id = :teacher_id
            """, {
                "registration_id": registration_id,
                "teacher_id": teacher_id
            })

            if not cursor.fetchone():
                messagebox.showerror(
                    "Access Denied",
                    "You cannot update this event's attendance.",
                    parent=window
                )
                return

            cursor.execute("""
                SELECT attendance_id
                FROM attendance
                WHERE registration_id = :registration_id
            """, {"registration_id": registration_id})

            existing = cursor.fetchone()

            if existing:
                cursor.execute("""
                    UPDATE attendance
                    SET status = :status,
                        attendance_date = SYSDATE
                    WHERE registration_id = :registration_id
                """, {
                    "status": status,
                    "registration_id": registration_id
                })
            else:
                cursor.execute("""
                    INSERT INTO attendance (
                        attendance_id,
                        registration_id,
                        status,
                        attendance_date
                    )
                    VALUES (
                        attendance_seq.NEXTVAL,
                        :registration_id,
                        :status,
                        SYSDATE
                    )
                """, {
                    "registration_id": registration_id,
                    "status": status
                })

            conn.commit()

            table.item(
                selected[0],
                values=(
                    values[0],
                    values[1],
                    values[2],
                    status
                )
            )

            messagebox.showinfo(
                "Success",
                "Attendance saved successfully!",
                parent=window
            )

        except Exception as e:
            if conn:
                conn.rollback()

            messagebox.showerror(
                "Database Error", str(e), parent=window
            )

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    tk.Button(
        window,
        text="SAVE ATTENDANCE",
        width=22,
        command=save_attendance
    ).pack(pady=10)


# ==========================================
# TEACHER: VIEW ATTENDANCE REPORT
# ==========================================

def view_attendance(teacher_id):
    window = tk.Toplevel()
    window.title("CampusConnect - Attendance Report")
    window.geometry("950x450")

    tk.Label(
        window,
        text="ATTENDANCE REPORT",
        font=("Arial", 18, "bold")
    ).pack(pady=15)

    columns = (
        "Student",
        "Event",
        "Status",
        "Attendance Date"
    )

    table = ttk.Treeview(
        window,
        columns=columns,
        show="headings"
    )

    for column in columns:
        table.heading(column, text=column)
        table.column(column, width=210, anchor="center")

    table.pack(fill="both", expand=True, padx=10, pady=10)

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT s.name, e.event_name,
                   a.status, a.attendance_date
            FROM attendance a
            JOIN registration r
                ON r.registration_id = a.registration_id
            JOIN student s
                ON s.student_id = r.student_id
            JOIN event e
                ON e.event_id = r.event_id
            WHERE e.teacher_id = :teacher_id
            ORDER BY a.attendance_date DESC, s.name
        """, {"teacher_id": teacher_id})

        rows = cursor.fetchall()

        for name, event_name, status, attendance_date in rows:
            date_text = (
                attendance_date.strftime("%d-%m-%Y")
                if attendance_date else ""
            )

            table.insert(
                "",
                tk.END,
                values=(name, event_name, status, date_text)
            )

        if not rows:
            messagebox.showinfo(
                "No Attendance",
                "No attendance records found for your events.",
                parent=window
            )

    except Exception as e:
        messagebox.showerror(
            "Database Error", str(e), parent=window
        )

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# ==========================================
# RUN THIS FILE DIRECTLY FOR TESTING
# ==========================================

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    manage_teachers()
    root.mainloop()

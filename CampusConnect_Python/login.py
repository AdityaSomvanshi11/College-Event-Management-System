import tkinter as tk
from tkinter import messagebox, ttk

from database import get_connection
from admin import open_admin_dashboard
from teacher import open_teacher_dashboard
from student import open_student_dashboard, register_new_student


def login(role):
    username = username_entries[role].get().strip()
    password = password_entries[role].get()

    if not username or not password:
        messagebox.showwarning(
            "Missing Information",
            "Please enter username and password.",
            parent=root
        )
        return

    conn = None
    cursor = None
    dashboard_opened = False

    try:
        conn = get_connection()
        cursor = conn.cursor()

        if role == "Admin":
            cursor.execute("""
                SELECT name
                FROM admin
                WHERE username = :username
                AND password = :password
            """, {
                "username": username,
                "password": password
            })

            result = cursor.fetchone()

            if result:
                messagebox.showinfo(
                    "Login Successful",
                    "Welcome Admin " + result[0],
                    parent=root
                )

                root.withdraw()
                dashboard_opened = True

                try:
                    open_admin_dashboard()
                except Exception:
                    root.deiconify()
                    raise

                return

        elif role == "Teacher":
            cursor.execute("""
                SELECT teacher_id, name
                FROM teacher
                WHERE username = :username
                AND password = :password
            """, {
                "username": username,
                "password": password
            })

            result = cursor.fetchone()

            if result:
                teacher_id, teacher_name = result

                messagebox.showinfo(
                    "Login Successful",
                    "Welcome Teacher " + teacher_name,
                    parent=root
                )

                root.withdraw()
                dashboard_opened = True

                try:
                    open_teacher_dashboard(
                        teacher_id,
                        teacher_name,
                        on_logout=show_login
                    )
                except Exception:
                    root.deiconify()
                    raise

                return

        else:
            cursor.execute("""
                SELECT student_id, name
                FROM student
                WHERE username = :username
                AND password = :password
            """, {
                "username": username,
                "password": password
            })

            result = cursor.fetchone()

            if result:
                student_id, student_name = result

                messagebox.showinfo(
                    "Login Successful",
                    "Welcome Student " + student_name,
                    parent=root
                )

                root.withdraw()
                dashboard_opened = True

                try:
                    open_student_dashboard(
                        student_id,
                        student_name,
                        on_logout=show_login
                    )
                except Exception:
                    root.deiconify()
                    raise

                return

        messagebox.showerror(
            "Login Failed",
            "Invalid username or password.",
            parent=root
        )

    except Exception as e:
        if dashboard_opened:
            root.deiconify()

        messagebox.showerror(
            "Error",
            str(e),
            parent=root
        )

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()


def show_login():
    if not root.winfo_exists():
        return

    root.deiconify()
    root.lift()

    for role in roles:
        username_entries[role].delete(0, tk.END)
        password_entries[role].delete(0, tk.END)

    username_entries[current_role()].focus_set()


def current_role():
    return roles[notebook.index(notebook.select())]


def close_app():
    root.destroy()


# Main login window
root = tk.Tk()
root.title("CampusConnect - Login")
root.geometry("520x430")
root.resizable(False, False)
root.configure(bg="#f3f6fb")

header = tk.Frame(root, bg="#17365d", height=100)
header.pack(fill="x")

tk.Label(
    header,
    text="CAMPUSCONNECT",
    font=("Arial", 23, "bold"),
    fg="white",
    bg="#17365d"
).pack(pady=(18, 2))

tk.Label(
    header,
    text="College Event Management System",
    font=("Arial", 10),
    fg="white",
    bg="#17365d"
).pack(pady=(0, 12))

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True, padx=25, pady=18)

roles = ["Admin", "Teacher", "Student"]
username_entries = {}
password_entries = {}

for role in roles:
    frame = tk.Frame(
        notebook,
        bg="white",
        padx=25,
        pady=20
    )

    notebook.add(frame, text=role.upper())

    tk.Label(
        frame,
        text=f"{role} Login",
        font=("Arial", 15, "bold"),
        bg="white",
        fg="#17365d"
    ).pack(pady=(0, 12))

    tk.Label(
        frame,
        text="Username",
        bg="white",
        anchor="w"
    ).pack(fill="x")

    username_entry = tk.Entry(
        frame,
        font=("Arial", 11),
        relief="solid",
        bd=1
    )
    username_entry.pack(fill="x", ipady=5, pady=(3, 9))

    tk.Label(
        frame,
        text="Password",
        bg="white",
        anchor="w"
    ).pack(fill="x")

    password_entry = tk.Entry(
        frame,
        font=("Arial", 11),
        show="*",
        relief="solid",
        bd=1
    )
    password_entry.pack(fill="x", ipady=5, pady=(3, 12))

    username_entries[role] = username_entry
    password_entries[role] = password_entry

    tk.Button(
        frame,
        text="LOGIN",
        font=("Arial", 10, "bold"),
        bg="#17365d",
        fg="white",
        activebackground="#254f7d",
        activeforeground="white",
        width=18,
        command=lambda r=role: login(r)
    ).pack(pady=4)

    if role == "Student":
        tk.Button(
            frame,
            text="New User? Register Here",
            relief="flat",
            fg="#145da0",
            bg="white",
            cursor="hand2",
            command=lambda: register_new_student(root)
        ).pack(pady=(8, 0))

root.protocol("WM_DELETE_WINDOW", close_app)
root.mainloop()
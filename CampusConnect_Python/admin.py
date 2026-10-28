import tkinter as tk
from tkinter import messagebox

from teacher import manage_teachers
from student import manage_students
from event import manage_events
from registration import manage_registrations
from attendance import manage_attendance


# ==========================================
# ADMIN DASHBOARD
# ==========================================

def open_admin_dashboard():

    dashboard = tk.Toplevel()
    dashboard.title("CampusConnect - Admin Dashboard")
    dashboard.geometry("600x550")
    dashboard.resizable(False, False)

    # Main heading
    tk.Label(
        dashboard,
        text="CAMPUSCONNECT",
        font=("Arial", 24, "bold")
    ).pack(pady=15)

    tk.Label(
        dashboard,
        text="ADMIN DASHBOARD",
        font=("Arial", 16, "bold")
    ).pack(pady=5)

    # Manage Teachers
    tk.Button(
        dashboard,
        text="Manage Teachers",
        width=25,
        height=2,
        command=manage_teachers
    ).pack(pady=8)

    # Manage Students
    tk.Button(
        dashboard,
        text="Manage Students",
        width=25,
        height=2,
        command=manage_students
    ).pack(pady=8)

    # Manage Events
    tk.Button(
        dashboard,
        text="Manage Events",
        width=25,
        height=2,
        command=manage_events
    ).pack(pady=8)

    # Manage Registrations
    tk.Button(
        dashboard,
        text="Manage Registrations",
        width=25,
        height=2,
        command=manage_registrations
    ).pack(pady=8)

    # View Attendance
    tk.Button(
        dashboard,
        text="View Attendance",
        width=25,
        height=2,
        command=manage_attendance
    ).pack(pady=8)

    # Logout
    tk.Button(
        dashboard,
        text="LOGOUT",
        width=20,
        command=dashboard.destroy
    ).pack(pady=15)


# ==========================================
# RUN ADMIN DASHBOARD DIRECTLY
# ==========================================

if __name__ == "__main__":

    root = tk.Tk()
    root.withdraw()

    open_admin_dashboard()

    root.mainloop()
    
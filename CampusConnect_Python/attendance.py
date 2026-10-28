import tkinter as tk
from tkinter import messagebox, ttk
from database import get_connection


def manage_attendance():

    window = tk.Toplevel()
    window.title("CampusConnect - Attendance")
    window.geometry("900x600")

    tk.Label(
        window,
        text="ATTENDANCE",
        font=("Arial", 20, "bold")
    ).pack(pady=15)

    # ---------- Load Attendance ----------
    def load_attendance():

        for item in table.get_children():
            table.delete(item)

        conn = None
        cursor = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    a.attendance_id,
                    s.name,
                    e.event_name,
                    a.status,
                    TO_CHAR(a.attendance_date, 'DD-MM-YYYY')
                FROM attendance a
                JOIN registration r
                    ON a.registration_id = r.registration_id
                JOIN student s
                    ON r.student_id = s.student_id
                JOIN event e
                    ON r.event_id = e.event_id
                ORDER BY a.attendance_id
            """)

            for row in cursor:
                table.insert("", tk.END, values=row)

        except Exception as e:
            messagebox.showerror(
                "Database Error",
                str(e)
            )

        finally:
            if cursor:
                cursor.close()

            if conn:
                conn.close()

    # ---------- Table ----------
    columns = (
        "Attendance ID",
        "Student",
        "Event",
        "Status",
        "Date"
    )

    table = ttk.Treeview(
        window,
        columns=columns,
        show="headings",
        height=15
    )

    for column in columns:
        table.heading(column, text=column)
        table.column(column, width=160)

    table.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=20
    )

    load_attendance()


if __name__ == "__main__":

    root = tk.Tk()
    root.withdraw()

    manage_attendance()

    root.mainloop()
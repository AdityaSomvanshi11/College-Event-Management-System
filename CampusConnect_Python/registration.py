import tkinter as tk
from tkinter import messagebox, ttk
from database import get_connection


def manage_registrations():

    window = tk.Toplevel()
    window.title("CampusConnect - Manage Registrations")
    window.geometry("900x600")

    tk.Label(
        window,
        text="MANAGE REGISTRATIONS",
        font=("Arial", 20, "bold")
    ).pack(pady=15)

    # ---------- Registration Form ----------
    form = tk.Frame(window)
    form.pack(pady=10)

    tk.Label(
        form,
        text="Student ID"
    ).grid(row=0, column=0, padx=10, pady=5)

    student_id_entry = tk.Entry(form, width=30)
    student_id_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(
        form,
        text="Event ID"
    ).grid(row=1, column=0, padx=10, pady=5)

    event_id_entry = tk.Entry(form, width=30)
    event_id_entry.grid(row=1, column=1, padx=10, pady=5)

    # ---------- Clear Fields ----------
    def clear_fields():
        student_id_entry.delete(0, tk.END)
        event_id_entry.delete(0, tk.END)

    # ---------- Load Registrations ----------
    def load_registrations():

        for item in table.get_children():
            table.delete(item)

        conn = None
        cursor = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    r.registration_id,
                    s.name,
                    e.event_name,
                    TO_CHAR(r.registration_date, 'DD-MM-YYYY')
                FROM registration r
                JOIN student s
                    ON r.student_id = s.student_id
                JOIN event e
                    ON r.event_id = e.event_id
                ORDER BY r.registration_id
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

    # ---------- Add Registration ----------
    def add_registration():

        student_id = student_id_entry.get()
        event_id = event_id_entry.get()

        if not student_id or not event_id:
            messagebox.showwarning(
                "Warning",
                "Please enter Student ID and Event ID"
            )
            return

        conn = None
        cursor = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO registration (
                    registration_id,
                    student_id,
                    event_id
                )
                VALUES (
                    registration_seq.NEXTVAL,
                    :student_id,
                    :event_id
                )
            """,
            student_id=int(student_id),
            event_id=int(event_id))

            conn.commit()

            messagebox.showinfo(
                "Success",
                "Student registered successfully!"
            )

            clear_fields()
            load_registrations()

        except Exception as e:
            messagebox.showerror(
                "Registration Error",
                str(e)
            )

        finally:
            if cursor:
                cursor.close()

            if conn:
                conn.close()

    # ---------- Register Button ----------
    tk.Button(
        window,
        text="REGISTER STUDENT",
        width=20,
        command=add_registration
    ).pack(pady=10)

    # ---------- Registration Table ----------
    columns = (
        "Registration ID",
        "Student",
        "Event",
        "Registration Date"
    )

    table = ttk.Treeview(
        window,
        columns=columns,
        show="headings",
        height=12
    )

    for column in columns:
        table.heading(column, text=column)
        table.column(column, width=180)

    table.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=10
    )

    load_registrations()


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    manage_registrations()

    root.mainloop()
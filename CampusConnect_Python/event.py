import tkinter as tk
from tkinter import messagebox, ttk
from database import get_connection


def manage_events():

    window = tk.Toplevel()
    window.title("CampusConnect - Manage Events")
    window.geometry("1000x650")

    tk.Label(
        window,
        text="MANAGE EVENTS",
        font=("Arial", 20, "bold")
    ).pack(pady=15)

    # ---------- Form ----------
    form = tk.Frame(window)
    form.pack(pady=10)

    tk.Label(form, text="Event Name").grid(
        row=0, column=0, padx=10, pady=5
    )
    event_name_entry = tk.Entry(form, width=30)
    event_name_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(form, text="Description").grid(
        row=1, column=0, padx=10, pady=5
    )
    description_entry = tk.Entry(form, width=30)
    description_entry.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(form, text="Event Date (DD-MM-YYYY)").grid(
        row=2, column=0, padx=10, pady=5
    )
    event_date_entry = tk.Entry(form, width=30)
    event_date_entry.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(form, text="Venue").grid(
        row=3, column=0, padx=10, pady=5
    )
    venue_entry = tk.Entry(form, width=30)
    venue_entry.grid(row=3, column=1, padx=10, pady=5)

    tk.Label(form, text="Teacher ID").grid(
        row=4, column=0, padx=10, pady=5
    )
    teacher_id_entry = tk.Entry(form, width=30)
    teacher_id_entry.grid(row=4, column=1, padx=10, pady=5)

    # ---------- Clear fields ----------
    def clear_fields():
        event_name_entry.delete(0, tk.END)
        description_entry.delete(0, tk.END)
        event_date_entry.delete(0, tk.END)
        venue_entry.delete(0, tk.END)
        teacher_id_entry.delete(0, tk.END)

    # ---------- Load Events ----------
    def load_events():

        for item in table.get_children():
            table.delete(item)

        conn = None
        cursor = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    e.event_id,
                    e.event_name,
                    e.description,
                    TO_CHAR(e.event_date, 'DD-MM-YYYY'),
                    e.venue,
                    t.name
                FROM event e
                JOIN teacher t
                    ON e.teacher_id = t.teacher_id
                ORDER BY e.event_id
            """)

            for row in cursor:
                table.insert("", tk.END, values=row)

        except Exception as e:
            messagebox.showerror("Database Error", str(e))

        finally:
            if cursor:
                cursor.close()

            if conn:
                conn.close()

    # ---------- Add Event ----------
    def add_event():

        event_name = event_name_entry.get()
        description = description_entry.get()
        event_date = event_date_entry.get()
        venue = venue_entry.get()
        teacher_id = teacher_id_entry.get()

        if not all([
            event_name,
            description,
            event_date,
            venue,
            teacher_id
        ]):
            messagebox.showwarning(
                "Warning",
                "Please fill all fields"
            )
            return

        conn = None
        cursor = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO event (
                    event_id,
                    event_name,
                    description,
                    event_date,
                    venue,
                    teacher_id
                )
                VALUES (
                    event_seq.NEXTVAL,
                    :event_name,
                    :description,
                    TO_DATE(:event_date, 'DD-MM-YYYY'),
                    :venue,
                    :teacher_id
                )
            """,
            event_name=event_name,
            description=description,
            event_date=event_date,
            venue=venue,
            teacher_id=int(teacher_id))

            conn.commit()

            messagebox.showinfo(
                "Success",
                "Event added successfully!"
            )

            clear_fields()
            load_events()

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

    # ---------- Add Button ----------
    tk.Button(
        window,
        text="ADD EVENT",
        width=20,
        command=add_event
    ).pack(pady=10)

    # ---------- Event Table ----------
    columns = (
        "ID",
        "Event Name",
        "Description",
        "Date",
        "Venue",
        "Teacher"
    )

    table = ttk.Treeview(
        window,
        columns=columns,
        show="headings",
        height=10
    )

    for column in columns:
        table.heading(column, text=column)
        table.column(column, width=140)

    table.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=10
    )

    load_events()


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    manage_events()

    root.mainloop()
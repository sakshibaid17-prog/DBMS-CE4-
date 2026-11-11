
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from datetime import date
import math

# ==========================================
# 1. DATABASE CONFIGURATION
# ==========================================

DB_PATH = Path(__file__).resolve().parent / "Deep_Sea_Research.db"


def connect_db():
    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA foreign_keys = ON")
    return con


def initialize_database():
    con = connect_db()
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS research_vessels (
            vessel_id INTEGER PRIMARY KEY AUTOINCREMENT,
            vessel_name TEXT NOT NULL UNIQUE COLLATE NOCASE,
            chief_scientist_email TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS deep_sea_dives (
            dive_id INTEGER PRIMARY KEY AUTOINCREMENT,
            vessel_id INTEGER NOT NULL,
            dive_site_name TEXT NOT NULL,
            dive_date TEXT NOT NULL,
            FOREIGN KEY (vessel_id)
                REFERENCES research_vessels(vessel_id)
                ON DELETE CASCADE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS sample_analyses (
            analysis_id INTEGER PRIMARY KEY AUTOINCREMENT,
            dive_id INTEGER NOT NULL,
            analysis_type TEXT NOT NULL,
            measured_value REAL NOT NULL CHECK(measured_value >= 0),
            FOREIGN KEY (dive_id)
                REFERENCES deep_sea_dives(dive_id)
                ON DELETE CASCADE
        )
    """)

    cur.execute("""
        SELECT
        (SELECT COUNT(*) FROM research_vessels),
        (SELECT COUNT(*) FROM deep_sea_dives),
        (SELECT COUNT(*) FROM sample_analyses)
    """)

    if cur.fetchone() == (0, 0, 0):

        vessels = [
            ("RV Ocean Explorer", "captain@oceanexplorer.org"),
            ("RV Deep Discoverer", "scientist@deepdiscoverer.org"),
            ("RV Nautilus", "research@nautilus.org"),
            ("RV Atlantis", "team@atlantis.org"),
            ("RV Challenger", "marine@challenger.org")
        ]

        cur.executemany("""
            INSERT INTO research_vessels
            (vessel_name, chief_scientist_email)
            VALUES (?, ?)
        """, vessels)

        dives = [
            (1, "Mariana Trench - Challenger Deep", "2026-10-20"),
            (1, "Pacific Ocean - Horizon Deep", "2026-10-22"),
            (2, "Puerto Rico Trench", "2026-10-23"),
            (3, "Indian Ocean - Java Trench", "2026-10-24"),
            (4, "South Sandwich Trench", "2026-10-25"),
            (5, "Mariana Trench - Sirena Deep", "2026-10-26")
        ]

        cur.executemany("""
            INSERT INTO deep_sea_dives
            (vessel_id, dive_site_name, dive_date)
            VALUES (?, ?, ?)
        """, dives)

        analyses = [
            (1, "Depth (m)", 10984),
            (1, "Temperature (C)", 1.8),
            (1, "Species Count", 25),
            (2, "Depth (m)", 10823),
            (2, "Temperature (C)", 2.1),
            (3, "Depth (m)", 8376),
            (3, "Species Count", 18),
            (4, "Temperature (C)", 3.2),
            (5, "Depth (m)", 7235),
            (6, "Species Count", 32)
        ]

        cur.executemany("""
            INSERT INTO sample_analyses
            (dive_id, analysis_type, measured_value)
            VALUES (?, ?, ?)
        """, analyses)

    con.commit()
    con.close()


# ==========================================
# 2. MAIN APPLICATION
# ==========================================

class DeepSeaResearchApp:

    def __init__(self, root):

        self.root = root
        self.root.title("Deep-Sea Research Dashboard")
        self.root.geometry("1400x900")
        self.root.minsize(1050, 700)
        self.root.configure(bg="#EAF4F4")

        self.setup_styles()
        self.create_header()
        self.create_insert_panel()
        self.create_delete_panel()
        self.create_tabs()
        self.refresh_all()

    # ======================================
    # 3. MODERN OCEAN THEME
    # ======================================

    def setup_styles(self):

        style = ttk.Style()
        style.theme_use("clam")

        self.colors = {
            "background": "#EAF4F4",
            "white": "#FFFFFF",
            "navy": "#073B4C",
            "teal": "#0F766E",
            "teal_dark": "#115E59",
            "text": "#16343B",
            "light_blue": "#D5E8E8",
            "alternate": "#E8F4F5",
            "border": "#B8D5D7"
        }

        style.configure(
            "TFrame",
            background=self.colors["background"]
        )

        style.configure(
            "TLabel",
            background=self.colors["white"],
            foreground=self.colors["text"],
            font=("Arial", 10)
        )

        style.configure(
            "TLabelframe",
            background=self.colors["white"],
            bordercolor=self.colors["border"],
            relief="solid"
        )

        style.configure(
            "TLabelframe.Label",
            background=self.colors["background"],
            foreground=self.colors["navy"],
            font=("Arial", 11, "bold")
        )

        style.configure(
            "TEntry",
            fieldbackground=self.colors["white"],
            foreground=self.colors["text"],
            padding=7
        )

        style.configure(
            "TCombobox",
            fieldbackground=self.colors["white"],
            background=self.colors["light_blue"],
            foreground=self.colors["text"],
            padding=7
        )

        style.configure(
            "TButton",
            background=self.colors["teal"],
            foreground=self.colors["white"],
            font=("Arial", 10, "bold"),
            padding=(12, 9),
            borderwidth=0
        )

        style.map(
            "TButton",
            background=[
                ("active", self.colors["teal_dark"]),
                ("pressed", self.colors["navy"])
            ],
            foreground=[("active", self.colors["white"])]
        )

        style.configure(
            "TNotebook",
            background=self.colors["background"],
            borderwidth=0
        )

        style.configure(
            "TNotebook.Tab",
            background=self.colors["light_blue"],
            foreground=self.colors["navy"],
            font=("Arial", 10, "bold"),
            padding=[16, 11]
        )

        style.map(
            "TNotebook.Tab",
            background=[
                ("selected", self.colors["teal"]),
                ("active", "#B9DCDC")
            ],
            foreground=[
                ("selected", self.colors["white"])
            ]
        )

        style.configure(
            "Treeview",
            background=self.colors["white"],
            fieldbackground=self.colors["white"],
            foreground=self.colors["text"],
            rowheight=32,
            font=("Arial", 10),
            borderwidth=0
        )

        style.configure(
            "Treeview.Heading",
            background=self.colors["navy"],
            foreground=self.colors["white"],
            font=("Arial", 10, "bold"),
            padding=10
        )

        style.map(
            "Treeview",
            background=[("selected", "#B7E4E5")],
            foreground=[("selected", self.colors["navy"])]
        )

    # ======================================
    # 4. HEADER
    # ======================================

    def create_header(self):

        header = tk.Frame(
            self.root,
            bg="#073B4C",
            height=105
        )

        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="DEEP-SEA RESEARCH DASHBOARD",
            font=("Arial", 25, "bold"),
            bg="#073B4C",
            fg="white"
        ).pack(pady=(20, 5))

        tk.Label(
            header,
            text="Research Vessels  |  Deep-Sea Dives  |  Sample Analyses",
            font=("Arial", 11),
            bg="#073B4C",
            fg="#CDEDEE"
        ).pack()

    # ======================================
    # 5. INSERT PANEL
    # ======================================

    def create_insert_panel(self):

        panel = ttk.LabelFrame(
            self.root,
            text="  ADD RESEARCH RECORDS  ",
            padding=15
        )

        panel.pack(fill="x", padx=15, pady=10)

        self.vessel_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.site_var = tk.StringVar()
        self.analysis_var = tk.StringVar()
        self.value_var = tk.StringVar()

        fields = [
            ("Vessel Name:", self.vessel_var),
            ("Chief Scientist Email:", self.email_var),
            ("Dive Site Name:", self.site_var),
            ("Analysis Type:", self.analysis_var),
            ("Measured Value:", self.value_var)
        ]

        positions = [
            (0, 0), (0, 2),
            (1, 0), (1, 2),
            (2, 0)
        ]

        for (label, variable), (row, col) in zip(fields, positions):

            ttk.Label(
                panel,
                text=label
            ).grid(
                row=row,
                column=col,
                padx=8,
                pady=10,
                sticky="w"
            )

            ttk.Entry(
                panel,
                textvariable=variable,
                width=29
            ).grid(
                row=row,
                column=col + 1,
                padx=8,
                pady=10
            )

        ttk.Button(
            panel,
            text="ADD RESEARCH RECORD",
            command=self.insert_record
        ).grid(
            row=2,
            column=2,
            columnspan=2,
            padx=10,
            pady=10,
            sticky="ew"
        )

    # ======================================
    # 6. INSERT RECORD LOGIC
    # ======================================

    def insert_record(self):

        vessel = self.vessel_var.get().strip()
        email = self.email_var.get().strip()
        site = self.site_var.get().strip()
        analysis = self.analysis_var.get().strip()
        value_text = self.value_var.get().strip()

        if not all([vessel, email, site, analysis, value_text]):
            messagebox.showwarning(
                "Missing Information",
                "Please fill in all fields."
            )
            return

        if "@" not in email or "." not in email.split("@")[-1]:
            messagebox.showwarning(
                "Invalid Email",
                "Please enter a valid email address."
            )
            return

        try:
            value = float(value_text)

            if not math.isfinite(value) or value < 0:
                raise ValueError

        except ValueError:
            messagebox.showwarning(
                "Invalid Value",
                "Enter a valid non-negative numeric value."
            )
            return

        con = connect_db()

        try:

            cur = con.cursor()

            cur.execute("""
                SELECT vessel_id
                FROM research_vessels
                WHERE vessel_name = ?
            """, (vessel,))

            result = cur.fetchone()

            if result:
                vessel_id = result[0]

            else:
                cur.execute("""
                    INSERT INTO research_vessels
                    (vessel_name, chief_scientist_email)
                    VALUES (?, ?)
                """, (vessel, email))

                vessel_id = cur.lastrowid

            dive_date = date.today().isoformat()

            cur.execute("""
                INSERT INTO deep_sea_dives
                (vessel_id, dive_site_name, dive_date)
                VALUES (?, ?, ?)
            """, (vessel_id, site, dive_date))

            dive_id = cur.lastrowid

            cur.execute("""
                INSERT INTO sample_analyses
                (dive_id, analysis_type, measured_value)
                VALUES (?, ?, ?)
            """, (dive_id, analysis, value))

            analysis_id = cur.lastrowid

            con.commit()

            self.vessel_var.set("")
            self.email_var.set("")
            self.site_var.set("")
            self.analysis_var.set("")
            self.value_var.set("")

            self.refresh_all()

            messagebox.showinfo(
                "Success",
                f"Research record added successfully!\n\n"
                f"Vessel ID: {vessel_id}\n"
                f"Dive ID: {dive_id}\n"
                f"Analysis ID: {analysis_id}"
            )

        except sqlite3.Error as error:
            con.rollback()
            messagebox.showerror("Database Error", str(error))

        finally:
            con.close()

    # ======================================
    # 7. DELETE PANEL
    # ======================================

    def create_delete_panel(self):

        panel = ttk.LabelFrame(
            self.root,
            text="  MANAGE RESEARCH RECORDS  ",
            padding=15
        )

        panel.pack(fill="x", padx=15, pady=5)

        self.vessel_delete_var = tk.StringVar()
        self.dive_delete_var = tk.StringVar()
        self.analysis_delete_var = tk.StringVar()

        # Vessel dropdown

        ttk.Label(
            panel,
            text="Research Vessel:"
        ).grid(row=0, column=0, padx=8, pady=9, sticky="w")

        self.vessel_dropdown = ttk.Combobox(
            panel,
            textvariable=self.vessel_delete_var,
            width=42,
            state="readonly"
        )

        self.vessel_dropdown.grid(
            row=0, column=1, padx=8, pady=9
        )

        ttk.Button(
            panel,
            text="DELETE VESSEL",
            command=self.delete_vessel
        ).grid(row=0, column=2, padx=12, pady=9)

        # Dive dropdown

        ttk.Label(
            panel,
            text="Deep-Sea Dive:"
        ).grid(row=1, column=0, padx=8, pady=9, sticky="w")

        self.dive_dropdown = ttk.Combobox(
            panel,
            textvariable=self.dive_delete_var,
            width=42,
            state="readonly"
        )

        self.dive_dropdown.grid(
            row=1, column=1, padx=8, pady=9
        )

        ttk.Button(
            panel,
            text="DELETE DIVE",
            command=self.delete_dive
        ).grid(row=1, column=2, padx=12, pady=9)

        # Analysis dropdown

        ttk.Label(
            panel,
            text="Sample Analysis:"
        ).grid(row=2, column=0, padx=8, pady=9, sticky="w")

        self.analysis_dropdown = ttk.Combobox(
            panel,
            textvariable=self.analysis_delete_var,
            width=42,
            state="readonly"
        )

        self.analysis_dropdown.grid(
            row=2, column=1, padx=8, pady=9
        )

        ttk.Button(
            panel,
            text="DELETE ANALYSIS",
            command=self.delete_analysis
        ).grid(row=2, column=2, padx=12, pady=9)

    # ======================================
    # 8. DELETE VESSEL
    # ======================================

    def delete_vessel(self):

        selected = self.vessel_delete_var.get()

        if not selected:
            messagebox.showwarning(
                "Selection Required",
                "Select a research vessel."
            )
            return

        vessel_id = int(selected.split(" | ")[0])

        confirm = messagebox.askyesno(
            "Confirm Deletion",
            "This will delete the vessel, all its dives "
            "and all related analyses.\n\nContinue?"
        )

        if not confirm:
            return

        con = connect_db()

        try:
            con.execute(
                "DELETE FROM research_vessels WHERE vessel_id = ?",
                (vessel_id,)
            )

            con.commit()
            self.refresh_all()

            messagebox.showinfo(
                "Success",
                "Vessel and associated records deleted."
            )

        except sqlite3.Error as error:
            con.rollback()
            messagebox.showerror("Database Error", str(error))

        finally:
            con.close()

    # ======================================
    # 9. DELETE DIVE
    # ======================================

    def delete_dive(self):

        selected = self.dive_delete_var.get()

        if not selected:
            messagebox.showwarning(
                "Selection Required",
                "Select a deep-sea dive."
            )
            return

        dive_id = int(selected.split(" | ")[0])

        confirm = messagebox.askyesno(
            "Confirm Deletion",
            "This will delete the dive and its sample analyses.\n"
            "The research vessel will remain.\n\nContinue?"
        )

        if not confirm:
            return

        con = connect_db()

        try:
            con.execute(
                "DELETE FROM deep_sea_dives WHERE dive_id = ?",
                (dive_id,)
            )

            con.commit()
            self.refresh_all()

            messagebox.showinfo(
                "Success",
                "Dive and its associated analyses deleted."
            )

        except sqlite3.Error as error:
            con.rollback()
            messagebox.showerror("Database Error", str(error))

        finally:
            con.close()

    # ======================================
    # 10. DELETE SAMPLE ANALYSIS
    # ======================================

    def delete_analysis(self):

        selected = self.analysis_delete_var.get()

        if not selected:
            messagebox.showwarning(
                "Selection Required",
                "Select a sample analysis."
            )
            return

        analysis_id = int(selected.split(" | ")[0])

        confirm = messagebox.askyesno(
            "Confirm Deletion",
            "Delete only this sample analysis?\n"
            "The dive and vessel will remain."
        )

        if not confirm:
            return

        con = connect_db()

        try:
            con.execute(
                "DELETE FROM sample_analyses WHERE analysis_id = ?",
                (analysis_id,)
            )

            con.commit()
            self.refresh_all()

            messagebox.showinfo(
                "Success",
                "Sample analysis deleted successfully."
            )

        except sqlite3.Error as error:
            con.rollback()
            messagebox.showerror("Database Error", str(error))

        finally:
            con.close()

    # ======================================
    # 11. DISPLAY TABS
    # ======================================

    def create_tabs(self):

        frame = ttk.Frame(self.root)

        frame.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=12
        )

        self.notebook = ttk.Notebook(frame)
        self.notebook.pack(fill="both", expand=True)

        self.tree_manifest = self.create_table_tab(
            "Research Manifest"
        )

        self.tree_vessels = self.create_table_tab(
            "Research Vessels"
        )

        self.tree_dives = self.create_table_tab(
            "Deep-Sea Dives"
        )

        self.tree_analyses = self.create_table_tab(
            "Sample Analyses"
        )

    def create_table_tab(self, title):

        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=title)

        container = ttk.Frame(frame)
        container.pack(fill="both", expand=True)

        tree = ttk.Treeview(
            container,
            show="headings"
        )

        vertical = ttk.Scrollbar(
            container,
            orient="vertical",
            command=tree.yview
        )

        horizontal = ttk.Scrollbar(
            container,
            orient="horizontal",
            command=tree.xview
        )

        tree.configure(
            yscrollcommand=vertical.set,
            xscrollcommand=horizontal.set
        )

        tree.grid(row=0, column=0, sticky="nsew")
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal.grid(row=1, column=0, sticky="ew")

        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        return tree

    # ======================================
    # 12. POPULATE TABLES
    # ======================================

    def populate_tree(self, tree, columns, rows):

        tree.delete(*tree.get_children())
        tree["columns"] = columns

        for column in columns:

            tree.heading(
                column,
                text=column.replace("_", " ").title()
            )

            tree.column(
                column,
                width=175,
                minwidth=110,
                anchor="center"
            )

        tree.tag_configure(
            "even",
            background="#FFFFFF"
        )

        tree.tag_configure(
            "odd",
            background="#E8F4F5"
        )

        for index, row in enumerate(rows):

            tag = "even" if index % 2 == 0 else "odd"

            tree.insert(
                "",
                "end",
                values=row,
                tags=(tag,)
            )

    # ======================================
    # 13. REFRESH TABLES AND DROPDOWNS
    # ======================================

    def refresh_all(self):

        con = connect_db()
        cur = con.cursor()

        try:

            # Research Manifest

            cur.execute("""
                SELECT
                    d.dive_id,
                    r.vessel_name,
                    d.dive_site_name,
                    d.dive_date,
                    s.analysis_type,
                    s.measured_value
                FROM research_vessels r
                JOIN deep_sea_dives d
                    ON r.vessel_id = d.vessel_id
                JOIN sample_analyses s
                    ON d.dive_id = s.dive_id
                ORDER BY d.dive_id, s.analysis_id
            """)

            self.populate_tree(
                self.tree_manifest,
                [
                    "dive_id",
                    "vessel_name",
                    "dive_site_name",
                    "dive_date",
                    "analysis_type",
                    "measured_value"
                ],
                cur.fetchall()
            )

            # Research Vessels

            cur.execute("""
                SELECT *
                FROM research_vessels
                ORDER BY vessel_id
            """)

            vessels = cur.fetchall()

            self.populate_tree(
                self.tree_vessels,
                [
                    "vessel_id",
                    "vessel_name",
                    "chief_scientist_email"
                ],
                vessels
            )

            # Deep-Sea Dives

            cur.execute("""
                SELECT *
                FROM deep_sea_dives
                ORDER BY dive_id
            """)

            dives = cur.fetchall()

            self.populate_tree(
                self.tree_dives,
                [
                    "dive_id",
                    "vessel_id",
                    "dive_site_name",
                    "dive_date"
                ],
                dives
            )

            # Sample Analyses

            cur.execute("""
                SELECT *
                FROM sample_analyses
                ORDER BY analysis_id
            """)

            analyses = cur.fetchall()

            self.populate_tree(
                self.tree_analyses,
                [
                    "analysis_id",
                    "dive_id",
                    "analysis_type",
                    "measured_value"
                ],
                analyses
            )

            # Vessel dropdown

            self.vessel_dropdown["values"] = [
                f"{row[0]} | {row[1]}"
                for row in vessels
            ]

            # Dive dropdown

            cur.execute("""
                SELECT
                    d.dive_id,
                    r.vessel_name,
                    d.dive_site_name,
                    d.dive_date
                FROM deep_sea_dives d
                JOIN research_vessels r
                    ON d.vessel_id = r.vessel_id
                ORDER BY d.dive_id
            """)

            dive_options = cur.fetchall()

            self.dive_dropdown["values"] = [
                f"{row[0]} | {row[1]} | {row[2]} | {row[3]}"
                for row in dive_options
            ]

            # Analysis dropdown

            cur.execute("""
                SELECT
                    s.analysis_id,
                    s.analysis_type,
                    d.dive_site_name
                FROM sample_analyses s
                JOIN deep_sea_dives d
                    ON s.dive_id = d.dive_id
                ORDER BY s.analysis_id
            """)

            analysis_options = cur.fetchall()

            self.analysis_dropdown["values"] = [
                f"{row[0]} | {row[1]} | {row[2]}"
                for row in analysis_options
            ]

            # Clear old dropdown selections

            self.vessel_delete_var.set("")
            self.dive_delete_var.set("")
            self.analysis_delete_var.set("")

        finally:
            con.close()


# ==========================================
# 14. START APPLICATION
# ==========================================

def main():

    try:

        initialize_database()

        root = tk.Tk()

        app = DeepSeaResearchApp(root)

        root.mainloop()

    except tk.TclError as error:
        print("Tkinter GUI could not start:", error)

    except sqlite3.Error as error:
        print("Database Error:", error)

    except Exception as error:
        print("Application Error:", error)


if __name__ == "__main__":
    main()
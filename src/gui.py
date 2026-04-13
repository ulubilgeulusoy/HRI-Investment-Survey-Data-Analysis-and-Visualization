from __future__ import annotations

import argparse
import csv
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from pipeline import DEFAULT_OUTPUT_CSV, combine_and_export

VIEW_COLUMNS = {
    "Overview": [
        "participant_id",
        "phase",
        "condition",
        "tlx_weighted_score",
        "trust_total_10_to_50",
        "investment_score_0_to_100",
        "respect_0_to_100",
        "self_confidence_0_to_100",
        "perception_autonomy_0_to_100",
    ],
    "Trust": [
        "participant_id",
        "phase",
        "condition",
        "trust_total_10_to_50",
        "trust_component_x_motion_pickup_2_to_10",
        "trust_component_y_safe_cooperation_4_to_20",
        "trust_component_z_reliability_4_to_20",
        "trust_mean_1_to_5",
        "trust_score_0_to_100",
        "trust_item_A",
        "trust_item_B",
        "trust_item_C",
        "trust_item_D",
        "trust_item_E",
        "trust_item_F",
        "trust_item_G",
        "trust_item_H",
        "trust_item_I",
        "trust_item_J",
        "trust_interpretation",
    ],
    "NASA TLX": [
        "participant_id",
        "phase",
        "condition",
        "tlx_weighted_score",
        "tlx_mental_demand_rating",
        "tlx_physical_demand_rating",
        "tlx_temporal_demand_rating",
        "tlx_performance_rating",
        "tlx_effort_rating",
        "tlx_frustration_rating",
        "tlx_mental_demand_weight",
        "tlx_physical_demand_weight",
        "tlx_temporal_demand_weight",
        "tlx_performance_weight",
        "tlx_effort_weight",
        "tlx_frustration_weight",
    ],
    "Investment": [
        "participant_id",
        "phase",
        "condition",
        "investment_score_0_to_100",
        "investment_item_1",
        "investment_item_2",
        "investment_item_3",
        "investment_item_4",
        "investment_item_5",
        "investment_item_6",
    ],
    "Self/Perception/Respect": [
        "participant_id",
        "phase",
        "condition",
        "respect_0_to_100",
        "self_confidence_0_to_100",
        "perception_autonomy_0_to_100",
    ],
    "Qualitative Responses": [
        "participant_id",
        "phase",
        "condition",
        "actions_performed",
        "why_actions_selected",
        "why_not_other_actions",
        "additional_comments",
    ],
}


class ScoreApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("HRI Score Viewer")
        self.geometry("1080x700")

        self.rows = []
        self.participant_var = tk.StringVar()
        self.phase_var = tk.StringVar()
        self.view_var = tk.StringVar(value="Overview")

        self._build_layout()
        self.last_combined_export: Path | None = None

    def _build_layout(self) -> None:
        top = ttk.Frame(self, padding=8)
        top.pack(fill=tk.X)

        ttk.Button(top, text="Load Break CSV", command=self._choose_break_csv).pack(side=tk.LEFT)
        ttk.Button(top, text="Load Baseline CSV (Optional)", command=self._choose_baseline_csv).pack(side=tk.LEFT, padx=8)
        ttk.Button(top, text="Compute Scores", command=self._compute).pack(side=tk.LEFT)
        ttk.Button(top, text="Load Computed Scores CSV", command=self._load_computed_scores).pack(side=tk.LEFT, padx=8)
        ttk.Button(top, text="Export Current View", command=self._export_view).pack(side=tk.LEFT, padx=8)

        self.break_path = tk.StringVar()
        self.baseline_path = tk.StringVar()

        path_frame = ttk.Frame(self, padding=(8, 0, 8, 8))
        path_frame.pack(fill=tk.X)
        ttk.Label(path_frame, textvariable=self.break_path).pack(anchor=tk.W)
        ttk.Label(path_frame, textvariable=self.baseline_path).pack(anchor=tk.W)

        filters = ttk.Frame(self, padding=8)
        filters.pack(fill=tk.X)

        ttk.Label(filters, text="Participant:").pack(side=tk.LEFT)
        self.participant_combo = ttk.Combobox(filters, textvariable=self.participant_var, state="readonly", width=20)
        self.participant_combo.bind("<<ComboboxSelected>>", lambda _e: self._refresh_table())
        self.participant_combo.pack(side=tk.LEFT, padx=(6, 20))

        ttk.Label(filters, text="Phase:").pack(side=tk.LEFT)
        self.phase_combo = ttk.Combobox(filters, textvariable=self.phase_var, state="readonly", width=20)
        self.phase_combo.bind("<<ComboboxSelected>>", lambda _e: self._refresh_table())
        self.phase_combo.pack(side=tk.LEFT, padx=6)

        ttk.Label(filters, text="Survey:").pack(side=tk.LEFT, padx=(20, 0))
        self.view_combo = ttk.Combobox(filters, textvariable=self.view_var, state="readonly", width=24)
        self.view_combo["values"] = list(VIEW_COLUMNS.keys())
        self.view_combo.bind("<<ComboboxSelected>>", lambda _e: self._refresh_table())
        self.view_combo.set("Overview")
        self.view_combo.pack(side=tk.LEFT, padx=6)

        table_frame = ttk.Frame(self)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.tree = ttk.Treeview(table_frame, columns=[], show="headings", height=16)
        self._configure_tree_columns(VIEW_COLUMNS["Overview"])

        yscroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        xscroll = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll.grid(row=1, column=0, sticky="ew")
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

    def _configure_tree_columns(self, columns: list[str]) -> None:
        self.tree["columns"] = columns
        for c in self.tree["columns"]:
            self.tree.heading(c, text="")
            self.tree.column(c, width=0, stretch=False)
        for c in columns:
            self.tree.heading(c, text=c)
            if c in {"actions_performed", "why_actions_selected", "why_not_other_actions", "additional_comments"}:
                width = 420
                anchor = tk.W
            elif c == "trust_interpretation":
                width = 320
                anchor = tk.CENTER
            else:
                width = 140
                anchor = tk.CENTER
            self.tree.column(c, width=width, anchor=anchor, stretch=True)

    def _choose_break_csv(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if path:
            self.break_path.set(f"Break CSV: {path}")

    def _choose_baseline_csv(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if path:
            self.baseline_path.set(f"Baseline CSV: {path}")

    def _compute(self) -> None:
        break_csv = self.break_path.get().replace("Break CSV: ", "", 1).strip()
        baseline_csv = self.baseline_path.get().replace("Baseline CSV: ", "", 1).strip()

        if not break_csv:
            messagebox.showerror("Missing Input", "Please choose a Break CSV.")
            return

        try:
            records = combine_and_export(
                break_csv_path=Path(break_csv),
                baseline_csv_path=Path(baseline_csv) if baseline_csv else None,
                output_csv_path=DEFAULT_OUTPUT_CSV,
            )
        except Exception as exc:
            messagebox.showerror("Scoring Error", str(exc))
            return

        self.rows = records
        self.last_combined_export = DEFAULT_OUTPUT_CSV
        self._refresh_filters_and_table()
        messagebox.showinfo("Computed", f"Combined results saved to:\n{DEFAULT_OUTPUT_CSV}")

    def _load_computed_scores(self) -> None:
        path = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv")],
            initialdir=str(DEFAULT_OUTPUT_CSV.parent),
            initialfile=DEFAULT_OUTPUT_CSV.name,
        )
        if not path:
            return

        try:
            with open(path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                self.rows = [dict(row) for row in reader]
        except Exception as exc:
            messagebox.showerror("Load Error", str(exc))
            return

        if not self.rows:
            messagebox.showinfo("No Data", "Selected CSV has no rows.")
            return

        self.last_combined_export = Path(path)
        self._refresh_filters_and_table()
        messagebox.showinfo("Loaded", f"Loaded computed scores from:\n{path}")

    def _refresh_filters_and_table(self) -> None:
        participants = sorted({str(r.get("participant_id", "")) for r in self.rows if str(r.get("participant_id", "")).strip()})
        phases = sorted({str(r.get("phase", "")) for r in self.rows if str(r.get("phase", "")).strip()})

        self.participant_combo["values"] = ["All", *participants]
        self.phase_combo["values"] = ["All", *phases]
        self.participant_combo.set("All")
        self.phase_combo.set("All")
        self._refresh_table()

    def _refresh_table(self) -> None:
        selected_view = self.view_var.get() or "Overview"
        columns = VIEW_COLUMNS[selected_view]
        self._configure_tree_columns(columns)

        for iid in self.tree.get_children():
            self.tree.delete(iid)

        participant = self.participant_var.get() or "All"
        phase = self.phase_var.get() or "All"

        filtered = self.rows
        if participant != "All":
            filtered = [r for r in filtered if str(r["participant_id"]) == participant]
        if phase != "All":
            filtered = [r for r in filtered if str(r["phase"]) == phase]

        for row in filtered:
            values = []
            for c in columns:
                value = row.get(c)
                if value is None:
                    values.append("")
                elif isinstance(value, (int, float)):
                    values.append(f"{float(value):.2f}")
                else:
                    values.append(str(value))
            self.tree.insert("", tk.END, values=values)

    def _export_view(self) -> None:
        if not self.rows:
            messagebox.showinfo("No Data", "Compute scores first.")
            return

        export_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            initialfile="scores_filtered.csv",
        )
        if not export_path:
            return

        participant = self.participant_var.get() or "All"
        phase = self.phase_var.get() or "All"

        filtered = self.rows
        if participant != "All":
            filtered = [r for r in filtered if str(r["participant_id"]) == participant]
        if phase != "All":
            filtered = [r for r in filtered if str(r["phase"]) == phase]

        keys = sorted({k for r in filtered for k in r.keys()})
        with open(export_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(filtered)

        messagebox.showinfo("Exported", f"Saved filtered scores to:\n{export_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="GUI for HRI score inspection.")
    parser.parse_args()
    app = ScoreApp()
    app.mainloop()


if __name__ == "__main__":
    main()

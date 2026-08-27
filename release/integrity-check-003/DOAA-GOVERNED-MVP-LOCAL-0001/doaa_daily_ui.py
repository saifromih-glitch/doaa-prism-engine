import json
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from doaa_run_report import build as build_run_report

OPERATIONS = {
    "إزالة فواصل الهاتف": ("remove_ascii_phone_separators", "phone"),
    "توحيد فراغات عمود محدد": ("normalize_ascii_spaces", "")
}


def build_request(input_path, output_path, operation, column, worksheet=""):
    if not input_path or not output_path or not operation or not column:
        raise ValueError("جميع الحقول الأساسية مطلوبة")
    if Path(input_path).resolve() == Path(output_path).resolve():
        raise ValueError("يجب أن يكون الإخراج ملفًا جديدًا")
    return {
        "input_path": str(Path(input_path).resolve()),
        "output_path": str(Path(output_path).resolve()),
        "allowed_root": str(Path(output_path).resolve().parent),
        "proposal": {"kind":"proposal","execution_authority":"none","operation":operation,"column":column,"arguments":{},"rationale":"Created by daily UI; requires governed review."},
        "human_review": {"status":"pending_user_review","execution_authority":"none"},
        "worksheet": worksheet or None,
        "ui_mode": "request_builder_only",
        "execution_started": False
    }


def launch():
    root = tk.Tk(); root.title("Doaa — الاستخدام اليومي الآمن"); root.geometry("700x430")
    frame = ttk.Frame(root, padding=16); frame.pack(fill="both", expand=True)
    ttk.Label(frame, text="Doaa — منشئ طلب حوْكمي", font=("Segoe UI", 16, "bold")).pack(anchor="w")
    ttk.Label(frame, text="هذه الواجهة تجهز الطلب فقط؛ لا تقرأ الملفات ولا تنفذ العملية تلقائيًا.").pack(anchor="w", pady=(4, 14))
    fields = {}
    def row(label, key, browse=False):
        box = ttk.Frame(frame); box.pack(fill="x", pady=5)
        ttk.Label(box, text=label, width=22).pack(side="left")
        var = tk.StringVar(); fields[key] = var
        ttk.Entry(box, textvariable=var).pack(side="left", fill="x", expand=True)
        if browse:
            ttk.Button(box, text="اختيار", command=lambda: var.set(filedialog.askopenfilename())).pack(side="left", padx=5)
    row("ملف الإدخال", "input_path", True); row("ملف الإخراج الجديد", "output_path", True)
    op = tk.StringVar(value=list(OPERATIONS)[0]); fields["op_label"] = op
    box = ttk.Frame(frame); box.pack(fill="x", pady=5); ttk.Label(box, text="العملية", width=22).pack(side="left"); ttk.Combobox(box, textvariable=op, values=list(OPERATIONS), state="readonly").pack(side="left", fill="x", expand=True)
    row("العمود الصريح", "column"); row("اسم الورقة (لـXLSX)", "worksheet")
    status = tk.StringVar(value="لم يُنشأ طلب بعد")
    def show_report():
        try:
            selected = filedialog.askopenfilename(title="اختيار نتيجة التشغيل", filetypes=[("JSON", "*.json")])
            if not selected: return
            result = json.loads(Path(selected).read_text(encoding="utf-8"))
            report = build_run_report(result)
            status.set(report.get("summary_ar", "لا يوجد ملخص"))
            messagebox.showinfo("تقرير التشغيل", report.get("summary_ar", "لا يوجد ملخص"))
        except Exception as exc:
            messagebox.showerror("تعذر عرض التقرير", str(exc))
    def prepare():
        try:
            operation, default_col = OPERATIONS[op.get()]; column = fields["column"].get().strip() or default_col
            request = build_request(fields["input_path"].get().strip(), fields["output_path"].get().strip(), operation, column, fields["worksheet"].get().strip())
            out = Path(fields["output_path"].get()).resolve().parent / "doaa-request.json"
            out.write_text(json.dumps(request, ensure_ascii=False, indent=2), encoding="utf-8")
            status.set(f"تم تجهيز الطلب فقط: {out}")
            messagebox.showinfo("تم تجهيز الطلب", "تم إنشاء request.json. لم يتم تنفيذ أي عملية.")
        except Exception as exc: messagebox.showerror("لم يُنشأ الطلب", str(exc))
    actions = ttk.Frame(frame); actions.pack(fill="x", pady=(16, 8))
    ttk.Button(actions, text="تجهيز طلب للمراجعة", command=prepare).pack(side="right")
    ttk.Button(actions, text="عرض تقرير التشغيل", command=show_report).pack(side="right", padx=8)
    ttk.Label(frame, textvariable=status, wraplength=650).pack(anchor="w")
    root.mainloop()

if __name__ == "__main__": launch()

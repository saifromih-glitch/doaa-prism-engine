import json
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from doaa_run_report import build as build_run_report
from doaa_preview import preview as preview_request
from doaa_xlsx_preview import preview_xlsx

OPERATIONS = {
    "إزالة فواصل الهاتف": ("remove_ascii_phone_separators", "phone"),
    "توحيد الفراغات": ("normalize_ascii_spaces", ""),
    "إزالة فراغات الحواف": ("trim_ascii_spaces", ""),
    "تحويل الجدولة إلى مسافة": ("tabs_to_ascii_space", ""),
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
        "proposal": {"kind": "proposal", "execution_authority": "none", "operation": operation, "column": column, "arguments": {}, "rationale": "Created by daily UI; requires governed review."},
        "human_review": {"status": "pending_user_review", "execution_authority": "none"},
        "worksheet": worksheet or None,
        "ui_mode": "request_builder_only",
        "execution_started": False,
    }


def preview_for_ui(input_path, operation, column, worksheet=""):
    request = {"input_path": input_path, "proposal": {"operation": operation, "column": column}, "worksheet": worksheet or "Sheet1"}
    result = preview_xlsx(request) if Path(input_path).suffix.lower() == ".xlsx" else preview_request(request)
    if result.get("status") != "preview_ready":
        report = build_run_report({"status": "preview_blocked", "reason": result.get("reason", "invalid_contract")})
        raise ValueError(report.get("reason_ar") or "تعذر إنشاء المعاينة")
    return result


def launch():
    root = tk.Tk(); root.title("Doaa - الطلب الحوْكمي المحلي"); root.geometry("760x520")
    frame = ttk.Frame(root, padding=18); frame.pack(fill="both", expand=True)
    ttk.Label(frame, text="Doaa - بناء طلب حوْكمي", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0, 12))
    fields = {}
    def row(label, key, browse=False):
        box = ttk.Frame(frame); box.pack(fill="x", pady=5)
        ttk.Label(box, text=label, width=24).pack(side="left")
        var = tk.StringVar(); fields[key] = var; ttk.Entry(box, textvariable=var).pack(side="left", fill="x", expand=True)
        if browse: ttk.Button(box, text="اختيار", command=lambda: var.set(filedialog.askopenfilename())).pack(side="left", padx=5)
    row("ملف الإدخال", "input_path", True); row("ملف الإخراج الجديد", "output_path", True)
    op = tk.StringVar(value=list(OPERATIONS)[0]); fields["op_label"] = op
    box = ttk.Frame(frame); box.pack(fill="x", pady=5); ttk.Label(box, text="العملية", width=24).pack(side="left"); ttk.Combobox(box, textvariable=op, values=list(OPERATIONS), state="readonly").pack(side="left", fill="x", expand=True)
    row("العمود الصريح", "column"); row("اسم الورقة (لـXLSX)", "worksheet")
    status = tk.StringVar(value="لم يُنشأ طلب بعد"); last_preview = {"hash": None}
    def preview_changes():
        try:
            operation, default_col = OPERATIONS[op.get()]; column = fields["column"].get().strip() or default_col
            result = preview_for_ui(fields["input_path"].get().strip(), operation, column, fields["worksheet"].get().strip() or "Sheet1")
            last_preview["hash"] = result.get("input_sha256")
            status.set("معاينة فقط: " + str(result.get("changed_cell_count", 0)) + " خلية متوقعة")
            lines = ["عدد الخلايا المتوقع تغييرها: " + str(result.get("changed_cell_count", 0))]
            for sample in result.get("samples", []): lines.append("الخانة " + str(sample.get("cell", sample.get("row_index", ""))) + ": " + str(sample.get("before", "")) + " ← " + str(sample.get("after", "")))
            messagebox.showinfo("معاينة قبل التنفيذ", "\n".join(lines) + "\n\nلم يُنشأ ملف ولم يبدأ التنفيذ.")
        except Exception as exc: messagebox.showerror("تعذر إنشاء المعاينة", str(exc))
    def prepare():
        try:
            operation, default_col = OPERATIONS[op.get()]; column = fields["column"].get().strip() or default_col
            if not last_preview["hash"]: raise ValueError("يجب إجراء المعاينة قبل تجهيز الطلب")
            request = build_request(fields["input_path"].get().strip(), fields["output_path"].get().strip(), operation, column, fields["worksheet"].get().strip())
            request["human_review"]["preview_input_sha256"] = last_preview["hash"]
            out = Path(fields["output_path"].get()).resolve().parent / "doaa-request.json"; out.write_text(json.dumps(request, ensure_ascii=False, indent=2), encoding="utf-8")
            status.set("تم تجهيز الطلب بعد المعاينة: " + str(out)); messagebox.showinfo("تم تجهيز الطلب", "تم إنشاء request.json. لم يتم تنفيذ أي عملية.")
        except Exception as exc: messagebox.showerror("لم يُنشأ الطلب", str(exc))
    def show_report():
        try:
            selected = filedialog.askopenfilename(title="اختيار نتيجة التشغيل", filetypes=[("JSON", "*.json")])
            if not selected: return
            result = json.loads(Path(selected).read_text(encoding="utf-8")); report = build_run_report(result); status.set(report.get("summary_ar", "لا يوجد ملخص")); messagebox.showinfo("تقرير التشغيل", report.get("summary_ar", "لا يوجد ملخص") + ("\n" + report.get("reason_ar", "") if report.get("reason_ar") else ""))
        except Exception as exc: messagebox.showerror("تعذر عرض التقرير", str(exc))
    actions = ttk.Frame(frame); actions.pack(fill="x", pady=(16, 8)); ttk.Button(actions, text="تجهيز طلب للمراجعة", command=prepare).pack(side="right"); ttk.Button(actions, text="معاينة التغييرات", command=preview_changes).pack(side="right", padx=8); ttk.Button(actions, text="عرض تقرير التشغيل", command=show_report).pack(side="right", padx=8)
    ttk.Label(frame, textvariable=status, wraplength=700).pack(anchor="w"); root.mainloop()


if __name__ == "__main__": launch()

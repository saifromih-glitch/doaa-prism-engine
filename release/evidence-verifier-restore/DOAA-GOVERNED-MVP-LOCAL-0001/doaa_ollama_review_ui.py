import tkinter as tk
from tkinter import messagebox

def review_decision(action):
    if action == "accept_for_gate":
        return {"status":"accepted_for_gate","execution_authority":"none","automatic_execution":False,"execution_started":False}
    return {"status":"rejected_by_human","execution_authority":"none","automatic_execution":False,"execution_started":False}

def show_review(parent, proposal):
    required = {"message_id", "model_id", "raw_response", "execution_authority", "automatic_execution"}
    if not isinstance(proposal, dict) or not required.issubset(proposal):
        return review_decision("reject")
    win = tk.Toplevel(parent)
    win.title("مراجعة اقتراح Ollama")
    win.transient(parent)
    tk.Label(win, text="النموذج: " + str(proposal["model_id"])).pack(anchor="w", padx=12, pady=6)
    text = tk.Text(win, width=90, height=20, wrap="word")
    text.insert("1.0", str(proposal["raw_response"]))
    text.configure(state="disabled")
    text.pack(padx=12, pady=6)
    result = [review_decision("reject")]
    def accept():
        result[0] = review_decision("accept_for_gate")
        win.destroy()
    def reject():
        result[0] = review_decision("reject")
        win.destroy()
    buttons = tk.Frame(win); buttons.pack(pady=8)
    tk.Button(buttons, text="قبول للبوابة فقط", command=accept).pack(side="right", padx=5)
    tk.Button(buttons, text="رفض", command=reject).pack(side="right", padx=5)
    win.grab_set(); parent.wait_window(win)
    return result[0]


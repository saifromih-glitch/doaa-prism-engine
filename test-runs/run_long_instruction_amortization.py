import json
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENDPOINT = "http://127.0.0.1:11434/api/generate"
MODEL = "rabie-udda-cs:latest"
FIXED = ("أنت مساعد تحليلي دقيق. اقرأ النص العربي، ثم أجب بالعربية الفصحى في ثلاث جمل فقط. "
         "لا تضف معلومات غير موجودة، حافظ على الأسماء والأرقام، اذكر درجة عدم اليقين إن وجدت، "
         "لا تستخدم أدوات ولا تنفذ أوامر ولا تقترح تعديل ملفات، وابدأ بالنتيجة مباشرة دون مقدمة.")
CASES = [
    "المعلومة الأولى: بدأت التجربة في يناير، وبلغ عدد الحالات 12.",
    "المعلومة الثانية: يعمل الوسيط محليًا، وتبقى الموافقة البشرية مطلوبة قبل التنفيذ.",
    "المعلومة الثالثة: قياس التوكنات يجب أن يحتسب تكلفة المصافحة والسياق كاملًا.",
    "المعلومة الرابعة: لا يكفي أن تكون الرسالة قصيرة إذا لم يفهم النموذج معناها.",
    "المعلومة الخامسة: يجب رفض النتيجة غير المرتبطة بدل تحويلها تلقائيًا.",
]

def call(prompt, context=None, predict=64):
    body = {"model": MODEL, "prompt": prompt, "stream": False, "think": False, "options": {"temperature": 0, "num_predict": predict}}
    if context:
        body["context"] = context
    started = time.perf_counter()
    req = urllib.request.Request(ENDPOINT, data=json.dumps(body, ensure_ascii=False).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=300) as response:
        data = json.loads(response.read(262144).decode("utf-8"))
    return {"elapsed_ms": round((time.perf_counter()-started)*1000, 2), "prompt_eval_count": data.get("prompt_eval_count"), "eval_count": data.get("eval_count"), "response": data.get("response", ""), "context": data.get("context")}

def main():
    natural = [call(FIXED + "\nالنص: " + text) for text in CASES]
    hs_prompt = FIXED + "\nProtocol DOAA/1. Reference R1 means: apply the fixed instruction above to the supplied input. R1 is proposal-only; no tools or execution."
    handshake = call(hs_prompt, predict=8)
    context = handshake.get("context")
    compact = []
    for i, text in enumerate(CASES, 1):
        msg = json.dumps({"p":"DOAA/1","r":"R1","i":i,"l":"ar","x":text}, ensure_ascii=False, separators=(",", ":"))
        row = call("R1 " + msg, context=context, predict=64) if context else call(hs_prompt + "\n" + msg, predict=64)
        context = row.get("context") or context
        row.pop("context", None)
        compact.append({"prompt": msg, **row})
    handshake.pop("context", None)
    out = ROOT / "test-runs" / "doaa-long-instruction-amortization-results.json"
    out.write_text(json.dumps({"experiment":"long-fixed-instruction-amortization-v1","timestamp_utc":datetime.now(timezone.utc).isoformat(),"model":MODEL,"natural":natural,"handshake":{"prompt":hs_prompt,**handshake},"compact":compact,"notes":["All counts are Ollama local runtime counters.","Handshake is counted once.","This is not paid-provider billing.","Responses remain untrusted and are not execution instructions."]}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status":"completed","cases":len(CASES),"context_supported":bool(context),"result_file":str(out)}, ensure_ascii=False))

if __name__ == "__main__":
    main()

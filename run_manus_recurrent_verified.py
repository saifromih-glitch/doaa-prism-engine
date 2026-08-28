from __future__ import annotations
import json, os, time
from pathlib import Path
from openai import OpenAI
from doaa_warm_checkpoint_session import WarmCheckpointSession
from doaa_answer_shape import build_request, validate_response, parse_json

DATASET = Path("benchmark-data/arabicaqa/test-cases.json")
OUTPUT = Path("benchmark-data/arabicaqa/manus-recurrent-verified-run.json")
MODEL = os.getenv("DOAA_MODEL", "gpt-5-mini")
SAMPLE_SIZE = int(os.getenv("DOAA_SAMPLE_SIZE", "20"))
if os.getenv("DOAA_RUN_LIVE") != "1": raise SystemExit("live_run_requires_DOAA_RUN_LIVE_1")

data = json.loads(DATASET.read_text(encoding="utf-8"))
selection = json.loads(Path("benchmark-data/arabicaqa/recurrent-context-selection.json").read_text(encoding="utf-8"))
ids = {item["case_id"] for item in selection["top_groups"][0]["cases"]}
selected = [case for case in data["cases"] if case["case_id"] in ids][:SAMPLE_SIZE]
payloads = [json.loads(case["request"]) for case in selected]
client = OpenAI()

def call(messages, schema):
    started = time.perf_counter()
    response = client.chat.completions.create(model=MODEL, messages=messages, max_completion_tokens=512, response_format=schema)
    if not response.choices or response.choices[0].message.content is None:
        detail = response.model_dump() if hasattr(response, "model_dump") else {"response": str(response)}
        raise RuntimeError("structured_response_empty:" + json.dumps(detail, ensure_ascii=False)[:1200])
    usage = response.usage
    return {"content": response.choices[0].message.content, "prompt_tokens": usage.prompt_tokens, "completion_tokens": usage.completion_tokens, "total_tokens": usage.total_tokens, "latency_ms": round((time.perf_counter()-started)*1000, 3)}

def overlap(answer, reference):
    ref = set(reference.split()); return round(len(set(answer.split()) & ref) / len(ref), 6) if ref else 0.0

item_schema = {"type":"object","properties":{"question_id":{"type":"string"},"answer":{"type":"string"},"evidence_quote":{"type":"string"},"uncertainty":{"type":"string","enum":["none","source_incomplete","not_found"]},"answer_units":{"type":"string"}},"required":["question_id","answer","evidence_quote","uncertainty","answer_units"],"additionalProperties":False}
schema = {"type":"json_schema","json_schema":{"name":"doaa_verified_answers","strict":True,"schema":{"type":"object","properties":{"answers":{"type":"array","items":item_schema}},"required":["answers"],"additionalProperties":False}}}

def request_messages(context, questions):
    body = {"ctx": context, "questions": [{"question_id": case["case_id"], "question": json.loads(case["request"])["question"], "question_type": build_request(case["case_id"], json.loads(case["request"])["question"], context)["question_type"]} for case in questions]}
    system = "doaa.alg.v1|أخرج إجابة لكل question_id بالترتيب. أجب عن كل سؤال من ctx فقط. evidence_quote اقتباس حرفي من ctx. لا تخلط بين الأسئلة، لا تخمن، ولا تضف شرحاً." 
    return [{"role":"system","content":system},{"role":"user","content":json.dumps(body, ensure_ascii=False, separators=(",",":"))}]

context = payloads[0]["context"]
baseline_rows=[]
base_system="أجب عن السؤال العربي اعتماداً على السياق فقط. أخرج إجابة عربية موجزة دون شرح."
for case,payload in zip(selected,payloads):
    natural=f"السؤال: {payload['question']}\n\nالسياق:\n{payload['context']}"
    result=client.chat.completions.create(model=MODEL,messages=[{"role":"system","content":base_system},{"role":"user","content":natural}],max_completion_tokens=256)
    usage=result.usage; text=result.choices[0].message.content or ""
    baseline_rows.append({"case_id":case["case_id"],"answer":text,"reference_answer":case["reference_answer"],"reference_overlap":overlap(text,case["reference_answer"]),"prompt_tokens":usage.prompt_tokens,"completion_tokens":usage.completion_tokens,"total_tokens":usage.total_tokens})

session=WarmCheckpointSession("manus-arabicaqa-verified")
registered=session.register_source(context)
questions=selected
a=session.prepare_query(payloads[0]["question"])
first=call(request_messages(context,questions),schema)
first_payload=parse_json(first["content"])
by_id={item.get("question_id"):item for item in first_payload.get("answers",[]) if isinstance(item,dict)}
rows=[]; failed=[]
for case in selected:
    req=build_request(case["case_id"],json.loads(case["request"])["question"],context)
    verdict=validate_response(by_id.get(case["case_id"],{}),req)
    row={"case_id":case["case_id"],"reference_answer":case["reference_answer"],"answer":by_id.get(case["case_id"],{}).get("answer", ""),"reference_overlap":overlap(by_id.get(case["case_id"],{}).get("answer", ""),case["reference_answer"]),"verification":verdict}
    rows.append(row)
    if verdict["status"] != "supported": failed.append(case)

retry=None
if failed:
    retry=call(request_messages(context,failed),schema)
    retry_payload=parse_json(retry["content"])
    for case in failed:
        item=next((x for x in retry_payload.get("answers",[]) if x.get("question_id")==case["case_id"]),{})
        req=build_request(case["case_id"],json.loads(case["request"])["question"],context)
        verdict=validate_response(item,req)
        row=next(x for x in rows if x["case_id"]==case["case_id"])
        row.update({"retry_answer":item.get("answer", ""),"retry_verification":verdict,"retry_reference_overlap":overlap(item.get("answer", ""),case["reference_answer"])})

base_prompt=sum(x["prompt_tokens"] for x in baseline_rows); base_total=sum(x["total_tokens"] for x in baseline_rows)
doaa_prompt=first["prompt_tokens"]+(retry["prompt_tokens"] if retry else 0); doaa_total=first["total_tokens"]+(retry["total_tokens"] if retry else 0)
accepted=sum(1 for x in rows if x.get("retry_verification",x["verification"])["status"]=="supported")
report={"status":"live_verified_recurrent_complete","model":MODEL,"sample_count":len(selected),"baseline":{"calls":len(baseline_rows),"prompt_tokens":base_prompt,"total_tokens":base_total,"mean_reference_overlap":round(sum(x["reference_overlap"] for x in baseline_rows)/len(baseline_rows),6)},"doaa":{"calls":1+(1 if retry else 0),"prompt_tokens":doaa_prompt,"total_tokens":doaa_total,"first_pass_supported":len(selected)-len(failed),"final_supported":accepted,"retry_count":len(failed),"mean_reference_overlap_first":round(sum(x["reference_overlap"] for x in rows)/len(rows),6)},"prompt_token_saving_ratio":round((base_prompt-doaa_prompt)/base_prompt,6),"total_token_saving_ratio":round((base_total-doaa_total)/base_total,6),"safety_evaluated":False,"human_review_completed":False,"checkpoint_source_sent_once_per_request":True,"execution_authority":"none","automatic_execution":False,"rows":rows}
OUTPUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({k:report[k] for k in ("status","sample_count","baseline","doaa","prompt_token_saving_ratio","total_token_saving_ratio","safety_evaluated")},ensure_ascii=False))

import json
from pathlib import Path
p=Path('benchmark-data/arabicaqa/manus-recurrent-verified-run.json')
r=json.loads(p.read_text(encoding='utf-8'))
final=[]
for row in r['rows']:
    if 'retry_verification' in row:
        final.append(row['retry_reference_overlap'])
    else:
        final.append(row['reference_overlap'])
accepted=sum(1 for row in r['rows'] if row.get('retry_verification',row['verification'])['status']=='supported')
summary={'sample_count':r['sample_count'],'first_pass_supported':r['doaa']['first_pass_supported'],'final_supported':accepted,'retry_count':r['doaa']['retry_count'],'final_mean_reference_overlap':round(sum(final)/len(final),6),'baseline_mean_reference_overlap':r['baseline']['mean_reference_overlap'],'prompt_token_saving_ratio':r['prompt_token_saving_ratio'],'total_token_saving_ratio':r['total_token_saving_ratio'],'safety_evaluated':r['safety_evaluated'],'human_review_completed':r['human_review_completed']}
Path('benchmark-data/arabicaqa/manus-recurrent-verified-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False))

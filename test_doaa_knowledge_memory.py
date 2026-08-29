import json
from pathlib import Path
from doaa_knowledge_memory import KnowledgeMemory, normalize_arabic


def load_memory():
    p=Path(__file__).parent/'library-pilot/software-security-seo.json'
    return KnowledgeMemory(json.loads(p.read_text(encoding='utf-8'))['entries'])


def test_arabic_normalization():
    assert normalize_arabic('أمانٌ ـ البرمجيات') == normalize_arabic('امان البرمجيات')


def test_top_k_and_source_warning():
    result=load_memory().retrieve('تحسين صفحة عربية لمحركات البحث', domain='digital_marketing', top_k=2)
    assert len(result['selected_ids']) <= 2
    assert result['execution_authority'] == 'none'
    assert result['prompt_payload']


def test_security_retrieval_is_bounded():
    result=load_memory().retrieve('ممارسات تطوير برمجيات آمنة', domain='software_security', top_k=1)
    assert len(result['selected_ids']) <= 1
    if result['selected_claims']:
        assert result['selected_claims'][0]['source_url'].startswith('https://')


if __name__ == '__main__':
    test_arabic_normalization(); test_top_k_and_source_warning(); test_security_retrieval_is_bounded(); print('ok')

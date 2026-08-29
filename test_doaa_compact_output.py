from doaa_compact_output import parse_compact


def test_valid():
    r=parse_compact('q1|إجابة|اقتباس|none|\nq2|نعم|نص المصدر|source_incomplete|وحدة',['q1','q2'])
    assert r['status']=='accepted' and len(r['records'])==2


def test_rejects_extra_fields_and_missing():
    r=parse_compact('q1|إجابة|اقتباس|none|وحدة|زائد',['q1','q2'])
    assert r['status']=='partial_or_rejected'
    assert r['missing_question_ids']==['q1','q2']


def test_rejects_duplicate_and_unknown():
    r=parse_compact('q1|إجابة|اقتباس|none|وحدة\nq1|ثانية|اقتباس|none|وحدة\nq9|x|y|none|',['q1'])
    assert len(r['rejected'])==2


if __name__=='__main__':
    test_valid(); test_rejects_extra_fields_and_missing(); test_rejects_duplicate_and_unknown(); print('ok')

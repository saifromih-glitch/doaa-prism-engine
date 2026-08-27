from zipfile import ZipFile
from pathlib import Path
p=Path(__file__).parent / "test-runs-excel" / "output-arabic-phone.xlsx"
with ZipFile(p) as z:
    print(z.read("xl/worksheets/sheet1.xml").decode("utf-8"))

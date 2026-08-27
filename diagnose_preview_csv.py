import csv
from pathlib import Path
p=Path(r"C:\Users\saifr\OneDrive\Desktop\Doaa-Local\preview-trial-002\input-bom.csv")
with p.open("r",encoding="utf-8-sig",newline="") as h:
    r=csv.DictReader(h); print(r.fieldnames); print(list(r))

import csv
from pathlib import Path


file_path = Path("backend/data/extracted/declarations/declaration_sample.csv")

with file_path.open("r", encoding="utf-8-sig", newline="") as file:
    reader = csv.DictReader(file)
    print(reader.fieldnames)
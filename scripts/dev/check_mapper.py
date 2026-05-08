from pathlib import Path
import csv

from backend.external.csv_mapper import map_row_to_document_data

file_path = Path("backend/data/samples/declaration_sample.csv")

with file_path.open("r", encoding="utf-8-sig", newline="") as file:
    reader = csv.DictReader(file)
    row = next(reader)

data = map_row_to_document_data(row, "declaration")

print("document_number:", data["document_number"])
print("status:", data["status"])
print("registered_at:", data["registered_at"])
print("valid_until:", data["valid_until"])
print("applicant_name:", data["applicant_name"])
print("manufacturer_name:", data["manufacturer_name"])
print("product_full_name:", data["product_full_name"])
print()
print("SEARCH TEXT:")
print(data["search_text"])

print(data.keys())
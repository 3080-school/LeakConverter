import json
import os
import sys
from pdf2image import convert_from_path

def extract_table_pages_from_json(pdf_path, base_name):
    json_path = f"practices/{base_name}.json"
    output_dir = f"table_snapshots/{base_name}"
    os.makedirs(output_dir, exist_ok=True)

    print(f"📦 Загружаем: {json_path}")
    if not os.path.exists(json_path):
        print(f"❌ Нет файла: {json_path}")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        questions = json.load(f)

    pages_with_tables = set()
    for q in questions:
        if q.get("has-table") is True and "page" in q:
            pages_with_tables.add(q["page"])

    pages_with_tables = sorted(pages_with_tables)
    if not pages_with_tables:
        print("⚠️ В JSON нет ни одной страницы с таблицей.")
        return

    from pdf2image import convert_from_path
    pdf_pages = convert_from_path(pdf_path, dpi=300)

    print(f"📄 Извлекаем страницы с таблицами: {pages_with_tables}")
    for page_num in pages_with_tables:
        if 1 <= page_num <= len(pdf_pages):
            img = pdf_pages[page_num - 1]
            out_path = os.path.join(output_dir, f"page_{page_num}_table.png")
            img.save(out_path)
            print(f"✅ Сохранено: {out_path}")
        else:
            print(f"❌ Страница {page_num} вне диапазона (в PDF {len(pdf_pages)} стр.)")

    print("🎉 Готово. Табличные страницы сохранены.")

if __name__ == "__main__":
    # Запуск: python3 extract_table_pages_from_json.py December_v1_2024.pdf December_v1_2024
    if len(sys.argv) < 3:
        print("Использование: python3 extract_table_pages_from_json.py <pdf_path> <base_name>")
        print("Пример: python3 extract_table_pages_from_json.py sources/December_v1_2024.pdf December_v1_2024")
        sys.exit(1)

    extract_table_pages_from_json(sys.argv[1], sys.argv[2])

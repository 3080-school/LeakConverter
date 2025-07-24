import os
import sys
from gpt_vision_to_txt import gpt_vision_to_txt
from merge_txt_to_json import merge_txt_to_json
from extract_table_pages_from_json import extract_table_pages_from_json
from crop_tables_from_images import crop_tables_from_images


def main(pdf_path):
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    print(f"BASE NAME: {base_name}")

    # 1. GPT Vision по страницам PDF
    gpt_vision_to_txt(pdf_path, base_name)

    # 2. Мердж всех TXT в JSON
    merge_txt_to_json(base_name)

    # 3. Снапшоты страниц с таблицами (по JSON)
    extract_table_pages_from_json(pdf_path, base_name)

    # 4. Кроп таблиц
    crop_tables_from_images(base_name)

    print(f"\n✅ Practice создан: practices/{base_name}.json\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Используй: python3 process_sat_pdf.py sources/December_v1_2024.pdf")
        sys.exit(1)
    main(sys.argv[1])

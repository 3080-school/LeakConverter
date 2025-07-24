import os
import json
import re
import sys

def merge_txt_to_json(base_name):
    folder_path = os.path.join('raw_txt', base_name)
    out_path = os.path.join('practices', f'{base_name}.json')
    merged_data = []

    # 🔢 Сортировка файлов по номеру страницы
    def extract_page_number(filename):
        match = re.search(r'page_(\d+)\.txt', filename)
        return int(match.group(1)) if match else float('inf')

    if not os.path.exists(folder_path):
        print(f"❌ Нет такой папки: {folder_path}")
        return

    filenames = sorted(
        [f for f in os.listdir(folder_path) if f.endswith('.txt')],
        key=extract_page_number
    )

    for idx, filename in enumerate(filenames, 1):
        with open(os.path.join(folder_path, filename), 'r', encoding='utf-8') as file:
            raw_text = file.read().strip()
            # Чистим обёртку ```json или ```
            clean_text = re.sub(r"^```json\s*|\s*```$", "", raw_text, flags=re.MULTILINE)

            try:
                data = json.loads(clean_text)
                if isinstance(data, list):
                    for q in data:
                        q["page"] = idx  # <= добавляем НОМЕР СТРАНИЦЫ
                    merged_data.extend(data)
                else:
                    print(f"⚠️ Внимание: {filename} не содержит список JSON.")
            except json.JSONDecodeError as e:
                print(f"❌ Ошибка в {filename}: {e}")

    # 🆔 Назначаем уникальные ID по порядку
    for idx, item in enumerate(merged_data, 1):
        item["id"] = f"q{idx}"

    os.makedirs("practices", exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as outfile:
        json.dump(merged_data, outfile, ensure_ascii=False, indent=2)

    print(f"✅ Готово! Объединено и сохранено в {out_path}")

if __name__ == "__main__":
    # Пример запуска: python3 merge_txt_to_json.py December_v1_2024
    if len(sys.argv) < 2:
        print("❌ Укажи base_name (например, December_v1_2024)")
        sys.exit(1)
    merge_txt_to_json(sys.argv[1])

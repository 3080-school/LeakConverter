import cv2
import os
import sys

def crop_largest_object(img_path, output_path, min_area=10_000):
    image = cv2.imread(img_path)
    if image is None:
        print(f"❌ Не удалось открыть изображение: {img_path}")
        return

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 180, 255, cv2.THRESH_BINARY_INV)

    # Находим контуры
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Фильтруем маленькие объекты
    contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_area]

    if not contours:
        print(f"⚠️ Ничего не найдено: {img_path}")
        return

    # Выбираем самый большой контур
    largest = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest)
    cropped = image[y:y+h, x:x+w]
    cv2.imwrite(output_path, cropped)
    print(f"✅ Сохранено: {output_path}")

def crop_tables_from_images(base_name):
    input_dir = os.path.join("table_snapshots", base_name)
    output_dir = os.path.join("tables_cropped", base_name)
    os.makedirs(output_dir, exist_ok=True)

    found = False
    for fname in os.listdir(input_dir):
        if not fname.endswith(".png"):
            continue

        found = True
        print(f"🧠 Обрабатываем: {fname}")
        in_path = os.path.join(input_dir, fname)
        out_path = os.path.join(output_dir, f"cropped_{fname}")
        crop_largest_object(in_path, out_path)

    if not found:
        print("⚠️ Нет изображений для обрезки.")
    else:
        print("🎉 Готово: графики и таблицы обрезаны.")

if __name__ == "__main__":
    # Запуск: python3 crop_tables_from_images.py December_v1_2024
    if len(sys.argv) < 2:
        print("Использование: python3 crop_tables_from_images.py <base_name>")
        print("Пример: python3 crop_tables_from_images.py December_v1_2024")
        sys.exit(1)
    crop_tables_from_images(sys.argv[1])

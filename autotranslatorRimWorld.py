import os
import time
import re
from deep_translator import GoogleTranslator

# Пути к файлам на Рабочем столе
# Определяем папку, в которой прямо сейчас находится сам скрипт (или .exe файл)
current_dir = os.path.dirname(os.path.abspath(__file__))

# Файлы будут искаться и создаваться прямо в этой же папке
input_file = os.path.join(current_dir, "translations.csv")
output_file = os.path.join(current_dir, "translations_ready.csv")


def clean_and_translate(text, translator):
    """Вытаскивает из каши символов нормальные английские слова и переводит их."""
    if not text or not text.strip():
        return ""
    
    # Находим полноценные английские слова от 3 букв
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text)
    if not words:
        return ""
        
    cleaned_text = " ".join(words)
    
    # Игнорируем технические префиксы мода
    if cleaned_text.startswith("VFEC") or (cleaned_text.isupper() and len(cleaned_text) < 5):
        return ""

    try:
        return translator.translate(cleaned_text)
    except Exception:
        return ""

def translate_csv_direct():
    if not os.path.exists(input_file):
        print(f"Ошибка: Файл '{input_file}' не найден в папке со скриптом!")
        input("\nНажмите Enter для выхода...")
        return

    print("Анализ текстовой структуры файла...")
    try:
        with open(input_file, mode='r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Ошибка чтения файла: {e}")
        input("\nНажмите Enter для выхода...")
        return
        
    total_rows = len(lines) - 1
    print(f"Найдено строк: {total_rows}")
    print("Запуск текстового парсера и очистки...\n")
    
    translator = GoogleTranslator(source='en', target='ru')
    
    try:
        with open(output_file, mode='w', encoding='utf-8') as outfile:
            # Записываем шапку таблицы
            outfile.write(lines[0])
            
            row_count = 1
            for line in lines[1:]:
                if not line.strip():
                    outfile.write(line)
                    continue
                
                # Делим строку по запятым
                parts = line.split(',')
                
                # Проверяем, что в строке есть нужные нам колонки
                if len(parts) >= 5:
                    # 4-я колонка — это оригинальный текст (индекс 3)
                    original_text = parts[3]
                    
                    translated = clean_and_translate(original_text, translator)
                    
                    if translated:
                        # Вставляем русский перевод в 5-ю колонку (индекс 4)
                        parts[4] = translated
                        print(f"Строка {row_count}/{total_rows} | Переведено => '{translated}'")
                    else:
                        parts[4] = ""
                        if row_count % 100 == 0:
                            print(f"Строка {row_count}/{total_rows} | [Пропущен технический мусор]")
                
                # Собираем строку обратно
                outfile.write(",".join(parts))
                row_count += 1
                time.sleep(0.04)
                
        print(f"\n[+] Всё готово! Очищенный файл сохранен в: {output_file}")
    except Exception as e:
        print(f"\n[-] Критическая ошибка во время работы: {e}")
    
    input("\nПроцесс завершен. Нажмите Enter, чтобы закрыть окно...")

if __name__ == "__main__":
    translate_csv_direct()

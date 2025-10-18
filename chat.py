import os
import json
import pandas as pd
import PyPDF2
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_community.chat_models.gigachat import GigaChat

load_dotenv('.env')

class FileDataProcessor:
    def __init__(self):
        self.llm = GigaChat(
            credentials=os.getenv('GIGACHAT_API_KEY'),
            model="GigaChat",
            temperature=0.7,
            verify_ssl_certs=False
        )
    
    def process_file(self, file_path, filter_criteria):
        """Обрабатывает файл и фильтрует данные по критериям"""
        
        # Читаем данные из файла в зависимости от формата
        file_data = self._read_file(file_path)
        
        if not file_data:
            return {"error": f"Не удалось прочитать файл: {file_path}"}
        
        prompt = f"""
        Проанализируй следующие данные из файла и отфильтруй их согласно критериям.
        
        ДАННЫЕ ИЗ ФАЙЛА:
        {file_data}
        
        КРИТЕРИИ ФИЛЬТРАЦИИ:
        {filter_criteria}
        
        Требования:
        1. Проанализируй структуру данных
        2. Примени критерии фильтрации
        3. Верни результат В ТОЛЬКО в формате JSON
        4. Сохрани структуру исходных данных
        5. Не добавляй пояснения или другой текст
        
        Формат ответа должен быть чистым JSON.
        """
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            return self._extract_json(response.content)
            
        except Exception as e:
            return {"error": f"Ошибка обработки: {str(e)}"}
    
    def _read_file(self, file_path):
        """Читает данные из файла в зависимости от формата"""
        if not os.path.exists(file_path):
            return None
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_ext == '.pdf':
                return self._read_pdf(file_path)
            elif file_ext in ['.xlsx', '.xls']:
                return self._read_excel(file_path)
            elif file_ext == '.csv':
                return self._read_csv(file_path)
            elif file_ext == '.json':
                return self._read_json(file_path)
            elif file_ext == '.txt':
                return self._read_txt(file_path)
            elif file_ext == '.sql':
                return self._read_sql(file_path)
            else:
                return f"Неподдерживаемый формат файла: {file_ext}"
                
        except Exception as e:
            return f"Ошибка чтения файла: {str(e)}"
    
    def _read_pdf(self, file_path):
        """Читает текст из PDF файла"""
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            return f"Ошибка чтения PDF: {str(e)}"
    
    def _read_excel(self, file_path):
        """Читает данные из Excel файла"""
        try:
            # Читаем все листы
            excel_file = pd.ExcelFile(file_path)
            result = {}
            
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                # Преобразуем DataFrame в словарь для лучшей обработки
                result[sheet_name] = {
                    "columns": df.columns.tolist(),
                    "data": df.fillna('').astype(str).to_dict('records')
                }
            
            return json.dumps(result, ensure_ascii=False, indent=2)
        except Exception as e:
            return f"Ошибка чтения Excel: {str(e)}"
    
    def _read_csv(self, file_path):
        """Читает данные из CSV файла"""
        try:
            df = pd.read_csv(file_path)
            return {
                "columns": df.columns.tolist(),
                "data": df.fillna('').astype(str).to_dict('records')
            }
        except Exception as e:
            return f"Ошибка чтения CSV: {str(e)}"
    
    def _read_json(self, file_path):
        """Читает данные из JSON файла"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                return json.dumps(data, ensure_ascii=False, indent=2)
        except Exception as e:
            return f"Ошибка чтения JSON: {str(e)}"
    
    def _read_txt(self, file_path):
        """Читает текст из TXT файла"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            return f"Ошибка чтения TXT: {str(e)}"
    
    def _read_sql(self, file_path):
        """Читает SQL файл"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            return f"Ошибка чтения SQL: {str(e)}"
    
    def _extract_json(self, text):
        """Извлекает JSON из текста ответа"""
        try:
            start = text.find('{')
            end = text.rfind('}') + 1
            
            if start != -1 and end != 0:
                json_str = text[start:end]
                return json.loads(json_str)
            else:
                return json.loads(text)
        except:
            return {"raw_response": text}

def save_to_json(data, output_path):
    """Сохраняет данные в JSON файл"""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ Ошибка сохранения: {e}")
        return False

def get_user_files():
    """Получает пути к файлам от пользователя"""
    print("\n📁 Введите пути к файлам (через запятую или каждый с новой строки):")
    print("(Для завершения введите пустую строку)")
    
    file_paths = []
    while True:
        path = input().strip()
        if not path:
            break
        # Разделяем пути, если введены через запятую
        paths = [p.strip() for p in path.split(',') if p.strip()]
        file_paths.extend(paths)
    
    return file_paths

def main():
    print("🚀 Обработчик файлов с GigaChat")
    print("=" * 50)
    
    try:
        # Инициализируем процессор
        processor = FileDataProcessor()
        
        # Получаем файлы от пользователя
        file_paths = get_user_files()
        
        if not file_paths:
            print("❌ Не указаны файлы для обработки")
            return
        
        # Проверяем существование файлов
        valid_files = []
        for file_path in file_paths:
            if os.path.exists(file_path):
                valid_files.append(file_path)
                print(f"✅ Найден: {file_path}")
            else:
                print(f"❌ Не найден: {file_path}")
        
        if not valid_files:
            print("❌ Нет доступных файлов для обработки")
            return
        
        print("\n🎯 Введите критерии фильтрации:")
        print("(Пример: 'оставить только строки где возраст больше 18', 'выбрать товары категории электроника' и т.д.)")
        filter_criteria = input("Критерии: ").strip()
        
        if not filter_criteria:
            print("❌ Не введены критерии фильтрации")
            return
        
        # Обрабатываем каждый файл
        all_results = {}
        
        for file_path in valid_files:
            print(f"\n🔄 Обрабатываю файл: {os.path.basename(file_path)}")
            
            result = processor.process_file(file_path, filter_criteria)
            all_results[os.path.basename(file_path)] = result
            
            # Сохраняем индивидуальный результат
            output_file = f"filtered_{os.path.splitext(os.path.basename(file_path))[0]}.json"
            if save_to_json(result, output_file):
                print(f"✅ Результат сохранен в: {output_file}")
        
        # Сохраняем объединенный результат
        if save_to_json(all_results, "all_filtered_results.json"):
            print(f"\n📊 Общий результат сохранен в: all_filtered_results.json")
        
        # Показываем сводку
        print(f"\n📈 Обработано файлов: {len(valid_files)}")
        for file_path in valid_files:
            print(f"   📄 {os.path.basename(file_path)}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def show_supported_formats():
    """Показывает поддерживаемые форматы файлов"""
    print("\n📋 Поддерживаемые форматы файлов:")
    formats = {
        ".pdf": "PDF документы",
        ".xlsx, .xls": "Excel таблицы", 
        ".csv": "CSV файлы",
        ".json": "JSON данные",
        ".txt": "Текстовые файлы",
        ".sql": "SQL файлы"
    }
    
    for ext, desc in formats.items():
        print(f"   🔹 {ext} - {desc}")

if __name__ == "__main__":
    # Показываем поддерживаемые форматы
    show_supported_formats()
    print("\n" + "="*50)
    
    # Запускаем основную программу
    main()
import os
import json
import pandas as pd
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import sys

sys.path.append('../HACKATHON-DISCOVER-MOSPROM')
load_dotenv()

app = Flask(__name__)

class SmartChartProcessor:
    def __init__(self):
        self.available_filters = self._get_default_filters()
    
    def _get_default_filters(self):
        return {
            "industry_type": {
                "name": "Отрасль промышленности",
                "type": "select",
                "options": ["Все", "Машиностроение", "Химическая", "Пищевая", "Металлургия", "Электроника"]
            },
            "region": {
                "name": "Округ Москвы", 
                "type": "select",
                "options": ["Все", "ЦАО", "САО", "СВАО", "ВАО", "ЮВАО", "ЮАО", "ЮЗАО", "ЗАО", "СЗАО", "НАО", "ТАО"]
            },
            "period": {
                "name": "Период",
                "type": "select", 
                "options": ["2024", "2023", "2022", "2021"]
            },
            "employee_count": {
                "name": "Численность сотрудников",
                "type": "range",
                "min": 0,
                "max": 5000
            }
        }
    
    def get_sample_data(self, filters):
        sample_data = [
            {"id": 1, "name": "Завод №1", "industry": "Машиностроение", "region": "ЦАО", 
             "production": 1500000, "employees": 1200, "revenue": 45000000, "growth": 5.2, "period": "2024-01"},
            {"id": 2, "name": "Химкомбинат", "industry": "Химическая", "region": "ЮАО",
             "production": 890000, "employees": 800, "revenue": 32000000, "growth": 3.8, "period": "2024-01"},
            {"id": 3, "name": "Пищекомбинат", "industry": "Пищевая", "region": "САО", 
             "production": 2100000, "employees": 1500, "revenue": 68000000, "growth": 7.1, "period": "2024-01"},
            {"id": 4, "name": "Металлург", "industry": "Металлургия", "region": "ВАО",
             "production": 1750000, "employees": 2000, "revenue": 55000000, "growth": 4.2, "period": "2024-02"},
            {"id": 5, "name": "Электроникс", "industry": "Электроника", "region": "ЗАО",
             "production": 950000, "employees": 600, "revenue": 28000000, "growth": 8.5, "period": "2024-02"},
            {"id": 6, "name": "Машстрой", "industry": "Машиностроение", "region": "СЗАО",
             "production": 1200000, "employees": 900, "revenue": 38000000, "growth": 6.1, "period": "2024-02"},
            {"id": 7, "name": "ХимПром", "industry": "Химическая", "region": "ВАО",
             "production": 1100000, "employees": 750, "revenue": 35000000, "growth": 4.8, "period": "2024-03"},
            {"id": 8, "name": "Продукты", "industry": "Пищевая", "region": "ЮЗАО",
             "production": 1900000, "employees": 1300, "revenue": 62000000, "growth": 6.9, "period": "2024-03"}
        ]
        
        filtered_data = self._apply_filters(sample_data, filters)
        return filtered_data
    
    def _apply_filters(self, data, filters):
        filtered = data.copy()
        
        if filters.get('industry_type') and filters['industry_type'] != "Все":
            filtered = [item for item in filtered if item['industry'] == filters['industry_type']]
        
        if filters.get('region') and filters['region'] != "Все":
            filtered = [item for item in filtered if item['region'] == filters['region']]
        
        if filters.get('period') and filters['period'] != "Все":
            filtered = [item for item in filtered if filters['period'] in item.get('period', '')]
        
        if filters.get('employee_count'):
            min_emp = filters['employee_count'].get('min', 0)
            max_emp = filters['employee_count'].get('max', 5000)
            filtered = [item for item in filtered if min_emp <= item['employees'] <= max_emp]
        
        return filtered
    
    def analyze_for_charts(self, data, create_charts=True):
        if not data:
            return {"error": "Нет данных для анализа"}
        
        df = pd.DataFrame(data)
        
        # Автоматически определяем числовые колонки, ИСКЛЮЧАЯ ID
        numeric_columns = [col for col in df.select_dtypes(include=['number']).columns.tolist() if col != 'id']
        categorical_columns = df.select_dtypes(include=['object']).columns.tolist()
        
        result = {
            "summary": {
                "total_records": len(data),
                "numeric_columns": numeric_columns,
                "categorical_columns": categorical_columns,
                "can_create_charts": len(numeric_columns) > 0 and create_charts
            },
            "data": data
        }
        
        if create_charts and numeric_columns:
            result["charts"] = self._create_charts(df, numeric_columns, categorical_columns)
        else:
            result["charts"] = None
            result["message"] = "Графики не созданы: нет числовых данных или пользователь отказался"
        
        return result

    def _create_charts(self, df, numeric_columns, categorical_columns):
        """Создает графики только для числовых данных"""
        charts = {}
        
        # ИСКЛЮЧАЕМ ID ИЗ ЧИСЛОВЫХ КОЛОНОК ДЛЯ ГРАФИКОВ
        meaningful_numeric_columns = [col for col in numeric_columns if col != 'id']
        
        if not meaningful_numeric_columns:
            return charts
        
        # Берем первую значимую числовую колонку (не id)
        numeric_column = meaningful_numeric_columns[0]
        
        # График распределения по отраслям (если есть категориальные данные)
        if 'industry' in categorical_columns:
            industry_data = df.groupby('industry')[numeric_column].sum()
            if not industry_data.empty:
                charts['industry_distribution'] = {
                    "type": "bar",
                    "title": f"Распределение {numeric_column} по отраслям",
                    "data": {
                        "labels": industry_data.index.tolist(),
                        "datasets": [{
                            "label": numeric_column,
                            "data": industry_data.values.tolist(),
                            "backgroundColor": [
                                'rgba(255, 99, 132, 0.6)',
                                'rgba(54, 162, 235, 0.6)', 
                                'rgba(255, 206, 86, 0.6)',
                                'rgba(75, 192, 192, 0.6)',
                                'rgba(153, 102, 255, 0.6)'
                            ]
                        }]
                    }
                }
        
        # График по регионам
        if 'region' in categorical_columns:
            region_data = df.groupby('region')[numeric_column].sum()
            if not region_data.empty:
                charts['region_distribution'] = {
                    "type": "bar", 
                    "title": f"Распределение {numeric_column} по округам",
                    "data": {
                        "labels": region_data.index.tolist(),
                        "datasets": [{
                            "label": numeric_column,
                            "data": region_data.values.tolist(),
                            "backgroundColor": 'rgba(54, 162, 235, 0.6)'
                        }]
                    }
                }
        
        # Круговая диаграмма по отраслям (если данных не слишком много)
        if 'industry' in categorical_columns and len(df['industry'].unique()) <= 10:
            industry_sum = df.groupby('industry')[numeric_column].sum()
            if not industry_sum.empty:
                charts['industry_pie'] = {
                    "type": "pie",
                    "title": f"Доля {numeric_column} по отраслям",
                    "data": {
                        "labels": industry_sum.index.tolist(),
                        "datasets": [{
                            "data": industry_sum.values.tolist(),
                            "backgroundColor": [
                                'rgba(255, 99, 132, 0.6)',
                                'rgba(54, 162, 235, 0.6)',
                                'rgba(255, 206, 86, 0.6)',
                                'rgba(75, 192, 192, 0.6)',
                                'rgba(153, 102, 255, 0.6)',
                                'rgba(255, 159, 64, 0.6)'
                            ]
                        }]
                    }
                }
        
        # Линейный график если есть временные данные
        if 'period' in df.columns:
            try:
                period_data = df.groupby('period')[numeric_column].sum().sort_index()
                if not period_data.empty:
                    charts['trend'] = {
                        "type": "line",
                        "title": f"Динамика {numeric_column} по периодам",
                        "data": {
                            "labels": period_data.index.tolist(),
                            "datasets": [{
                                "label": numeric_column,
                                "data": period_data.values.tolist(),
                                "borderColor": 'rgba(75, 192, 192, 1)',
                                "backgroundColor": 'rgba(75, 192, 192, 0.2)',
                                "fill": True
                            }]
                        }
                    }
            except Exception as e:
                print(f"Ошибка создания трендового графика: {e}")
        
        # Если есть вторая числовая колонка, создаем scatter plot
        if len(meaningful_numeric_columns) >= 2:
            second_numeric = meaningful_numeric_columns[1]
            scatter_data = []
            for _, row in df.iterrows():
                scatter_data.append({
                    'x': row[numeric_column],
                    'y': row[second_numeric]
                })
            
            charts['scatter'] = {
                "type": "scatter",
                "title": f"{numeric_column} vs {second_numeric}",
                "data": {
                    "datasets": [{
                        "label": "Предприятия",
                        "data": scatter_data,
                        "backgroundColor": 'rgba(255, 99, 132, 0.6)'
                    }]
                },
                "options": {
                    "scales": {
                        "x": {
                            "title": {
                                "display": True,
                                "text": numeric_column
                            }
                        },
                        "y": {
                            "title": {
                                "display": True,
                                "text": second_numeric
                            }
                        }
                    }
                }
            }
        
        return charts

@app.route('/')
def index():
    processor = SmartChartProcessor()
    return render_template('index.html', filters=processor.available_filters)

@app.route('/api/filters')
def get_filters():
    processor = SmartChartProcessor()
    return jsonify(processor.available_filters)

@app.route('/api/analyze', methods=['POST'])
def analyze_data():
    try:
        data = request.json
        filters = data.get('filters', {})
        create_charts = data.get('create_charts', True)
        
        processor = SmartChartProcessor()
        sample_data = processor.get_sample_data(filters)
        result = processor.analyze_for_charts(sample_data, create_charts)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
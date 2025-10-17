from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime
import os
from dotenv import load_dotenv
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from data import db_session
from flasgger import Swagger
from api import *
from flask_restful import Api
from functools import wraps
from flask import abort
import requests
import os
from werkzeug.utils import secure_filename
from dotenv import load_dotenv


app = Flask(__name__)

load_dotenv()
# Конфигурация
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# swagger = Swagger(app, template={
#         "swagger": "2.0",
#         "info": {
#             "title": "API документация",
#             "description": "Документация д  ля всех доступных API",
#             "version": "1.0"
#         },
#         "consumes": [
#         "application/json"
#         ],
#         # "host": f"",
#         "basePath": "/",
#         "schemes": [
#             "http"
#         ],
#         "tags": [
#             {
#                 "name": "Application Requests",
#                 "description": "Операции с заявками"
#             },
#             {
#                 "name": "Application Eviction",
#                 "description": "Операции с заявками на выселение"
#             },
#             {
#                 "name": "Students",
#                 "description": "Операции со студентами"
#             },
#             {
#                 "name": "Rooms",
#                 "description": "Операции с комнатами"
#             },
#             {
#                 "name": "Hostels",
#                 "description": "Операции с общежитиями"
#             }
#         ]
#     })

api = Api(app)

def init_db():
    db_path = os.path.join(os.path.dirname(__file__), "db/database.db")
    print(f"Initializing database at: {db_path}")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    db_session.global_init(db_path)


@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part"

    file = request.files['file']
    if file.filename == '':
        return "No selected file"

    # Сохранение файла
    filepath = os.path.join('static/uploads', file.filename)
    file.save(filepath)

    return render_template('index.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Страница контактов с формой"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        
        # Здесь можно добавить логику сохранения сообщения
        return render_template('contact.html', 
                             success=True, 
                             name=name)
    
    return render_template('contact.html')

@app.route('/about')
def about():
    """Страница о проекте"""
    return render_template('about.html')

@app.errorhandler(404)
def not_found(error):
    """Обработчик ошибки 404"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Обработчик ошибки 500"""
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Создаем папку для шаблонов если её нет
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    init_db()

    
    app.run(debug=True, host='0.0.0.0', port=5000)

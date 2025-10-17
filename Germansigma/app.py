import os
from flask import Flask, render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 МБ максимальный размер файла

# Разрешенные расширения файлов
ALLOWED_EXTENSIONS = {'csv', 'xlsx'}

# Создаем папку для загрузок, если она не существует
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


def allowed_file(filename):
    """Проверяет, разрешено ли расширение файла"""
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Главная страница с формой загрузки"""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """Обработка загрузки файла"""
    try:
        # Проверяем наличие файла в запросе
        if 'file' not in request.files:
            flash('Файл не выбран', 'error')
            return redirect(url_for('index'))

        file = request.files['file']

        # Если пользователь не выбрал файл
        if file.filename == '':
            flash('Файл не выбран', 'error')
            return redirect(url_for('index'))

        # Проверяем расширение файла
        if not allowed_file(file.filename):
            flash('Неверный формат файла. Разрешены только CSV и XLSX файлы.', 'error')
            return redirect(url_for('index'))

        # Если файл валиден, сохраняем его
        if file:
            # Безопасное имя файла
            filename = secure_filename(file.filename)

            # Генерируем уникальное имя, если файл уже существует
            base_filename, extension = os.path.splitext(filename)
            counter = 1
            while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
                filename = f"{base_filename}_{counter}{extension}"
                counter += 1

            # Сохраняем файл
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Получаем размер файла
            file_size = os.path.getsize(filepath)
            file_size_mb = round(file_size / (1024 * 1024), 2)

            flash(f'Файл "{filename}" успешно загружен! Размер: {file_size_mb} МБ', 'success')
            return redirect(url_for('index'))

    except RequestEntityTooLarge:
        flash('Файл слишком большой. Максимальный размер: 16 МБ', 'error')
        return redirect(url_for('index'))
    except Exception as e:
        flash(f'Произошла ошибка при загрузке файла: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.errorhandler(413)
def request_entity_too_large(error):
    flash('Файл слишком большой. Максимальный размер: 16 МБ', 'error')
    return redirect(url_for('index'))


@app.errorhandler(404)
def page_not_found(error):
    return render_template('index.html'), 404


if __name__ == '__main__':
    app.run(debug=True, port=8000)
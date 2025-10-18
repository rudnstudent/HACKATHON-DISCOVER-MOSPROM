// Moscow Industry Database - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Инициализация всех компонентов
    initAnimations();
    initFormValidation();
    initTooltips();
    initSmoothScrolling();
});

// Анимации при скролле
function initAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
            }
        });
    }, observerOptions);

    // Наблюдаем за всеми карточками и секциями
    document.querySelectorAll('.card, .hero-section, .stats-card').forEach(element => {
        observer.observe(element);
    });
}

// Валидация форм
function initFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
            }
        });
    });
}

// Валидация конкретной формы
function validateForm(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            showFieldError(field, 'Это поле обязательно для заполнения');
            isValid = false;
        } else {
            clearFieldError(field);
            
            // Дополнительная валидация для email
            if (field.type === 'email' && !isValidEmail(field.value)) {
                showFieldError(field, 'Введите корректный email адрес');
                isValid = false;
            }
        }
    });
    
    return isValid;
}

// Показать ошибку поля
function showFieldError(field, message) {
    clearFieldError(field);
    
    field.classList.add('is-invalid');
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    
    field.parentNode.appendChild(errorDiv);
}

// Очистить ошибку поля
function clearFieldError(field) {
    field.classList.remove('is-invalid');
    
    const errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.remove();
    }
}

// Валидация email
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Инициализация тултипов
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Плавная прокрутка
function initSmoothScrolling() {
    const links = document.querySelectorAll('a[href^="#"]');
    
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                e.preventDefault();
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Утилиты
const Utils = {
    // Форматирование чисел
    formatNumber: function(num) {
        return new Intl.NumberFormat('ru-RU').format(num);
    },
    
    // Форматирование валюты
    formatCurrency: function(amount) {
        return new Intl.NumberFormat('ru-RU', {
            style: 'currency',
            currency: 'RUB'
        }).format(amount);
    },
    
    // Форматирование даты
    formatDate: function(date) {
        return new Intl.DateTimeFormat('ru-RU').format(new Date(date));
    },
    
    // Дебаунс функция
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    // Проверка на мобильное устройство
    isMobile: function() {
        return window.innerWidth <= 768;
    }
};

// API утилиты
const API = {
    // Базовый URL API
    baseURL: '/api',
    
    // Выполнение GET запроса
    get: async function(endpoint) {
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('API GET Error:', error);
            throw error;
        }
    },
    
    // Выполнение POST запроса
    post: async function(endpoint, data) {
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('API POST Error:', error);
            throw error;
        }
    }
};

// Уведомления
const Notifications = {
    // Показать уведомление
    show: function(message, type = 'info', duration = 5000) {
        const alertClass = `alert-${type}`;
        const iconClass = this.getIconClass(type);
        
        const notification = document.createElement('div');
        notification.className = `alert ${alertClass} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        
        notification.innerHTML = `
            <i class="${iconClass} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Автоматическое удаление
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, duration);
    },
    
    // Получить класс иконки
    getIconClass: function(type) {
        const icons = {
            'success': 'fas fa-check-circle',
            'danger': 'fas fa-exclamation-circle',
            'warning': 'fas fa-exclamation-triangle',
            'info': 'fas fa-info-circle'
        };
        return icons[type] || icons['info'];
    },
    
    // Успешное уведомление
    success: function(message) {
        this.show(message, 'success');
    },
    
    // Ошибка
    error: function(message) {
        this.show(message, 'danger');
    },
    
    // Предупреждение
    warning: function(message) {
        this.show(message, 'warning');
    },
    
    // Информация
    info: function(message) {
        this.show(message, 'info');
    }
};

// Экспорт для использования в других скриптах
window.Utils = Utils;
window.API = API;
window.Notifications = Notifications;

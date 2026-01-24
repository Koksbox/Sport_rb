// СпортБаш - Основной JavaScript

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Проверка Telegram Mini App
    if (window.Telegram && window.Telegram.WebApp) {
        const tg = window.Telegram.WebApp;
        tg.ready();
        tg.expand();
        
        // Настройка темы Telegram
        if (tg.colorScheme === 'dark') {
            document.body.classList.add('telegram-dark');
        }
    }
    
    // Инициализация бургер-меню
    initBurgerMenu();
    
    // Обработка форм с HTMX
    initHTMXForms();
    
    // Автоматическое скрытие сообщений
    autoHideMessages();
});

// Инициализация HTMX форм
function initHTMXForms() {
    // Добавление индикаторов загрузки
    document.body.addEventListener('htmx:beforeRequest', function(event) {
        const form = event.detail.elt.closest('form');
        if (form) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="loading"></span> Отправка...';
            }
        }
    });
    
    document.body.addEventListener('htmx:afterRequest', function(event) {
        const form = event.detail.elt.closest('form');
        if (form) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = false;
                const originalText = submitBtn.getAttribute('data-original-text') || 'Отправить';
                submitBtn.innerHTML = originalText;
            }
        }
    });
    
    // Обработка успешных ответов
    document.body.addEventListener('htmx:afterSwap', function(event) {
        if (event.detail.target.id === 'messages') {
            autoHideMessages();
        }
        
        // Прокрутка к новому контенту
        if (event.detail.target) {
            event.detail.target.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    });
}

// Инициализация бургер-меню
function initBurgerMenu() {
    const burgerMenus = document.querySelectorAll('.burger-menu');
    
    if (burgerMenus.length === 0) {
        return;
    }
    
    burgerMenus.forEach(function(burgerMenu) {
        const burgerBtn = burgerMenu.querySelector('.burger-btn');
        const burgerDropdown = burgerMenu.querySelector('.burger-dropdown');
        
        if (!burgerBtn || !burgerDropdown) {
            return;
        }
        
        // Переключение меню при клике на кнопку
        burgerBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            burgerBtn.classList.toggle('active');
            burgerDropdown.classList.toggle('active');
        });
        
        // Закрытие меню при клике на ссылку внутри меню
        const burgerLinks = burgerDropdown.querySelectorAll('.burger-link');
        burgerLinks.forEach(function(link) {
            link.addEventListener('click', function() {
                burgerBtn.classList.remove('active');
                burgerDropdown.classList.remove('active');
            });
        });
    });
    
    // Закрытие всех меню при клике вне их
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.burger-menu')) {
            burgerMenus.forEach(function(burgerMenu) {
                const burgerBtn = burgerMenu.querySelector('.burger-btn');
                const burgerDropdown = burgerMenu.querySelector('.burger-dropdown');
                if (burgerBtn && burgerDropdown) {
                    burgerBtn.classList.remove('active');
                    burgerDropdown.classList.remove('active');
                }
            });
        }
    });
}

// Автоматическое скрытие сообщений
function autoHideMessages() {
    const messages = document.querySelectorAll('.alert');
    messages.forEach(function(msg) {
        setTimeout(function() {
            msg.style.transition = 'opacity 0.5s';
            msg.style.opacity = '0';
            setTimeout(function() {
                msg.remove();
            }, 500);
        }, 5000);
    });
}

// API функции для работы с бэкендом
const API = {
    baseURL: '/api',
    
    async request(url, options = {}) {
        const token = localStorage.getItem('access_token');
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };
        
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        try {
            const response = await fetch(`${this.baseURL}${url}`, {
                ...options,
                headers
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || data.detail || 'Ошибка запроса');
            }
            
            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },
    
    async get(url) {
        return this.request(url, { method: 'GET' });
    },
    
    async post(url, data) {
        return this.request(url, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },
    
    async put(url, data) {
        return this.request(url, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },
    
    async delete(url) {
        return this.request(url, { method: 'DELETE' });
    }
};

// Сохранение токена после авторизации
function saveToken(accessToken, refreshToken) {
    localStorage.setItem('access_token', accessToken);
    if (refreshToken) {
        localStorage.setItem('refresh_token', refreshToken);
    }
}

// Получение токена
function getToken() {
    return localStorage.getItem('access_token');
}

// Выход
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = '/login/';
}

// Экспорт для использования в других скриптах
window.SportBash = {
    API,
    saveToken,
    getToken,
    logout
};

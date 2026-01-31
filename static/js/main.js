// СпортБаш - Основной JavaScript

// Инициализация при загрузке страницы
function initializeApp() {
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
}

// Функция для принудительной инициализации бургер-меню
function forceInitBurgerMenu() {
    // Удаляем все атрибуты инициализации для переинициализации
    document.querySelectorAll('.burger-btn').forEach(function(btn) {
        btn.removeAttribute('data-burger-initialized');
    });
    // Всегда инициализируем заново (удаление старых обработчиков происходит внутри initBurgerMenu)
    initBurgerMenu();
}

// Запускаем инициализацию при загрузке DOM
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        initializeApp();
        // Дополнительная инициализация бургер-меню
        setTimeout(forceInitBurgerMenu, 50);
    });
} else {
    // DOM уже загружен
    initializeApp();
    setTimeout(forceInitBurgerMenu, 50);
}

// Дополнительная инициализация через небольшую задержку (на случай динамической загрузки)
setTimeout(forceInitBurgerMenu, 100);
setTimeout(forceInitBurgerMenu, 300);
setTimeout(forceInitBurgerMenu, 500);

// Инициализация после полной загрузки страницы (включая все ресурсы)
window.addEventListener('load', function() {
    forceInitBurgerMenu();
});

// Инициализация при изменении DOM (для динамически загружаемого контента)
if (window.MutationObserver) {
    let initTimeout;
    const observer = new MutationObserver(function(mutations) {
        // Используем debounce для избежания множественных вызовов
        clearTimeout(initTimeout);
        initTimeout = setTimeout(function() {
            const hasBurgerMenu = document.querySelector('.burger-menu');
            if (hasBurgerMenu) {
                // Всегда переинициализируем при обнаружении меню
                // Это нужно для работы при переходе на новые страницы
                forceInitBurgerMenu();
            }
        }, 100);
    });
    
    // Начинаем наблюдение за изменениями в body
    if (document.body) {
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
}

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

// Инициализация бургер-меню - упрощенная версия с делегированием событий
function initBurgerMenu() {
    // Удаляем старый глобальный обработчик, если есть
    if (document._burgerMenuGlobalHandler) {
        document.removeEventListener('click', document._burgerMenuGlobalHandler, true);
        document._burgerMenuGlobalHandler = null;
    }
    
    // Используем делегирование событий - один обработчик на весь document
    const globalClickHandler = function(e) {
        const target = e.target;
        
        // Проверяем, кликнули ли на кнопку бургер-меню
        const burgerBtn = target.closest('.burger-btn');
        if (burgerBtn) {
            e.preventDefault();
            e.stopPropagation();
            
            const burgerMenu = burgerBtn.closest('.burger-menu');
            const dropdown = burgerMenu ? burgerMenu.querySelector('.burger-dropdown') : null;
            
            if (!dropdown) return;
            
            const isActive = burgerBtn.classList.contains('active');
            
            // Закрываем все другие меню
            document.querySelectorAll('.burger-menu').forEach(function(menu) {
                const otherBtn = menu.querySelector('.burger-btn');
                const otherDropdown = menu.querySelector('.burger-dropdown');
                if (otherBtn && otherDropdown && otherBtn !== burgerBtn) {
                    otherBtn.classList.remove('active');
                    otherDropdown.classList.remove('active');
                }
            });
            
            // Переключаем текущее меню
            if (isActive) {
                burgerBtn.classList.remove('active');
                dropdown.classList.remove('active');
            } else {
                burgerBtn.classList.add('active');
                dropdown.classList.add('active');
            }
            return;
        }
        
        // Проверяем, кликнули ли на ссылку внутри меню
        const burgerLink = target.closest('.burger-link');
        if (burgerLink) {
            const burgerMenu = burgerLink.closest('.burger-menu');
            if (burgerMenu) {
                const btn = burgerMenu.querySelector('.burger-btn');
                const dropdown = burgerMenu.querySelector('.burger-dropdown');
                if (btn && dropdown) {
                    // Закрываем меню после небольшой задержки (чтобы переход успел произойти)
                    setTimeout(function() {
                        btn.classList.remove('active');
                        dropdown.classList.remove('active');
                    }, 100);
                }
            }
            return;
        }
        
        // Если клик был вне бургер-меню, закрываем все меню
        const clickedMenu = target.closest('.burger-menu');
        if (!clickedMenu) {
            document.querySelectorAll('.burger-menu').forEach(function(menu) {
                const btn = menu.querySelector('.burger-btn');
                const dropdown = menu.querySelector('.burger-dropdown');
                if (btn && dropdown) {
                    btn.classList.remove('active');
                    dropdown.classList.remove('active');
                }
            });
        }
    };
    
    // Добавляем обработчик с capture фазой для более раннего перехвата
    document.addEventListener('click', globalClickHandler, true);
    document._burgerMenuGlobalHandler = globalClickHandler;
}

// Делаем функцию доступной глобально
window.initBurgerMenu = initBurgerMenu;

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

// Утилиты для работы с HTML и cookies
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Улучшенная функция для API запросов с обработкой ошибок
async function apiRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    // Добавляем CSRF токен
    const csrfToken = getCookie('csrftoken');
    if (csrfToken) {
        defaultOptions.headers['X-CSRFToken'] = csrfToken;
    }
    
    // Объединяем опции
    const finalOptions = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...(options.headers || {})
        }
    };
    
    try {
        const response = await fetch(url, finalOptions);
        
        // Проверяем, есть ли ответ
        let data;
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            data = await response.json();
        } else {
            data = await response.text();
        }
        
        if (!response.ok) {
            throw new Error(data.error || data.detail || data.message || `HTTP ${response.status}`);
        }
        
        return { status: response.status, data };
    } catch (error) {
        console.error('API Request Error:', error);
        throw error;
    }
}

// Toast Notification System - перенесено в toast.js
// Toast Notification System - перенесено в toast.js
// ToastManager будет определен в toast.js (загружается после main.js)

// Confirmation Dialog
function showConfirm(message, title = 'Подтверждение', confirmText = 'Да', cancelText = 'Отмена') {
    return new Promise((resolve) => {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.style.display = 'block';
        
        modal.innerHTML = `
            <div class="modal-content" style="max-width: 500px;">
                <div class="modal-header">
                    <h3>${escapeHtml(title)}</h3>
                    <button class="close" type="button">&times;</button>
                </div>
                <div class="modal-body">
                    <p>${escapeHtml(message)}</p>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary cancel-btn" type="button">${escapeHtml(cancelText)}</button>
                    <button class="btn btn-primary confirm-btn" type="button">${escapeHtml(confirmText)}</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Обработчики для кнопок
        const closeBtn = modal.querySelector('.close');
        const cancelBtn = modal.querySelector('.cancel-btn');
        const confirmBtn = modal.querySelector('.confirm-btn');
        
        const closeModal = (result) => {
            modal.remove();
            document.removeEventListener('keydown', escapeHandler);
            resolve(result);
        };
        
        // Закрытие по кнопке X
        closeBtn.addEventListener('click', () => closeModal(false));
        
        // Кнопка отмены
        cancelBtn.addEventListener('click', () => closeModal(false));
        
        // Кнопка подтверждения
        confirmBtn.addEventListener('click', () => closeModal(true));
        
        // Закрытие по клику вне модального окна
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeModal(false);
            }
        });
        
        // Закрытие по Escape
        const escapeHandler = function(e) {
            if (e.key === 'Escape') {
                closeModal(false);
            }
        };
        document.addEventListener('keydown', escapeHandler);
        
        // Фокус на кнопке подтверждения
        setTimeout(() => {
            confirmBtn.focus();
        }, 100);
    });
}

// Улучшенная функция для показа сообщений об ошибках
function showError(message, title = 'Ошибка') {
    if (window.toastManager) {
        window.toastManager.error(message, title);
    } else {
        alert(title + ': ' + message);
    }
}

function showSuccess(message, title = 'Успешно') {
    if (window.toastManager) {
        window.toastManager.success(message, title);
    } else {
        alert(title + ': ' + message);
    }
}

function showWarning(message, title = 'Внимание') {
    if (window.toastManager) {
        window.toastManager.warning(message, title);
    } else {
        alert(title + ': ' + message);
    }
}

function showInfo(message, title = 'Информация') {
    if (window.toastManager) {
        window.toastManager.info(message, title);
    } else {
        alert(title + ': ' + message);
    }
}

// Экспорт для использования в других скриптах
window.SportBash = {
    API,
    saveToken,
    getToken,
    logout,
    escapeHtml,
    getCookie,
    apiRequest,
    // toast будет определен в toast.js
    // toast: toastManager,
    // showConfirm будет определен в toast.js
    // showConfirm,
    showError,
    showSuccess,
    showWarning,
    showInfo
};

// Глобальные функции для обратной совместимости
window.escapeHtml = escapeHtml;
window.getCookie = getCookie;
// showConfirm будет определен в toast.js (загружается после main.js)
// window.showConfirm = showConfirm;
window.showError = showError;
window.showSuccess = showSuccess;
window.showWarning = showWarning;
window.showInfo = showInfo;
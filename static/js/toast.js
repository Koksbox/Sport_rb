// Toast Notification System
class ToastManager {
    constructor() {
        this.container = null;
        this.toasts = new Map();
        this.init();
    }
    
    init() {
        // Создаем контейнер для toast-уведомлений
        if (!document.querySelector('.toast-container')) {
            this.container = document.createElement('div');
            this.container.className = 'toast-container';
            document.body.appendChild(this.container);
        } else {
            this.container = document.querySelector('.toast-container');
        }
    }
    
    show(message, type = 'info', title = null, duration = 5000) {
        if (!this.container) this.init();
        
        const toastId = 'toast-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.id = toastId;
        
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };
        
        toast.innerHTML = `
            <span class="toast-icon">${icons[type] || icons.info}</span>
            <div class="toast-content">
                ${title ? `<div class="toast-title">${escapeHtml(title)}</div>` : ''}
                <div class="toast-message">${escapeHtml(message)}</div>
            </div>
            <button class="toast-close" aria-label="Закрыть">&times;</button>
            <div class="toast-progress" style="animation-duration: ${duration}ms;"></div>
        `;
        
        this.container.appendChild(toast);
        this.toasts.set(toastId, toast);
        
        // Закрытие по клику на кнопку
        const closeBtn = toast.querySelector('.toast-close');
        closeBtn.addEventListener('click', () => this.hide(toastId));
        
        // Автоматическое закрытие
        if (duration > 0) {
            setTimeout(() => this.hide(toastId), duration);
        }
        
        return toastId;
    }
    
    hide(toastId) {
        const toast = this.toasts.get(toastId);
        if (!toast) return;
        
        toast.classList.add('toast-exit');
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
            this.toasts.delete(toastId);
        }, 300);
    }
    
    success(message, title = null, duration = 5000) {
        return this.show(message, 'success', title, duration);
    }
    
    error(message, title = null, duration = 7000) {
        return this.show(message, 'error', title, duration);
    }
    
    warning(message, title = null, duration = 6000) {
        return this.show(message, 'warning', title, duration);
    }
    
    info(message, title = null, duration = 5000) {
        return this.show(message, 'info', title, duration);
    }
}

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

// Улучшенные функции для показа сообщений
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

// Инициализация Toast Manager
const toastManager = new ToastManager();
window.toastManager = toastManager;

// Экспорт
window.SportBash = window.SportBash || {};
window.SportBash.toast = toastManager;
window.SportBash.showConfirm = showConfirm;
window.SportBash.showError = showError;
window.SportBash.showSuccess = showSuccess;
window.SportBash.showWarning = showWarning;
window.SportBash.showInfo = showInfo;

// Глобальные функции для обратной совместимости
window.showConfirm = showConfirm;
window.showError = showError;
window.showSuccess = showSuccess;
window.showWarning = showWarning;
window.showInfo = showInfo;

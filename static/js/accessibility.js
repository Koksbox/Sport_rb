// Улучшения accessibility
class AccessibilityManager {
    constructor() {
        this.init();
    }
    
    init() {
        // Добавляем ARIA атрибуты к интерактивным элементам
        this.addAriaLabels();
        
        // Улучшаем навигацию с клавиатуры
        this.improveKeyboardNavigation();
        
        // Добавляем skip links
        this.addSkipLinks();
        
        // Улучшаем фокус
        this.improveFocus();
        
        // Обработка динамического контента
        this.handleDynamicContent();
    }
    
    addAriaLabels() {
        // Кнопки без текста
        document.querySelectorAll('button:not([aria-label]):empty, button:not([aria-label]) img').forEach(btn => {
            const icon = btn.textContent || btn.innerHTML;
            if (icon && !btn.getAttribute('aria-label')) {
                btn.setAttribute('aria-label', this.getLabelFromIcon(icon));
            }
        });
        
        // Формы
        document.querySelectorAll('form').forEach(form => {
            if (!form.getAttribute('aria-label') && !form.querySelector('legend')) {
                const title = form.querySelector('h2, h3, .form-title');
                if (title) {
                    form.setAttribute('aria-labelledby', title.id || this.generateId(title));
                }
            }
        });
    }
    
    improveKeyboardNavigation() {
        // Обработка Enter на карточках
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && e.target.classList.contains('item-card')) {
                e.target.click();
            }
        });
        
        // Обработка Escape для закрытия модальных окон
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                const modals = document.querySelectorAll('.modal[style*="block"]');
                modals.forEach(modal => {
                    const closeBtn = modal.querySelector('.close');
                    if (closeBtn) closeBtn.click();
                });
            }
        });
        
        // Tab navigation для карточек
        document.querySelectorAll('.item-card').forEach(card => {
            if (!card.getAttribute('tabindex')) {
                card.setAttribute('tabindex', '0');
                card.setAttribute('role', 'button');
            }
        });
    }
    
    addSkipLinks() {
        const skipLink = document.createElement('a');
        skipLink.href = '#main-content';
        skipLink.className = 'skip-link sr-only';
        skipLink.textContent = 'Перейти к основному содержимому';
        skipLink.addEventListener('focus', function() {
            this.classList.remove('sr-only');
        });
        skipLink.addEventListener('blur', function() {
            this.classList.add('sr-only');
        });
        document.body.insertBefore(skipLink, document.body.firstChild);
        
        // Добавляем id к основному контенту
        const mainContent = document.querySelector('.main-content');
        if (mainContent && !mainContent.id) {
            mainContent.id = 'main-content';
        }
    }
    
    improveFocus() {
        // Улучшенные стили фокуса уже в CSS
        // Добавляем визуальную индикацию для фокуса
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                document.body.classList.add('keyboard-navigation');
            }
        });
        
        document.addEventListener('mousedown', () => {
            document.body.classList.remove('keyboard-navigation');
        });
    }
    
    handleDynamicContent() {
        // Обработка динамически добавленного контента
        if (window.MutationObserver) {
            const observer = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    mutation.addedNodes.forEach((node) => {
                        if (node.nodeType === 1) { // Element node
                            // Добавляем ARIA к новым элементам
                            if (node.classList && node.classList.contains('item-card')) {
                                node.setAttribute('tabindex', '0');
                                node.setAttribute('role', 'button');
                            }
                            
                            // Добавляем ARIA к новым формам
                            if (node.tagName === 'FORM') {
                                const title = node.querySelector('h2, h3, .form-title');
                                if (title && !node.getAttribute('aria-label')) {
                                    const titleId = title.id || this.generateId(title);
                                    title.id = titleId;
                                    node.setAttribute('aria-labelledby', titleId);
                                }
                            }
                        }
                    });
                });
            });
            
            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
        }
    }
    
    getLabelFromIcon(icon) {
        const iconMap = {
            '❤️': 'В избранном',
            '🤍': 'Добавить в избранное',
            '✏️': 'Редактировать',
            '🗑️': 'Удалить',
            '➕': 'Добавить',
            '🔍': 'Поиск',
            '📅': 'Календарь',
            '🏢': 'Организации',
            '🏆': 'Мероприятия',
            '🔔': 'Уведомления'
        };
        
        for (const [emoji, label] of Object.entries(iconMap)) {
            if (icon.includes(emoji)) {
                return label;
            }
        }
        
        return 'Кнопка';
    }
    
    generateId(element) {
        const text = element.textContent || element.innerText || '';
        const id = 'id_' + text.toLowerCase().replace(/[^a-z0-9]+/g, '_').substring(0, 20);
        element.id = id;
        return id;
    }
}

// Инициализация
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new AccessibilityManager();
    });
} else {
    new AccessibilityManager();
}

// Экспорт
window.AccessibilityManager = AccessibilityManager;

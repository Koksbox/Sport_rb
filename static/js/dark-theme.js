// Управление темной темой
class DarkThemeManager {
    constructor() {
        this.storageKey = 'sportbash_dark_theme';
        this.init();
    }
    
    init() {
        // Проверяем, что document.body существует
        if (!document.body) {
            // Если body еще не загружен, ждем
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => this.init());
                return;
            }
        }
        
        try {
            // Проверяем сохраненную настройку пользователя
            const saved = localStorage.getItem(this.storageKey);
            
            // По умолчанию всегда светлая тема
            // Темная тема включается только если пользователь явно выбрал её
            if (saved === 'true') {
                this.enable();
            } else {
                // Если настройка не сохранена или явно установлена в false - светлая тема
                this.disable();
            }
            
            // НЕ слушаем изменения системной темы - пользователь должен сам выбрать
            // Темная тема включается только по явному выбору пользователя
        } catch (error) {
            console.error('Ошибка при инициализации темной темы:', error);
            // В случае ошибки используем светлую тему по умолчанию
            this.disable();
        }
    }
    
    enable() {
        try {
            if (document.body) {
                document.body.classList.add('dark-theme');
            }
            if (localStorage) {
                localStorage.setItem(this.storageKey, 'true');
            }
            this.dispatchEvent(true);
        } catch (error) {
            console.error('Ошибка при включении темной темы:', error);
        }
    }
    
    disable() {
        try {
            if (document.body) {
                document.body.classList.remove('dark-theme');
            }
            if (localStorage) {
                localStorage.setItem(this.storageKey, 'false');
            }
            this.dispatchEvent(false);
        } catch (error) {
            console.error('Ошибка при отключении темной темы:', error);
        }
    }
    
    toggle() {
        if (this.isEnabled()) {
            this.disable();
        } else {
            this.enable();
        }
    }
    
    isEnabled() {
        return document.body.classList.contains('dark-theme');
    }
    
    dispatchEvent(enabled) {
        const event = new CustomEvent('themeChanged', {
            detail: { dark: enabled }
        });
        document.dispatchEvent(event);
    }
}

// Инициализация
const darkThemeManager = new DarkThemeManager();

// Экспорт сразу после инициализации
window.DarkThemeManager = DarkThemeManager;
window.darkThemeManager = darkThemeManager;

// Создаем кнопку переключения темы в бургер-меню
function createThemeToggle() {
    try {
        // Проверяем, что darkThemeManager инициализирован
        if (!darkThemeManager) {
            return;
        }
        
        // Находим все бургер-меню
        const burgerDropdowns = document.querySelectorAll('.burger-dropdown');
        
        if (burgerDropdowns.length === 0) {
            return;
        }
        
        burgerDropdowns.forEach(dropdown => {
            // Проверяем, не добавлена ли уже кнопка
            if (dropdown.querySelector('.theme-toggle-link')) {
                return;
            }
        
        // Создаем элемент кнопки
        const toggleLink = document.createElement('div');
        toggleLink.className = 'burger-link theme-toggle-link';
        toggleLink.setAttribute('role', 'button');
        toggleLink.setAttribute('tabindex', '0');
        toggleLink.setAttribute('aria-label', 'Переключить тему');
        
        const label = document.createElement('span');
        label.textContent = darkThemeManager.isEnabled() ? '☀️ Светлая тема' : '🌙 Темная тема';
        
        const icon = document.createElement('span');
        icon.className = 'icon';
        icon.textContent = darkThemeManager.isEnabled() ? '☀️' : '🌙';
        
        toggleLink.appendChild(label);
        toggleLink.appendChild(icon);
        
        // Функция переключения с анимацией
        const handleToggle = () => {
            // Добавляем класс анимации
            toggleLink.classList.add('animating');
            icon.style.transition = 'transform 0.6s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.3s';
            
            // Переключаем тему
            darkThemeManager.toggle();
            
            // Обновляем текст и иконку с анимацией
            setTimeout(() => {
                // Плавное изменение текста
                label.style.opacity = '0';
                icon.style.opacity = '0';
                
                setTimeout(() => {
                    label.textContent = darkThemeManager.isEnabled() ? '☀️ Светлая тема' : '🌙 Темная тема';
                    icon.textContent = darkThemeManager.isEnabled() ? '☀️' : '🌙';
                    
                    label.style.opacity = '1';
                    icon.style.opacity = '1';
                    
                    // Убираем класс анимации
                    setTimeout(() => {
                        toggleLink.classList.remove('animating');
                        icon.style.transition = '';
                    }, 400);
                }, 150);
            }, 200);
        };
        
        toggleLink.onclick = handleToggle;
        toggleLink.onkeydown = (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                handleToggle();
            }
        };
        
        // Находим разделитель перед "Выход" или добавляем в конец
        const logoutLink = dropdown.querySelector('a[href*="logout"]');
        const usefulLinksTitle = dropdown.querySelector('.burger-section-title');
        const lastDivider = dropdown.querySelectorAll('.burger-divider');
        
        if (logoutLink && logoutLink.previousElementSibling) {
            // Вставляем перед "Выход"
            dropdown.insertBefore(toggleLink, logoutLink);
            // Добавляем разделитель перед кнопкой темы
            const divider = document.createElement('div');
            divider.className = 'burger-divider';
            dropdown.insertBefore(divider, toggleLink);
        } else if (lastDivider.length > 0) {
            // Вставляем после последнего разделителя
            const lastDiv = lastDivider[lastDivider.length - 1];
            dropdown.insertBefore(toggleLink, lastDiv.nextSibling);
        } else {
            // Добавляем в конец
            dropdown.appendChild(toggleLink);
        }
        });
    } catch (error) {
        console.error('Ошибка при создании кнопки темы:', error);
    }
}

// Обновляем кнопки при изменении темы
document.addEventListener('themeChanged', () => {
    const toggles = document.querySelectorAll('.theme-toggle-link');
    toggles.forEach(toggle => {
        const label = toggle.querySelector('span:first-child');
        const icon = toggle.querySelector('.icon');
        if (label && icon) {
            label.textContent = darkThemeManager.isEnabled() ? '☀️ Светлая тема' : '🌙 Темная тема';
            icon.textContent = darkThemeManager.isEnabled() ? '☀️' : '🌙';
        }
    });
});

// Создаем кнопку при загрузке
function initThemeToggle() {
    try {
        createThemeToggle();
    } catch (error) {
        console.error('Ошибка при создании кнопки переключения темы:', error);
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        initThemeToggle();
        // Повторяем через небольшую задержку для бургер-меню, которое может загружаться динамически
        setTimeout(initThemeToggle, 100);
        setTimeout(initThemeToggle, 500);
    });
} else {
    initThemeToggle();
    setTimeout(initThemeToggle, 100);
    setTimeout(initThemeToggle, 500);
}

// Обновляем при динамическом добавлении бургер-меню
if (window.MutationObserver) {
    let isUpdating = false;
    const observer = new MutationObserver((mutations) => {
        // Предотвращаем бесконечный цикл
        if (isUpdating) return;
        
        // Проверяем, были ли добавлены новые бургер-меню
        let shouldUpdate = false;
        mutations.forEach(mutation => {
            if (mutation.addedNodes.length > 0) {
                mutation.addedNodes.forEach(node => {
                    if (node.nodeType === 1) { // Element node
                        if (node.classList && node.classList.contains('burger-dropdown')) {
                            shouldUpdate = true;
                        } else if (node.querySelector && node.querySelector('.burger-dropdown')) {
                            shouldUpdate = true;
                        }
                    }
                });
            }
        });
        
        if (shouldUpdate) {
            isUpdating = true;
            setTimeout(() => {
                createThemeToggle();
                isUpdating = false;
            }, 100);
        }
    });
    
    // Наблюдаем только за изменениями в body, но не за всеми поддеревьями
    if (document.body) {
        observer.observe(document.body, {
            childList: true,
            subtree: false // Изменено на false, чтобы избежать слишком частых обновлений
        });
    }
}

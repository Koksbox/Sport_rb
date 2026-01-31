// Простая аналитика действий пользователя
class AnalyticsManager {
    constructor() {
        this.events = [];
        this.maxEvents = 100; // Максимум событий в памяти
        this.flushInterval = 30000; // Отправка каждые 30 секунд
        this.init();
    }
    
    init() {
        // Отслеживание кликов
        this.trackClicks();
        
        // Отслеживание форм
        this.trackForms();
        
        // Отслеживание навигации
        this.trackNavigation();
        
        // Периодическая отправка данных
        setInterval(() => this.flush(), this.flushInterval);
        
        // Отправка при закрытии страницы
        window.addEventListener('beforeunload', () => this.flush());
    }
    
    track(eventName, properties = {}) {
        const event = {
            name: eventName,
            properties: {
                ...properties,
                timestamp: new Date().toISOString(),
                url: window.location.pathname,
                userAgent: navigator.userAgent
            }
        };
        
        this.events.push(event);
        
        // Ограничиваем размер массива
        if (this.events.length > this.maxEvents) {
            this.events.shift();
        }
        
        // Немедленная отправка для критических событий
        if (this.isCriticalEvent(eventName)) {
            this.sendEvent(event);
        }
    }
    
    trackClicks() {
        document.addEventListener('click', (e) => {
            const target = e.target.closest('a, button, .item-card, .btn');
            if (target) {
                const text = target.textContent?.trim() || target.getAttribute('aria-label') || '';
                const href = target.href || target.getAttribute('href') || '';
                
                this.track('click', {
                    element: target.tagName.toLowerCase(),
                    text: text.substring(0, 50),
                    href: href.substring(0, 100),
                    className: target.className
                });
            }
        });
    }
    
    trackForms() {
        document.addEventListener('submit', (e) => {
            const form = e.target;
            this.track('form_submit', {
                formId: form.id || 'unknown',
                formAction: form.action || window.location.pathname
            });
        });
    }
    
    trackNavigation() {
        // Отслеживание переходов между страницами
        let lastUrl = window.location.pathname;
        
        const observer = new MutationObserver(() => {
            const currentUrl = window.location.pathname;
            if (currentUrl !== lastUrl) {
                this.track('page_view', {
                    path: currentUrl,
                    referrer: lastUrl
                });
                lastUrl = currentUrl;
            }
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
    
    isCriticalEvent(eventName) {
        const criticalEvents = ['form_submit', 'error', 'purchase', 'registration'];
        return criticalEvents.some(ce => eventName.includes(ce));
    }
    
    sendEvent(event) {
        // Отправка события на сервер
        if (navigator.onLine) {
            fetch('/api/analytics/track/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': window.getCookie?.('csrftoken') || ''
                },
                body: JSON.stringify(event)
            }).catch(error => {
                console.warn('Analytics: Failed to send event', error);
            });
        }
    }
    
    flush() {
        if (this.events.length === 0 || !navigator.onLine) {
            return;
        }
        
        const eventsToSend = [...this.events];
        this.events = [];
        
        fetch('/api/analytics/track-batch/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': window.getCookie?.('csrftoken') || ''
            },
            body: JSON.stringify({ events: eventsToSend })
        }).catch(error => {
            console.warn('Analytics: Failed to flush events', error);
            // Возвращаем события обратно в очередь
            this.events.unshift(...eventsToSend);
        });
    }
}

// Инициализация (только если пользователь авторизован)
if (document.body.dataset.userAuthenticated === 'true' || 
    document.querySelector('.nav-menu a[href*="dashboard"]')) {
    const analyticsManager = new AnalyticsManager();
    window.analyticsManager = analyticsManager;
    
    // Глобальная функция для отслеживания
    window.trackEvent = (name, properties) => {
        analyticsManager.track(name, properties);
    };
}

// Экспорт
window.AnalyticsManager = AnalyticsManager;

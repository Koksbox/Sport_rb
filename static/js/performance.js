// Оптимизация производительности
class PerformanceOptimizer {
    constructor() {
        this.debounceTimers = new Map();
        this.throttleTimers = new Map();
        this.init();
    }
    
    init() {
        // Оптимизация изображений
        this.optimizeImages();
        
        // Preload критических ресурсов
        this.preloadCriticalResources();
        
        // Оптимизация скролла
        this.optimizeScroll();
    }
    
    // Debounce функция
    debounce(key, func, delay = 300) {
        if (this.debounceTimers.has(key)) {
            clearTimeout(this.debounceTimers.get(key));
        }
        
        const timer = setTimeout(() => {
            func();
            this.debounceTimers.delete(key);
        }, delay);
        
        this.debounceTimers.set(key, timer);
    }
    
    // Throttle функция
    throttle(key, func, delay = 100) {
        if (this.throttleTimers.has(key)) {
            return;
        }
        
        func();
        this.throttleTimers.set(key, true);
        
        setTimeout(() => {
            this.throttleTimers.delete(key);
        }, delay);
    }
    
    optimizeImages() {
        // Добавляем loading="lazy" ко всем изображениям
        document.querySelectorAll('img:not([loading])').forEach(img => {
            if (!img.hasAttribute('loading')) {
                img.setAttribute('loading', 'lazy');
            }
        });
        
        // Обрабатываем новые изображения
        if (window.MutationObserver) {
            const observer = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    mutation.addedNodes.forEach((node) => {
                        if (node.nodeType === 1 && node.tagName === 'IMG') {
                            if (!node.hasAttribute('loading')) {
                                node.setAttribute('loading', 'lazy');
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
    
    preloadCriticalResources() {
        // Preload критических шрифтов и стилей
        const criticalLinks = [
            { rel: 'preload', href: '/static/css/main.css', as: 'style' },
            { rel: 'preload', href: '/static/js/main.js', as: 'script' }
        ];
        
        criticalLinks.forEach(link => {
            const linkEl = document.createElement('link');
            linkEl.rel = link.rel;
            linkEl.href = link.href;
            linkEl.as = link.as;
            document.head.appendChild(linkEl);
        });
    }
    
    optimizeScroll() {
        // Используем passive listeners для скролла
        let ticking = false;
        
        const optimizedScrollHandler = () => {
            if (!ticking) {
                window.requestAnimationFrame(() => {
                    // Обработка скролла
                    ticking = false;
                });
                ticking = true;
            }
        };
        
        window.addEventListener('scroll', optimizedScrollHandler, { passive: true });
    }
    
    // Виртуальный скролл для больших списков
    createVirtualScroll(container, items, itemHeight, renderItem) {
        const visibleCount = Math.ceil(container.clientHeight / itemHeight) + 2;
        let startIndex = 0;
        
        const render = () => {
            const endIndex = Math.min(startIndex + visibleCount, items.length);
            const visibleItems = items.slice(startIndex, endIndex);
            
            container.innerHTML = '';
            visibleItems.forEach((item, index) => {
                const element = renderItem(item, startIndex + index);
                container.appendChild(element);
            });
        };
        
        container.addEventListener('scroll', () => {
            const newStartIndex = Math.floor(container.scrollTop / itemHeight);
            if (newStartIndex !== startIndex) {
                startIndex = newStartIndex;
                render();
            }
        }, { passive: true });
        
        render();
    }
}

// Инициализация
const performanceOptimizer = new PerformanceOptimizer();

// Экспорт
window.PerformanceOptimizer = PerformanceOptimizer;
window.performanceOptimizer = performanceOptimizer;

// Глобальные функции debounce и throttle
window.debounce = (key, func, delay) => performanceOptimizer.debounce(key, func, delay);
window.throttle = (key, func, delay) => performanceOptimizer.throttle(key, func, delay);

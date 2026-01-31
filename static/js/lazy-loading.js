// Lazy Loading для изображений
class LazyImageLoader {
    constructor() {
        this.imageObserver = null;
        this.init();
    }
    
    init() {
        // Проверяем поддержку Intersection Observer
        if ('IntersectionObserver' in window) {
            this.imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        this.loadImage(img);
                        observer.unobserve(img);
                    }
                });
            }, {
                rootMargin: '50px' // Начинаем загрузку за 50px до появления в viewport
            });
        }
        
        // Обрабатываем все существующие изображения с data-src
        this.processImages();
        
        // Обрабатываем динамически добавленные изображения
        if (window.MutationObserver) {
            const mutationObserver = new MutationObserver(() => {
                this.processImages();
            });
            
            mutationObserver.observe(document.body, {
                childList: true,
                subtree: true
            });
        }
    }
    
    processImages() {
        const images = document.querySelectorAll('img[data-src]');
        images.forEach(img => {
            if (this.imageObserver) {
                this.imageObserver.observe(img);
            } else {
                // Fallback для старых браузеров
                this.loadImage(img);
            }
        });
    }
    
    loadImage(img) {
        const src = img.getAttribute('data-src');
        if (!src) return;
        
        // Показываем placeholder или skeleton
        if (!img.src) {
            img.style.backgroundColor = '#f0f0f0';
            img.style.minHeight = '200px';
        }
        
        const imageLoader = new Image();
        imageLoader.onload = () => {
            img.src = src;
            img.removeAttribute('data-src');
            img.classList.add('loaded');
            img.style.backgroundColor = '';
            img.style.minHeight = '';
        };
        imageLoader.onerror = () => {
            img.src = '/static/images/placeholder.png'; // Fallback изображение
            img.alt = 'Изображение не загружено';
            img.classList.add('error');
        };
        imageLoader.src = src;
    }
}

// Инициализация
const lazyImageLoader = new LazyImageLoader();

// Экспорт
window.LazyImageLoader = LazyImageLoader;
window.lazyImageLoader = lazyImageLoader;

// Cache Manager для кэширования данных на клиенте
class CacheManager {
    constructor() {
        this.prefix = 'sportbash_';
        this.defaultTTL = 5 * 60 * 1000; // 5 минут по умолчанию
    }
    
    _getKey(key) {
        return `${this.prefix}${key}`;
    }
    
    set(key, data, ttl = null) {
        const cacheKey = this._getKey(key);
        const ttlValue = ttl || this.defaultTTL;
        const expiry = Date.now() + ttlValue;
        
        const cacheData = {
            data: data,
            expiry: expiry,
            timestamp: Date.now()
        };
        
        try {
            localStorage.setItem(cacheKey, JSON.stringify(cacheData));
            return true;
        } catch (e) {
            // Если localStorage переполнен, очищаем старые записи
            if (e.name === 'QuotaExceededError') {
                this.clearExpired();
                try {
                    localStorage.setItem(cacheKey, JSON.stringify(cacheData));
                    return true;
                } catch (e2) {
                    console.warn('Cache: Unable to store data', e2);
                    return false;
                }
            }
            return false;
        }
    }
    
    get(key) {
        const cacheKey = this._getKey(key);
        try {
            const cached = localStorage.getItem(cacheKey);
            if (!cached) return null;
            
            const cacheData = JSON.parse(cached);
            
            // Проверяем срок действия
            if (Date.now() > cacheData.expiry) {
                localStorage.removeItem(cacheKey);
                return null;
            }
            
            return cacheData.data;
        } catch (e) {
            console.warn('Cache: Error reading cache', e);
            return null;
        }
    }
    
    has(key) {
        return this.get(key) !== null;
    }
    
    remove(key) {
        const cacheKey = this._getKey(key);
        try {
            localStorage.removeItem(cacheKey);
            return true;
        } catch (e) {
            return false;
        }
    }
    
    clear() {
        const keys = Object.keys(localStorage);
        keys.forEach(key => {
            if (key.startsWith(this.prefix)) {
                localStorage.removeItem(key);
            }
        });
    }
    
    clearExpired() {
        const keys = Object.keys(localStorage);
        const now = Date.now();
        let cleared = 0;
        
        keys.forEach(key => {
            if (key.startsWith(this.prefix)) {
                try {
                    const cached = localStorage.getItem(key);
                    if (cached) {
                        const cacheData = JSON.parse(cached);
                        if (now > cacheData.expiry) {
                            localStorage.removeItem(key);
                            cleared++;
                        }
                    }
                } catch (e) {
                    // Удаляем поврежденные записи
                    localStorage.removeItem(key);
                    cleared++;
                }
            }
        });
        
        return cleared;
    }
    
    // Специализированные методы для разных типов данных
    cacheOrganizations(data, filters = {}) {
        const key = `organizations_${JSON.stringify(filters)}`;
        return this.set(key, data, 10 * 60 * 1000); // 10 минут
    }
    
    getCachedOrganizations(filters = {}) {
        const key = `organizations_${JSON.stringify(filters)}`;
        return this.get(key);
    }
    
    cacheEvents(data, filters = {}) {
        const key = `events_${JSON.stringify(filters)}`;
        return this.set(key, data, 5 * 60 * 1000); // 5 минут
    }
    
    getCachedEvents(filters = {}) {
        const key = `events_${JSON.stringify(filters)}`;
        return this.get(key);
    }
    
    cacheCities(data) {
        return this.set('cities', data, 60 * 60 * 1000); // 1 час
    }
    
    getCachedCities() {
        return this.get('cities');
    }
    
    cacheSports(data) {
        return this.set('sports', data, 60 * 60 * 1000); // 1 час
    }
    
    getCachedSports() {
        return this.get('sports');
    }
}

// Инициализация
const cacheManager = new CacheManager();

// Очистка устаревших записей при загрузке
cacheManager.clearExpired();

// Экспорт
window.CacheManager = CacheManager;
window.cacheManager = cacheManager;

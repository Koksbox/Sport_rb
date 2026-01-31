// Система избранного
class FavoritesManager {
    constructor() {
        this.storageKey = 'sportbash_favorites';
        this.favorites = this.load();
    }
    
    load() {
        try {
            const stored = localStorage.getItem(this.storageKey);
            return stored ? JSON.parse(stored) : {
                organizations: [],
                events: []
            };
        } catch (e) {
            console.warn('Favorites: Error loading favorites', e);
            return { organizations: [], events: [] };
        }
    }
    
    save() {
        try {
            localStorage.setItem(this.storageKey, JSON.stringify(this.favorites));
            return true;
        } catch (e) {
            console.warn('Favorites: Error saving favorites', e);
            return false;
        }
    }
    
    addOrganization(orgId) {
        if (!this.favorites.organizations.includes(orgId)) {
            this.favorites.organizations.push(orgId);
            this.save();
            this.dispatchEvent('organization', orgId, true);
            return true;
        }
        return false;
    }
    
    removeOrganization(orgId) {
        const index = this.favorites.organizations.indexOf(orgId);
        if (index > -1) {
            this.favorites.organizations.splice(index, 1);
            this.save();
            this.dispatchEvent('organization', orgId, false);
            return true;
        }
        return false;
    }
    
    isOrganizationFavorite(orgId) {
        return this.favorites.organizations.includes(orgId);
    }
    
    addEvent(eventId) {
        if (!this.favorites.events.includes(eventId)) {
            this.favorites.events.push(eventId);
            this.save();
            this.dispatchEvent('event', eventId, true);
            return true;
        }
        return false;
    }
    
    removeEvent(eventId) {
        const index = this.favorites.events.indexOf(eventId);
        if (index > -1) {
            this.favorites.events.splice(index, 1);
            this.save();
            this.dispatchEvent('event', eventId, false);
            return true;
        }
        return false;
    }
    
    isEventFavorite(eventId) {
        return this.favorites.events.includes(eventId);
    }
    
    getOrganizations() {
        return [...this.favorites.organizations];
    }
    
    getEvents() {
        return [...this.favorites.events];
    }
    
    dispatchEvent(type, id, isFavorite) {
        const event = new CustomEvent('favoritesChanged', {
            detail: { type, id, isFavorite }
        });
        document.dispatchEvent(event);
    }
    
    // Получить все избранное
    getAll() {
        return {
            organizations: this.getOrganizations(),
            events: this.getEvents()
        };
    }
}

// Инициализация
const favoritesManager = new FavoritesManager();

// Экспорт
window.FavoritesManager = FavoritesManager;
window.favoritesManager = favoritesManager;

// static/js/yandex_maps_city_selector.js
// Компонент для выбора города с автокомплитом и картой Яндекс

class YandexMapsCitySelector {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.options = {
            apiKey: options.apiKey || '',
            onCitySelect: options.onCitySelect || null,
            initialCity: options.initialCity || null,
            initialCoords: options.initialCoords || null, // {lat, lng}
            showMap: options.showMap !== false, // По умолчанию показываем карту
            mapHeight: options.mapHeight || '300px',
            ...options
        };
        
        this.map = null;
        this.geocoder = null;
        this.selectedCity = null;
        this.selectedCoords = null;
        this.suggestView = null;
        
        this.init();
    }
    
    init() {
        const container = document.getElementById(this.containerId);
        if (!container) {
            console.error(`Container #${this.containerId} not found`);
            return;
        }
        
        // Создаём структуру компонента
        container.innerHTML = `
            <div class="yandex-city-selector">
                <div class="form-group" style="position: relative;">
                    <label class="form-label">Город *</label>
                    <input type="text" 
                           class="form-control" 
                           id="${this.containerId}_input" 
                           placeholder="Начните вводить название города, села или деревни"
                           autocomplete="off">
                    <div id="${this.containerId}_suggestions" class="city-suggestions" style="display: none;"></div>
                    <input type="hidden" id="${this.containerId}_city_id" name="city_id">
                    <input type="hidden" id="${this.containerId}_city_name" name="city_name">
                    <input type="hidden" id="${this.containerId}_latitude" name="latitude">
                    <input type="hidden" id="${this.containerId}_longitude" name="longitude">
                </div>
                ${this.options.showMap ? `
                <div class="form-group" style="margin-top: 1rem;">
                    <label class="form-label">Расположение на карте</label>
                    <div id="${this.containerId}_map" style="width: 100%; height: ${this.options.mapHeight}; border-radius: 8px; background: #f0f0f0;"></div>
                    <small style="color: var(--text-light);">Кликните на карте, чтобы указать точное местоположение</small>
                </div>
                ` : ''}
            </div>
        `;
        
        // Инициализируем автокомплит из API
        this.initAutocomplete();
        
        // Инициализируем карту, если нужно
        if (this.options.showMap) {
            this.initMap();
        }
    }
    
    initAutocomplete() {
        const input = document.getElementById(`${this.containerId}_input`);
        const suggestions = document.getElementById(`${this.containerId}_suggestions`);
        let searchTimeout;
        
        input.addEventListener('input', (e) => {
            const query = e.target.value.trim();
            
            clearTimeout(searchTimeout);
            
            if (query.length < 2) {
                suggestions.style.display = 'none';
                return;
            }
            
            searchTimeout = setTimeout(() => {
                this.searchCities(query, suggestions, input);
            }, 300);
        });
        
        // Скрываем подсказки при клике вне поля
        document.addEventListener('click', (e) => {
            if (!input.contains(e.target) && !suggestions.contains(e.target)) {
                suggestions.style.display = 'none';
            }
        });
    }
    
    async searchCities(query, suggestionsContainer, input) {
        try {
            const response = await fetch(`/api/geography/cities/search/?q=${encodeURIComponent(query)}`);
            const results = await response.json();
            
            if (results.length === 0) {
                suggestionsContainer.style.display = 'none';
                return;
            }
            
            suggestionsContainer.innerHTML = '';
            results.forEach(city => {
                const item = document.createElement('div');
                item.className = 'city-suggestion-item';
                item.textContent = city.display_name;
                item.onclick = () => {
                    this.selectCity(city, input);
                    suggestionsContainer.style.display = 'none';
                };
                suggestionsContainer.appendChild(item);
            });
            suggestionsContainer.style.display = 'block';
        } catch (error) {
            console.error('Ошибка поиска городов:', error);
        }
    }
    
    selectCity(city, input) {
        input.value = city.display_name;
        document.getElementById(`${this.containerId}_city_id`).value = city.id;
        document.getElementById(`${this.containerId}_city_name`).value = city.name;
        
        this.selectedCity = city;
        
        // Если есть карта, центрируем на городе
        if (this.map && city.name) {
            this.geocodeCity(city.name);
        }
        
        // Вызываем callback
        if (this.options.onCitySelect) {
            this.options.onCitySelect(city);
        }
    }
    
    initMap() {
        const mapContainer = document.getElementById(`${this.containerId}_map`);
        if (!mapContainer) return;
        
        // Загружаем Яндекс.Карты API
        if (!window.ymaps) {
            const script = document.createElement('script');
            script.src = `https://api-maps.yandex.ru/2.1/?apikey=${this.options.apiKey}&lang=ru_RU`;
            script.onload = () => {
                window.ymaps.ready(() => {
                    this.createMap(mapContainer);
                });
            };
            document.head.appendChild(script);
        } else {
            window.ymaps.ready(() => {
                this.createMap(mapContainer);
            });
        }
    }
    
    createMap(container) {
        // Начальные координаты (Уфа, если не указаны)
        const initialCoords = this.options.initialCoords || [54.7431, 55.9678];
        
        this.map = new window.ymaps.Map(container, {
            center: initialCoords,
            zoom: 12,
            controls: ['zoomControl', 'fullscreenControl']
        });
        
        // Маркер для выбранной точки
        this.marker = new window.ymaps.Placemark(initialCoords, {}, {
            draggable: true,
            preset: 'islands#blueDotIcon'
        });
        
        this.map.geoObjects.add(this.marker);
        
        // Обработчик клика на карте
        this.map.events.add('click', (e) => {
            const coords = e.get('coords');
            this.setCoordinates(coords);
        });
        
        // Обработчик перетаскивания маркера
        this.marker.events.add('dragend', () => {
            const coords = this.marker.geometry.getCoordinates();
            this.setCoordinates(coords);
        });
        
        // Если есть начальные координаты, устанавливаем их
        if (this.options.initialCoords) {
            this.setCoordinates(initialCoords);
        }
    }
    
    async geocodeCity(cityName) {
        if (!window.ymaps || !this.map) return;
        
        try {
            const geocoder = window.ymaps.geocode(cityName + ', Республика Башкортостан');
            geocoder.then((res) => {
                const firstGeoObject = res.geoObjects.get(0);
                if (firstGeoObject) {
                    const coords = firstGeoObject.geometry.getCoordinates();
                    this.map.setCenter(coords, 12);
                    this.setCoordinates(coords);
                }
            });
        } catch (error) {
            console.error('Ошибка геокодирования:', error);
        }
    }
    
    setCoordinates(coords) {
        this.selectedCoords = coords;
        
        // Обновляем маркер
        if (this.marker) {
            this.marker.geometry.setCoordinates(coords);
        }
        
        // Обновляем скрытые поля
        document.getElementById(`${this.containerId}_latitude`).value = coords[0];
        document.getElementById(`${this.containerId}_longitude`).value = coords[1];
        
        // Обратное геокодирование для получения адреса
        if (window.ymaps) {
            window.ymaps.geocode(coords).then((res) => {
                const firstGeoObject = res.geoObjects.get(0);
                if (firstGeoObject) {
                    const address = firstGeoObject.getAddressLine();
                    // Можно обновить поле адреса, если оно есть
                }
            });
        }
    }
    
    getSelectedCity() {
        return {
            id: document.getElementById(`${this.containerId}_city_id`).value,
            name: document.getElementById(`${this.containerId}_city_name`).value,
            display_name: document.getElementById(`${this.containerId}_input`).value
        };
    }
    
    getSelectedCoordinates() {
        return {
            latitude: document.getElementById(`${this.containerId}_latitude`).value,
            longitude: document.getElementById(`${this.containerId}_longitude`).value
        };
    }
}

// Глобальная функция для создания селектора
window.createYandexCitySelector = function(containerId, options) {
    return new YandexMapsCitySelector(containerId, options);
};

// Улучшенная валидация форм
class FormValidator {
    constructor(form) {
        this.form = form;
        this.fields = {};
        this.init();
    }
    
    init() {
        // Находим все поля с валидацией
        const inputs = this.form.querySelectorAll('input[required], textarea[required], select[required]');
        inputs.forEach(input => {
            this.fields[input.name] = {
                element: input,
                group: input.closest('.form-group'),
                label: this.form.querySelector(`label[for="${input.id}"]`) || 
                       this.form.querySelector(`.form-label[for="${input.id}"]`),
                rules: this.getValidationRules(input)
            };
            
            // Добавляем обработчики
            input.addEventListener('blur', () => this.validateField(input.name));
            input.addEventListener('input', () => {
                if (this.fields[input.name].hasError) {
                    this.validateField(input.name);
                }
            });
        });
    }
    
    getValidationRules(input) {
        const rules = {};
        
        if (input.required) {
            rules.required = true;
        }
        
        if (input.type === 'email') {
            rules.email = true;
        }
        
        if (input.type === 'tel') {
            rules.phone = true;
        }
        
        if (input.pattern) {
            rules.pattern = input.pattern;
        }
        
        if (input.minLength) {
            rules.minLength = parseInt(input.minLength);
        }
        
        if (input.maxLength && input.maxLength > 0) {
            const maxLen = parseInt(input.maxLength);
            if (maxLen > 0) {
                rules.maxLength = maxLen;
            }
        }
        
        return rules;
    }
    
    validateField(fieldName) {
        const field = this.fields[fieldName];
        if (!field) return true;
        
        const value = field.element.value.trim();
        const rules = field.rules;
        let isValid = true;
        let errorMessage = '';
        
        // Проверка обязательности
        if (rules.required && !value) {
            isValid = false;
            errorMessage = 'Это поле обязательно для заполнения';
        }
        
        // Проверка email
        if (isValid && rules.email && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                isValid = false;
                errorMessage = 'Введите корректный email адрес';
            }
        }
        
        // Проверка телефона
        if (isValid && rules.phone && value) {
            const phoneRegex = /^(\+7|8|7)?[\d\s\-\(\)]{10,}$/;
            const cleanPhone = value.replace(/\D/g, '');
            if (cleanPhone.length < 10 || cleanPhone.length > 11) {
                isValid = false;
                errorMessage = 'Введите корректный номер телефона';
            }
        }
        
        // Проверка паттерна
        if (isValid && rules.pattern && value) {
            const regex = new RegExp(rules.pattern);
            if (!regex.test(value)) {
                isValid = false;
                errorMessage = 'Неверный формат данных';
            }
        }
        
        // Проверка длины
        if (isValid && rules.minLength && value.length < rules.minLength) {
            isValid = false;
            errorMessage = `Минимальная длина: ${rules.minLength} символов`;
        }
        
        if (isValid && rules.maxLength && rules.maxLength > 0 && value.length > rules.maxLength) {
            isValid = false;
            errorMessage = `Максимальная длина: ${rules.maxLength} символов`;
        }
        
        // Обновляем UI
        this.updateFieldUI(fieldName, isValid, errorMessage);
        
        field.isValid = isValid;
        field.hasError = !isValid;
        
        return isValid;
    }
    
    updateFieldUI(fieldName, isValid, errorMessage) {
        const field = this.fields[fieldName];
        if (!field) return;
        
        const input = field.element;
        const group = field.group;
        
        // Удаляем предыдущие сообщения
        const existingError = group?.querySelector('.form-error');
        const existingSuccess = group?.querySelector('.form-success');
        if (existingError) existingError.remove();
        if (existingSuccess) existingSuccess.remove();
        
        // Удаляем классы
        input.classList.remove('error', 'success');
        group?.classList.remove('has-error', 'has-success');
        
        if (input.value.trim()) {
            if (isValid) {
                input.classList.add('success');
                group?.classList.add('has-success');
            } else {
                input.classList.add('error');
                group?.classList.add('has-error');
                
                // Добавляем сообщение об ошибке
                if (group && errorMessage) {
                    const errorDiv = document.createElement('div');
                    errorDiv.className = 'form-error';
                    errorDiv.textContent = errorMessage;
                    group.appendChild(errorDiv);
                }
            }
        }
    }
    
    validateAll() {
        let isValid = true;
        for (const fieldName in this.fields) {
            if (!this.validateField(fieldName)) {
                isValid = false;
            }
        }
        return isValid;
    }
    
    getErrors() {
        const errors = {};
        for (const fieldName in this.fields) {
            const field = this.fields[fieldName];
            if (field.hasError) {
                errors[fieldName] = field.element.value;
            }
        }
        return errors;
    }
}

// Инициализация валидации для всех форм
function initFormValidation() {
    document.querySelectorAll('form').forEach(form => {
        if (!form.dataset.validatorInitialized) {
            form.validator = new FormValidator(form);
            form.dataset.validatorInitialized = 'true';
            
            // Валидация при отправке
            form.addEventListener('submit', function(e) {
                if (!this.validator.validateAll()) {
                    e.preventDefault();
                    const firstError = Object.keys(this.validator.getErrors())[0];
                    if (firstError) {
                        this.validator.fields[firstError].element.focus();
                        this.validator.fields[firstError].element.scrollIntoView({ 
                            behavior: 'smooth', 
                            block: 'center' 
                        });
                    }
                    return false;
                }
            });
        }
    });
}

// Инициализация при загрузке
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initFormValidation);
} else {
    initFormValidation();
}

// Экспорт
window.FormValidator = FormValidator;
window.initFormValidation = initFormValidation;

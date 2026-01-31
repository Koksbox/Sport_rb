// Система пагинации для списков
class PaginationManager {
    constructor(container, options = {}) {
        this.container = container;
        this.currentPage = options.currentPage || 1;
        this.totalPages = options.totalPages || 1;
        this.total = options.total || 0;
        this.pageSize = options.pageSize || 12;
        this.onPageChange = options.onPageChange || (() => {});
        this.maxVisible = options.maxVisible || 5; // Максимум видимых страниц
    }
    
    render() {
        if (this.totalPages <= 1) {
            this.container.innerHTML = '';
            return;
        }
        
        const pagination = document.createElement('div');
        pagination.className = 'pagination';
        
        // Предыдущая страница
        const prevBtn = document.createElement('button');
        prevBtn.className = 'pagination-btn';
        prevBtn.innerHTML = '← Предыдущая';
        prevBtn.disabled = this.currentPage === 1;
        prevBtn.addEventListener('click', () => {
            if (this.currentPage > 1) {
                this.goToPage(this.currentPage - 1);
            }
        });
        pagination.appendChild(prevBtn);
        
        // Номера страниц
        const pagesContainer = document.createElement('div');
        pagesContainer.className = 'pagination-pages';
        
        const startPage = Math.max(1, this.currentPage - Math.floor(this.maxVisible / 2));
        const endPage = Math.min(this.totalPages, startPage + this.maxVisible - 1);
        
        // Первая страница
        if (startPage > 1) {
            const firstBtn = this.createPageButton(1);
            pagesContainer.appendChild(firstBtn);
            if (startPage > 2) {
                const ellipsis = document.createElement('span');
                ellipsis.className = 'pagination-ellipsis';
                ellipsis.textContent = '...';
                pagesContainer.appendChild(ellipsis);
            }
        }
        
        // Страницы
        for (let i = startPage; i <= endPage; i++) {
            pagesContainer.appendChild(this.createPageButton(i));
        }
        
        // Последняя страница
        if (endPage < this.totalPages) {
            if (endPage < this.totalPages - 1) {
                const ellipsis = document.createElement('span');
                ellipsis.className = 'pagination-ellipsis';
                ellipsis.textContent = '...';
                pagesContainer.appendChild(ellipsis);
            }
            const lastBtn = this.createPageButton(this.totalPages);
            pagesContainer.appendChild(lastBtn);
        }
        
        pagination.appendChild(pagesContainer);
        
        // Следующая страница
        const nextBtn = document.createElement('button');
        nextBtn.className = 'pagination-btn';
        nextBtn.innerHTML = 'Следующая →';
        nextBtn.disabled = this.currentPage === this.totalPages;
        nextBtn.addEventListener('click', () => {
            if (this.currentPage < this.totalPages) {
                this.goToPage(this.currentPage + 1);
            }
        });
        pagination.appendChild(nextBtn);
        
        // Информация о странице
        const info = document.createElement('div');
        info.className = 'pagination-info';
        const start = (this.currentPage - 1) * this.pageSize + 1;
        const end = Math.min(this.currentPage * this.pageSize, this.total);
        info.textContent = `Показано ${start}-${end} из ${this.total}`;
        pagination.appendChild(info);
        
        this.container.innerHTML = '';
        this.container.appendChild(pagination);
    }
    
    createPageButton(page) {
        const btn = document.createElement('button');
        btn.className = 'pagination-page';
        if (page === this.currentPage) {
            btn.classList.add('active');
        }
        btn.textContent = page;
        btn.addEventListener('click', () => this.goToPage(page));
        return btn;
    }
    
    goToPage(page) {
        if (page < 1 || page > this.totalPages || page === this.currentPage) {
            return;
        }
        
        this.currentPage = page;
        this.render();
        this.onPageChange(page);
        
        // Прокрутка вверх
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
    
    update(total, pageSize, currentPage = 1) {
        this.total = total;
        this.pageSize = pageSize;
        this.totalPages = Math.ceil(total / pageSize);
        this.currentPage = Math.min(currentPage, this.totalPages);
        this.render();
    }
}

// Экспорт
window.PaginationManager = PaginationManager;

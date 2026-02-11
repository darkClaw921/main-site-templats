// JavaScript для интерактивности приложения

document.addEventListener('DOMContentLoaded', function() {
    // ==================== Модальное окно ====================
    const modal = document.getElementById('imageModal');
    const modalImg = document.getElementById('modalImage');
    const closeBtn = document.querySelector('.image-modal-close');
    const imageTriggers = document.querySelectorAll('.image-modal-trigger');

    // Открытие модального окна при клике на изображение
    imageTriggers.forEach(function(trigger) {
        trigger.addEventListener('click', function() {
            modal.style.display = 'flex';
            modalImg.src = this.getAttribute('data-image-src');
            modalImg.alt = this.getAttribute('alt');
            document.body.style.overflow = 'hidden'; // Блокируем прокрутку страницы
        });
    });

    // Закрытие модального окна при клике на кнопку закрытия
    if (closeBtn) {
        closeBtn.addEventListener('click', function() {
            modal.style.display = 'none';
            document.body.style.overflow = ''; // Восстанавливаем прокрутку страницы
        });
    }

    // Закрытие модального окна при клике вне изображения
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                modal.style.display = 'none';
                document.body.style.overflow = ''; // Восстанавливаем прокрутку страницы
            }
        });
    }

    // Закрытие модального окна при нажатии Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && modal && modal.style.display === 'flex') {
            modal.style.display = 'none';
            document.body.style.overflow = ''; // Восстанавливаем прокрутку страницы
        }
    });

    // ==================== Табы (навигация в хедере) ====================
    const navTabs = document.querySelectorAll('.nav-tab');
    const tabContents = document.querySelectorAll('.tab-content');

    navTabs.forEach(function(navTab) {
        navTab.addEventListener('click', function(e) {
            // Предотвращаем переход по ссылке только если мы уже на главной
            if (tabContents.length > 0) {
                e.preventDefault();
            }
            var targetTab = this.getAttribute('data-tab');

            // Убираем active у всех навигационных табов
            navTabs.forEach(function(t) { t.classList.remove('active'); });
            tabContents.forEach(function(tc) { tc.classList.remove('active'); });

            // Активируем нужный таб
            this.classList.add('active');
            var targetContent = document.getElementById('tab-' + targetTab);
            if (targetContent) {
                targetContent.classList.add('active');
            }

            // Скроллим к контенту
            var heroSection = document.querySelector('.hero-section');
            if (heroSection) {
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }
        });
    });

    // ==================== Фильтр доработок ====================
    const filters = document.querySelectorAll('.tweak-filter');
    const tweakCards = document.querySelectorAll('.tweak-card');

    filters.forEach(function(filter) {
        filter.addEventListener('click', function() {
            var category = this.getAttribute('data-category');

            // Убираем active у всех фильтров
            filters.forEach(function(f) { f.classList.remove('active'); });
            this.classList.add('active');

            // Показываем/скрываем карточки
            tweakCards.forEach(function(card) {
                if (category === 'all' || card.getAttribute('data-category') === category) {
                    card.style.display = '';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    });
});

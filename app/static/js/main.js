// JavaScript для интерактивности приложения

// Модальное окно для увеличения изображений проектов
document.addEventListener('DOMContentLoaded', function() {
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
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            modal.style.display = 'none';
            document.body.style.overflow = ''; // Восстанавливаем прокрутку страницы
        }
    });

    // Закрытие модального окна при нажатии Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && modal.style.display === 'flex') {
            modal.style.display = 'none';
            document.body.style.overflow = ''; // Восстанавливаем прокрутку страницы
        }
    });
});
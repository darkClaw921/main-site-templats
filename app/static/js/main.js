// JavaScript для интерактивности приложения

document.addEventListener('DOMContentLoaded', function() {
    // ==================== Модальное окно ====================
    const modal = document.getElementById('imageModal');
    const modalImg = document.getElementById('modalImage');
    const closeBtn = document.querySelector('.image-modal-close');
    const imageTriggers = document.querySelectorAll('.image-modal-trigger');

    // Открытие модального окна при клике на изображение
    imageTriggers.forEach(function(trigger) {
        trigger.addEventListener('click', function(e) {
            e.stopPropagation();
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

    // ==================== Анимация переворота карточек доработок ====================
    tweakCards.forEach(function(card) {
        card.addEventListener('click', function() {
            if (card.classList.contains('flipping') || card.classList.contains('flipping-back')) return;

            var isFlipped = card.classList.contains('flipped');
            var inner = card.querySelector('.tweak-card-inner');

            if (!isFlipped) {
                // First click: jump animation + flip to back
                card.classList.add('flipping');

                setTimeout(function() { createCrackParticles(card); }, 1036);

                inner.addEventListener('animationend', function handler() {
                    card.classList.remove('flipping');
                    card.classList.add('flipped');
                    inner.removeEventListener('animationend', handler);
                });
            } else {
                // Second click: jump animation + flip back to front
                card.classList.add('flipping-back');

                setTimeout(function() { createCrackParticles(card); }, 1036);

                inner.addEventListener('animationend', function handler() {
                    card.classList.remove('flipping-back');
                    card.classList.remove('flipped');
                    inner.removeEventListener('animationend', handler);
                });
            }
        });
    });

    function createCrackParticles(card) {
        var rect = card.getBoundingClientRect();
        var centerX = rect.left + rect.width / 2;
        var bottomY = rect.top + rect.height;
        var front = card.querySelector('.tweak-card-front');
        var borderColor = getComputedStyle(front).borderLeftColor;
        var letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
        var particleCount = 14;

        for (var i = 0; i < particleCount; i++) {
            var particle = document.createElement('span');
            particle.className = 'crack-particle';
            particle.textContent = letters.charAt(Math.floor(Math.random() * letters.length));

            // Частицы разлетаются веером из нижней части карточки
            var angle = Math.PI * 0.5 + (Math.random() - 0.5) * Math.PI * 1.4;
            var distance = 70 + Math.random() * 130;
            var x = Math.cos(angle) * distance;
            var y = Math.abs(Math.sin(angle)) * distance;
            var rotation = (Math.random() - 0.5) * 540;
            var fontSize = 0.9 + Math.random() * 1.1;

            particle.style.left = (centerX + (Math.random() - 0.5) * rect.width * 0.6) + 'px';
            particle.style.top = bottomY + 'px';
            particle.style.color = borderColor;
            particle.style.setProperty('--crack-x', x + 'px');
            particle.style.setProperty('--crack-y', y + 'px');
            particle.style.setProperty('--crack-rot', rotation + 'deg');
            particle.style.setProperty('--crack-size', fontSize + 'rem');

            document.body.appendChild(particle);

            (function(p) {
                setTimeout(function() {
                    if (p.parentNode) p.parentNode.removeChild(p);
                }, 1800);
            })(particle);
        }
    }

    // ==================== Переворот карточек проектов ====================
    var projectCards = document.querySelectorAll('.project-card--has-github');

    projectCards.forEach(function(card) {
        card.addEventListener('click', function(e) {
            if (e.target.closest('.image-modal-trigger') || e.target.closest('a')) return;
            card.classList.toggle('flipped');
        });
    });
});

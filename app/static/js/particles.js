// Анимация частиц с буквами для фона сайта
(function() {
    'use strict';

    // Английские буквы A-Z и цифры 0-9
    const letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    
    // Количество частиц
    const particleCount = 50;
    
    // Контейнер для частиц
    let particlesContainer;
    let particles = [];
    let animationId;
    let heroSection = null;

    // Инициализация
    function init() {
        // Проверяем, что body существует
        if (!document.body) {
            setTimeout(init, 100);
            return;
        }

        // Создаем контейнер для частиц
        particlesContainer = document.createElement('div');
        particlesContainer.className = 'particles-background';
        particlesContainer.style.position = 'fixed';
        particlesContainer.style.top = '0';
        particlesContainer.style.left = '0';
        particlesContainer.style.width = '100%';
        particlesContainer.style.height = '100%';
        particlesContainer.style.zIndex = '-1';
        particlesContainer.style.pointerEvents = 'none';
        particlesContainer.style.overflow = 'hidden';
        document.body.appendChild(particlesContainer);

        // Находим элемент hero-section
        heroSection = document.querySelector('.hero-section');
        
        // Создаем частицы
        createParticles();
        
        // Проверяем, что частицы созданы
        if (particles.length === 0) {
            console.warn('Particles not created, retrying...');
            setTimeout(function() {
                createParticles();
                if (particles.length > 0) {
                    animate();
                }
            }, 100);
        } else {
            // Запускаем анимацию
            animate();
        }
        
        // Обработка изменения размера окна
        window.addEventListener('resize', handleResize);
        
        // Обработка скролла для обновления позиции hero-section
        window.addEventListener('scroll', function() {
            // Позиция hero-section обновится в функции animate
        });
    }

    // Создание частиц
    function createParticles() {
        if (!particlesContainer) {
            return;
        }

        const width = window.innerWidth || 1920;
        const height = window.innerHeight || 1080;

        for (let i = 0; i < particleCount; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            
            // Случайная буква
            const letter = letters[Math.floor(Math.random() * letters.length)];
            particle.textContent = letter;
            
            // Случайная позиция
            const x = Math.random() * width;
            const y = Math.random() * height;
            particle.style.left = x + 'px';
            particle.style.top = y + 'px';
            
            // Случайный размер (от 2rem до 4rem для лучшей видимости)
            const size = 2 + Math.random() * 2;
            particle.style.fontSize = size + 'rem';
            
            // Случайная скорость движения (увеличена для лучшей видимости)
            const speedX = (Math.random() - 0.5) * 1.5;
            const speedY = (Math.random() - 0.5) * 1.5;
            
            // Случайная прозрачность (от 0.3 до 0.6 для лучшей видимости)
            const opacity = 0.3 + Math.random() * 0.3;
            particle.style.opacity = opacity;
            particle.style.visibility = 'visible';
            particle.style.display = 'block';
            particle.style.position = 'absolute';
            
            particlesContainer.appendChild(particle);
            
            particles.push({
                element: particle,
                x: x,
                y: y,
                speedX: speedX,
                speedY: speedY,
                size: size
            });
        }
    }

    // Проверка, находится ли частица в области hero-section
    function isParticleInHeroSection(x, y) {
        if (!heroSection) {
            return false;
        }
        
        // getBoundingClientRect возвращает координаты относительно viewport
        const rect = heroSection.getBoundingClientRect();
        
        // Проверяем, находится ли частица в пределах hero-section (координаты относительно viewport)
        return (
            x >= rect.left &&
            x <= rect.right &&
            y >= rect.top &&
            y <= rect.bottom
        );
    }

    // Анимация частиц
    function animate() {
        const width = window.innerWidth;
        const height = window.innerHeight;

        particles.forEach(function(particle) {
            // Обновляем позицию
            particle.x += particle.speedX;
            particle.y += particle.speedY;

            // Отскок от границ
            if (particle.x < 0 || particle.x > width) {
                particle.speedX *= -1;
            }
            if (particle.y < 0 || particle.y > height) {
                particle.speedY *= -1;
            }

            // Ограничиваем позицию в пределах экрана
            particle.x = Math.max(0, Math.min(width, particle.x));
            particle.y = Math.max(0, Math.min(height, particle.y));

            // Применяем новую позицию
            particle.element.style.left = particle.x + 'px';
            particle.element.style.top = particle.y + 'px';
            
            // Проверяем, находится ли частица в области hero-section
            // Если да - устанавливаем z-index выше, чтобы она была поверх hero-section
            if (isParticleInHeroSection(particle.x, particle.y)) {
                // Устанавливаем высокий z-index и position: fixed для частиц в hero-section
                particle.element.style.zIndex = '10';
                particle.element.style.position = 'fixed';
                // Перемещаем частицу из контейнера в body для правильного контекста наложения
                if (particle.element.parentElement === particlesContainer) {
                    document.body.appendChild(particle.element);
                }
            } else {
                particle.element.style.zIndex = '';
                particle.element.style.position = 'absolute';
                // Возвращаем частицу в контейнер, если она была перемещена
                if (particle.element.parentElement === document.body) {
                    particlesContainer.appendChild(particle.element);
                }
            }
        });

        animationId = requestAnimationFrame(animate);
    }

    // Обработка изменения размера окна
    function handleResize() {
        const width = window.innerWidth;
        const height = window.innerHeight;

        particles.forEach(function(particle) {
            // Ограничиваем позицию в пределах нового размера экрана
            particle.x = Math.max(0, Math.min(width, particle.x));
            particle.y = Math.max(0, Math.min(height, particle.y));
        });
    }

    // Запуск при загрузке DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        // Используем setTimeout для гарантии, что body готов
        setTimeout(init, 0);
    }
})();

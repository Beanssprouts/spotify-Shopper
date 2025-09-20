let currentSlide = 0;
let isAutoPlaying = true;
let autoSlideInterval;
const slides = document.querySelectorAll('.slide');
const totalSlides = slides.length;
const slideTime = 4000; // 4 seconds per slide

// Initialize the slideshow
function initSlideShow() {
    updateSlideDisplay();
    updateControlButtons();
    updateProgressBar();
    startAutoSlide();
}

// Update which slide is visible
function updateSlideDisplay() {
    slides.forEach((slide, index) => {
        slide.classList.remove('active', 'prev');
        
        if (index === currentSlide) {
            slide.classList.add('active');
        } else if (index < currentSlide) {
            slide.classList.add('prev');
        }
        
        // Trigger content animation
        const content = slide.querySelector('.slide-content');
        if (index === currentSlide) {
            content.style.animation = 'none';
            setTimeout(() => {
                content.style.animation = 'slideContentIn 1s ease-out';
            }, 10);
        }
    });
}

// Update control button states
function updateControlButtons() {
    const controlBtns = document.querySelectorAll('.control-btn');
    controlBtns.forEach((btn, index) => {
        btn.classList.toggle('active', index === currentSlide);
    });
}

// Update progress bar
function updateProgressBar() {
    const progressBar = document.getElementById('progressBar');
    const progress = ((currentSlide + 1) / totalSlides) * 100;
    progressBar.style.width = `${progress}%`;
}

// Go to specific slide
function goToSlide(slideIndex) {
    if (slideIndex >= 0 && slideIndex < totalSlides) {
        currentSlide = slideIndex;
        updateSlideDisplay();
        updateControlButtons();
        updateProgressBar();
        
        // Reset auto-slide timer
        if (isAutoPlaying) {
            clearInterval(autoSlideInterval);
            startAutoSlide();
        }
    }
}

// Go to next slide
function nextSlide() {
    currentSlide = (currentSlide + 1) % totalSlides;
    updateSlideDisplay();
    updateControlButtons();
    updateProgressBar();
}

// Go to previous slide
function prevSlide() {
    currentSlide = (currentSlide - 1 + totalSlides) % totalSlides;
    updateSlideDisplay();
    updateControlButtons();
    updateProgressBar();
}

// Start auto-sliding
function startAutoSlide() {
    if (isAutoPlaying) {
        autoSlideInterval = setInterval(() => {
            nextSlide();
        }, slideTime);
    }
}

// Stop auto-sliding
function stopAutoSlide() {
    clearInterval(autoSlideInterval);
}

// Toggle auto-slide on/off
function toggleAutoSlide() {
    const playPauseBtn = document.getElementById('playPauseBtn');
    
    if (isAutoPlaying) {
        stopAutoSlide();
        isAutoPlaying = false;
        playPauseBtn.textContent = '▶️';
    } else {
        isAutoPlaying = true;
        startAutoSlide();
        playPauseBtn.textContent = '⏸️';
    }
}

// Reset slideshow to beginning
function resetSlideShow() {
    currentSlide = 0;
    updateSlideDisplay();
    updateControlButtons();
    updateProgressBar();
    
    if (isAutoPlaying) {
        clearInterval(autoSlideInterval);
        startAutoSlide();
    }
}

// Keyboard navigation
document.addEventListener('keydown', (e) => {
    switch(e.key) {
        case 'ArrowRight':
        case ' ':
            e.preventDefault();
            nextSlide();
            if (isAutoPlaying) {
                clearInterval(autoSlideInterval);
                startAutoSlide();
            }
            break;
        case 'ArrowLeft':
            e.preventDefault();
            prevSlide();
            if (isAutoPlaying) {
                clearInterval(autoSlideInterval);
                startAutoSlide();
            }
            break;
        case 'Home':
            e.preventDefault();
            goToSlide(0);
            break;
        case 'End':
            e.preventDefault();
            goToSlide(totalSlides - 1);
            break;
        case 'Escape':
            e.preventDefault();
            toggleAutoSlide();
            break;
    }
});

// Touch/swipe support for mobile
let touchStartX = 0;
let touchEndX = 0;

document.addEventListener('touchstart', (e) => {
    touchStartX = e.changedTouches[0].screenX;
});

document.addEventListener('touchend', (e) => {
    touchEndX = e.changedTouches[0].screenX;
    handleSwipe();
});

function handleSwipe() {
    const swipeThreshold = 50;
    const swipeDistance = touchEndX - touchStartX;
    
    if (Math.abs(swipeDistance) > swipeThreshold) {
        if (swipeDistance > 0) {
            // Swipe right - go to previous slide
            prevSlide();
        } else {
            // Swipe left - go to next slide
            nextSlide();
        }
        
        if (isAutoPlaying) {
            clearInterval(autoSlideInterval);
            startAutoSlide();
        }
    }
}

// Pause auto-slide when window loses focus
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        stopAutoSlide();
    } else if (isAutoPlaying) {
        startAutoSlide();
    }
});

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    initSlideShow();
});

// Smooth progress animation during auto-slide
let progressAnimation;

function animateProgress() {
    const progressBar = document.getElementById('progressBar');
    let startTime;
    const duration = slideTime;
    const startProgress = ((currentSlide) / totalSlides) * 100;
    const endProgress = ((currentSlide + 1) / totalSlides) * 100;
    
    function animate(timestamp) {
        if (!startTime) startTime = timestamp;
        const elapsed = timestamp - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const currentProgress = startProgress + (endProgress - startProgress) * progress;
        progressBar.style.width = `${currentProgress}%`;
        
        if (progress < 1 && isAutoPlaying) {
            progressAnimation = requestAnimationFrame(animate);
        }
    }
    
    if (isAutoPlaying) {
        progressAnimation = requestAnimationFrame(animate);
    }
}

// Update the auto-slide function to include progress animation
function startAutoSlide() {
    if (isAutoPlaying) {
        animateProgress();
        autoSlideInterval = setInterval(() => {
            nextSlide();
            animateProgress();
        }, slideTime);
    }
}
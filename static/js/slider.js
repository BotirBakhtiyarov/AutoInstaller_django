let currentSlide = 0;
let slides;

function showSlide(index) {
    const slidesContainer = document.querySelector('.slides-container');
    slidesContainer.style.transform = `translateX(${-100 * index}%)`;  // Move the slides container
}

function nextSlide() {
    currentSlide = (currentSlide + 1) % slides.length;  // Loop back to the first slide when reaching the end
    showSlide(currentSlide);
}

document.addEventListener('DOMContentLoaded', () => {
    slides = document.querySelectorAll('.slide');
    showSlide(currentSlide);                       // Show the first slide
    setInterval(nextSlide, 3000);                  // Automatically change the slide every 3 seconds
});

// Wait for the DOM to be fully loaded
document.addEventListener("DOMContentLoaded", function () {
    // Enable the carousel functionality for the testimonials
    $('#testimonial-carousel').carousel({
        interval: 5000, // Auto scroll every 5 seconds
        pause: "hover", // Pause carousel on hover
    });

    // Smooth scroll for "Learn More" button (if applicable)
    // const learnMoreBtn = document.querySelector('#learn-more-btn');
    // if (learnMoreBtn) {
    //     learnMoreBtn.addEventListener('click', function (event) {
    //         event.preventDefault();
    //         document.querySelector('#mission-impact').scrollIntoView({
    //             behavior: 'smooth',
    //             block: 'start'
    //         });
    //     });
    // }
});


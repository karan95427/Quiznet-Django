document.addEventListener("DOMContentLoaded", () => {
    // Fade in body
    document.body.style.opacity = 0;
    document.body.style.transition = "opacity 0.8s ease-in-out";
    requestAnimationFrame(() => {
        document.body.style.opacity = 1;
    });

    // Fade background
    const bg = document.querySelector('.fade-bg');
    if (bg) {
        bg.classList.add('visible');
    }

    const bc = document.querySelector('.dashboard-container');
    if (bc) {
        bc.style.opacity = '1';
    }

    // Login/Signup box
    const box = document.querySelector('.login-box');
    if (box) {
        box.style.opacity = '1';
    }

    // 👇 Animate title/logo
    const title = document.querySelector('.dashboard-title');
    if (title) {
        setTimeout(() => {
            title.classList.add('visible');
        }, 100); // delay for smooth entry
    }
});

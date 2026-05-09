document.addEventListener('DOMContentLoaded', function () {
    const navToggle = document.getElementById('nav-toggle');
    const navLinks = document.getElementById('nav-links');

    if (navToggle && navLinks) {
        navToggle.addEventListener('click', function () {
            navLinks.classList.toggle('open');
        });
    }

    const messages = document.querySelectorAll('.messages-wrap .msg');
    if (messages.length) {
        setTimeout(function () {
            messages.forEach(function (message) {
                message.style.opacity = '0';
                setTimeout(function () {
                    message.remove();
                }, 400);
            });
        }, 5000);
    }
});

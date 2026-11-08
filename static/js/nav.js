/* nav.js : the mobile menu. One function opens and closes it, so the button's
   aria-expanded always matches the menu. A link click, a click outside, or
   Escape closes it; Escape also returns focus to the button. */
(function () {
    var button = document.querySelector('.hamburger');
    var menu = document.getElementById('site-menu');
    if (!button || !menu) return;

    function isOpen() {
        return button.getAttribute('aria-expanded') === 'true';
    }

    function setOpen(open) {
        button.setAttribute('aria-expanded', open ? 'true' : 'false');
        button.classList.toggle('active', open);
        menu.classList.toggle('active', open);
    }

    button.addEventListener('click', function (event) {
        event.stopPropagation();
        setOpen(!isOpen());
    });

    menu.querySelectorAll('a').forEach(function (link) {
        link.addEventListener('click', function () { setOpen(false); });
    });

    document.addEventListener('click', function (event) {
        if (isOpen() && !menu.contains(event.target)) setOpen(false);
    });

    document.addEventListener('keydown', function (event) {
        if (event.key === 'Escape' && isOpen()) {
            setOpen(false);
            button.focus();
        }
    });
}());

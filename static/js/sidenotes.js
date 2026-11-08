/* sidenotes.js : sidenote markers. A marker button toggles its note; on narrow
   screens CSS shows only the active note, on wide screens it highlights it.
   Opening one note closes the others, and Escape closes the open note and
   returns focus to its marker. */
(function () {
    var refs = Array.prototype.slice.call(document.querySelectorAll('.sidenote-ref'));
    if (!refs.length) return;

    function setActive(ref, active) {
        ref.classList.toggle('sn-active', active);
        ref.setAttribute('aria-expanded', active ? 'true' : 'false');
    }

    refs.forEach(function (ref) {
        ref.addEventListener('click', function () {
            var open = ref.getAttribute('aria-expanded') !== 'true';
            refs.forEach(function (other) { setActive(other, false); });
            setActive(ref, open);
        });
    });

    document.addEventListener('keydown', function (event) {
        if (event.key !== 'Escape') return;
        var open = refs.filter(function (ref) { return ref.getAttribute('aria-expanded') === 'true'; });
        open.forEach(function (ref) {
            setActive(ref, false);
            ref.focus();
        });
    });
}());

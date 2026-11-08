/* toc.js : the post table of contents. Highlights the section in view and
   shows or hides the list; the toggle exposes its state with aria-expanded. */
(function() {
    var body = document.getElementById('tocBody');
    var toggle = document.getElementById('tocToggle');
    if (!body || !toggle) return;

    var byId = new Map();
    body.querySelectorAll('a[href^="#"]').forEach(function(link) {
        var heading = document.getElementById(link.getAttribute('href').slice(1));
        if (heading) byId.set(heading, link.closest('.toc-item'));
    });

    if (byId.size && 'IntersectionObserver' in window) {
        var observer = new IntersectionObserver(function(entries) {
            var current = null;
            entries.forEach(function(entry) {
                if (entry.isIntersecting) current = entry.target;
            });
            if (!current) return;
            byId.forEach(function(item) { item.classList.remove('toc-active'); });
            byId.get(current).classList.add('toc-active');
        }, { rootMargin: '-80px 0px -60% 0px' });
        byId.forEach(function(item, heading) { observer.observe(heading); });
    }

    toggle.addEventListener('click', function() {
        var collapsed = !body.hidden;
        body.hidden = collapsed;
        toggle.innerHTML = collapsed ? '&#9654;' : '&#9664;';
        toggle.setAttribute('aria-expanded', collapsed ? 'false' : 'true');
        toggle.setAttribute('aria-label', collapsed ? 'Show contents' : 'Hide contents');
    });
})();

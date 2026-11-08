/* toc.js : the post table of contents. Highlights the section in view and
   shows or hides the list; the toggle exposes its state with aria-expanded. */
(function() {
    var toc = document.getElementById('postToc');
    var body = document.getElementById('tocBody');
    var toggle = document.getElementById('tocToggle');
    if (!toc || !body || !toggle) return;

    var links = Array.prototype.slice.call(toc.querySelectorAll('a[href^="#"]'));
    var headings = [];
    var byId = new Map();

    function decodeApostrophes(text) {
        return text
            .replace(/&#39;/g, "'")
            .replace(/&#x27;/g, "'")
            .replace(/&apos;/g, "'")
            .replace(/&amp;#39;/g, "'")
            .replace(/&amp;#x27;/g, "'")
            .replace(/&amp;apos;/g, "'");
    }

    function sanitizeLabel(link) {
        var raw = link.textContent;
        var fixed = decodeApostrophes(raw);
        if (fixed !== raw) {
            link.textContent = fixed;
        }
    }

    function normalizeId(rawId) {
        if (!rawId) return rawId;
        try { return decodeURIComponent(rawId); } catch (e) { return rawId; }
    }

    function clearActive() {
        for (var i = 0; i < links.length; i++) {
            var li = links[i].closest('.toc-item');
            if (li) li.classList.remove('toc-active');
        }
    }

    links.forEach(function(link) {
        var id = link.getAttribute('href').slice(1);
        var el = document.getElementById(id);
        if (!el) return;
        sanitizeLabel(link);
        headings.push({ el: el, link: link });
        byId.set(id, link);
        byId.set(normalizeId(id), link);
    });

    if (headings.length && 'IntersectionObserver' in window) {
        var obs = new IntersectionObserver(function(entries) {
            var best = null;
            for (var i = 0; i < entries.length; i++) {
                if (entries[i].isIntersecting) best = entries[i].target;
            }
            if (!best) return;

            clearActive();
            var active = byId.get(best.id) || byId.get(normalizeId(best.id)) || byId.get(best.getAttribute('id'));
            if (active) {
                var activeItem = active.closest('.toc-item');
                if (activeItem) activeItem.classList.add('toc-active');
            }
        }, { rootMargin: '-80px 0px -60% 0px' });
        for (var i = 0; i < headings.length; i++) {
            obs.observe(headings[i].el);
        }
    }

    toggle.addEventListener('click', function() {
        var collapsed = toc.classList.toggle('toc-collapsed');
        body.style.display = collapsed ? 'none' : '';
        toggle.innerHTML = collapsed ? '&#9654;' : '&#9664;';
        toggle.setAttribute('aria-expanded', collapsed ? 'false' : 'true');
        toggle.setAttribute('aria-label', collapsed ? 'Show contents' : 'Hide contents');
    });
})();

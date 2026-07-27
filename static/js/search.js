/* search.js : client-side search over Zola's elasticlunr index */
(function () {
    var input = document.getElementById('search-input');
    var results = document.getElementById('search-results');
    var hint = document.getElementById('search-hint');
    if (!input || !results || !window.elasticlunr || !window.searchIndex) return;

    var index = elasticlunr.Index.load(window.searchIndex);
    var docs = window.searchIndex.documentStore ? window.searchIndex.documentStore.docs : {};

    function escape(s) {
        return String(s).replace(/[&<>"']/g, function (c) {
            return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
        });
    }

    function titleFor(ref) {
        var d = docs[ref];
        if (d && d.title) return d.title;
        var slug = ref.replace(/\/$/, '').split('/').pop();
        if (!slug) return ref;
        try {
            return decodeURIComponent(slug).replace(/-/g, ' ');
        } catch (e) {
            return slug;
        }
    }

    function safeUrl(ref) {
        var c = ref.charAt(0);
        if (c === '/' || c === '#' || c === '?') return ref;
        var m = /^([a-z][a-z0-9+.\-]*):/i.exec(ref);
        if (m && (m[1].toLowerCase() === 'http' || m[1].toLowerCase() === 'https')) return ref;
        return '';
    }

    function labelFor(ref) {
        if (ref === 'https://eneskemalergin.github.io/' || ref === '/') return 'Home';
        if (ref.indexOf('/blog/') !== -1) return 'Blog';
        if (ref.indexOf('/projects/') !== -1) return 'Projects';
        if (ref.indexOf('/research/') !== -1) return 'Research';
        if (ref.indexOf('/tags/') !== -1) return 'Tag';
        if (ref.indexOf('/news/') !== -1) return 'News';
        if (ref.indexOf('/cv/') !== -1) return 'CV';
        return 'Page';
    }

    function render(query) {
        if (!query.trim()) {
            results.innerHTML = '';
            if (hint) hint.textContent = 'Type to search.';
            return;
        }
        var hits;
        try {
            hits = index.search(query, { expand: true });
        } catch (e) {
            hits = [];
        }
        if (!hits.length) {
            results.innerHTML = '';
            if (hint) hint.textContent = 'No results.';
            return;
        }
        if (hint) hint.textContent = hits.length + ' result' + (hits.length === 1 ? '' : 's');
        var html = '';
        for (var i = 0; i < hits.length; i++) {
            var ref = hits[i].ref;
            var href = safeUrl(ref);
            if (!href) continue;
            html += '<li class="search-item">' +
                '<a href="' + escape(href) + '" class="search-link">' +
                '<span class="search-label">' + escape(labelFor(ref)) + '</span>' +
                '<span class="search-title">' + escape(titleFor(ref)) + '</span>' +
                '</a></li>';
        }
        results.innerHTML = html;
    }

    var timer;
    input.addEventListener('input', function () {
        var q = input.value;
        clearTimeout(timer);
        timer = setTimeout(function () { render(q); }, 80);
    });

    input.focus();
})();
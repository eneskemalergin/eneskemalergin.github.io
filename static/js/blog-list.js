/* blog-list.js : the post list on the blog page and on tag pages. Pages
   through the list five posts at a time, builds the archive sidebar, and on the
   blog page filters by kind. Without JavaScript every post shows and the
   filter row stays hidden. */
(function () {
    var PAGE_SIZE = 5;
    var MONTH_ORDER = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ];

    function escape(s) {
        return String(s).replace(/[&<>"']/g, function (c) {
            return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
        });
    }

    function decodeHtml(text) {
        var ta = document.createElement('textarea');
        ta.innerHTML = String(text || '');
        return ta.value;
    }

    // Whitelist schemes for href values read from data attributes.
    // Anything else (e.g. "javascript:") is dropped before injection.
    function safeUrl(ref) {
        var c = ref.charAt(0);
        if (c === '/' || c === '#' || c === '?') return ref;
        var m = /^([a-z][a-z0-9+.\-]*):/i.exec(ref);
        if (m && (m[1].toLowerCase() === 'http' || m[1].toLowerCase() === 'https')) return ref;
        return '';
    }

    function renderPagination(currentPage, totalPages, onPageChange) {
        var container = document.getElementById('blog-pagination');
        if (!container) return;
        container.hidden = totalPages <= 1;
        if (totalPages <= 1) { container.innerHTML = ''; return; }
        var html = '';
        if (currentPage > 1) {
            html += '<button type="button" class="page-btn" data-page="' + (currentPage - 1) + '" aria-label="Previous page">&larr;</button>';
        }
        for (var i = 1; i <= totalPages; i++) {
            html += '<button type="button" class="page-btn' + (i === currentPage ? ' active" aria-current="page' : '') + '" data-page="' + i + '" aria-label="Page ' + i + '">' + i + '</button>';
        }
        if (currentPage < totalPages) {
            html += '<button type="button" class="page-btn" data-page="' + (currentPage + 1) + '" aria-label="Next page">&rarr;</button>';
        }
        container.innerHTML = html;
        container.querySelectorAll('.page-btn').forEach(function (btn) {
            btn.addEventListener('click', function () {
                onPageChange(parseInt(btn.dataset.page, 10));
            });
        });
    }

    function buildArchive(items) {
        var tree = {};
        items.forEach(function (item) {
            var yr = item.dataset.year;
            var mo = item.dataset.month;
            var title = decodeHtml(item.dataset.title);
            var href = item.dataset.href;
            if (!tree[yr]) tree[yr] = {};
            if (!tree[yr][mo]) tree[yr][mo] = [];
            tree[yr][mo].push({ title: title, href: href });
        });
        var sidebar = document.getElementById('blog-archive');
        if (!sidebar) return;
        var years = Object.keys(tree).sort().reverse();
        if (years.length === 0) { sidebar.innerHTML = '<p class="empty">Nothing here.</p>'; return; }
        var html = '';
        years.forEach(function (yr) {
            html += '<details class="archive-year" open><summary class="archive-year-label">' + escape(yr) + '</summary>';
            var months = Object.keys(tree[yr]);
            months.sort(function (a, b) { return MONTH_ORDER.indexOf(b) - MONTH_ORDER.indexOf(a); });
            months.forEach(function (mo) {
                var count = tree[yr][mo].length;
                html += '<details class="archive-month"><summary class="archive-month-label">' + escape(mo) + ' <span class="archive-count">(' + escape(count) + ')</span></summary>';
                html += '<ul class="archive-list">';
                tree[yr][mo].forEach(function (p) {
                    var href = safeUrl(p.href);
                    if (!href) return;
                    html += '<li><a href="' + escape(href) + '">' + escape(p.title) + '</a></li>';
                });
                html += '</ul></details>';
            });
            html += '</details>';
        });
        sidebar.innerHTML = html;
    }

    function init() {
        var list = document.getElementById('blog-list');
        if (!list) return;
        var allItems = Array.prototype.slice.call(list.querySelectorAll('.blog-item'));
        var filters = Array.prototype.slice.call(document.querySelectorAll('.blog-tab'));
        var currentFilter = 'all';
        var currentPage = 1;

        function filtered() {
            if (currentFilter === 'all') return allItems;
            return allItems.filter(function (item) { return item.dataset.kind === currentFilter; });
        }

        function render() {
            var items = filtered();
            var totalPages = Math.ceil(items.length / PAGE_SIZE);
            allItems.forEach(function (item) { item.style.display = 'none'; });
            var start = (currentPage - 1) * PAGE_SIZE;
            items.slice(start, start + PAGE_SIZE).forEach(function (item) { item.style.display = ''; });
            renderPagination(currentPage, totalPages, function (page) {
                currentPage = page;
                render();
                buildArchive(filtered());
                // Keyboard focus follows the new page instead of the removed button.
                var first = items[(currentPage - 1) * PAGE_SIZE];
                var link = first && first.querySelector('.blog-title a');
                if (link) link.focus({ preventScroll: true });
                list.scrollIntoView({ behavior: 'smooth', block: 'start' });
            });
        }

        filters.forEach(function (btn) {
            btn.addEventListener('click', function () {
                filters.forEach(function (b) {
                    b.classList.toggle('active', b === btn);
                    b.setAttribute('aria-pressed', b === btn ? 'true' : 'false');
                });
                currentFilter = btn.dataset.filter;
                currentPage = 1;
                render();
                buildArchive(filtered());
            });
        });

        render();
        buildArchive(filtered());
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
}());

/* blog-list.js : shared utilities for blog listing and tag pages */
var BlogList = (function () {
    var PAGE_SIZE = 10;
    var MONTH_ORDER = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ];

    function renderPagination(currentPage, totalPages, onPageChange) {
        var container = document.getElementById('blog-pagination');
        if (!container) return;
        if (totalPages <= 1) { container.innerHTML = ''; return; }
        var html = '';
        if (currentPage > 1) {
            html += '<button class="page-btn" data-page="' + (currentPage - 1) + '">&larr;</button>';
        }
        for (var i = 1; i <= totalPages; i++) {
            html += '<button class="page-btn' + (i === currentPage ? ' active' : '') + '" data-page="' + i + '">' + i + '</button>';
        }
        if (currentPage < totalPages) {
            html += '<button class="page-btn" data-page="' + (currentPage + 1) + '">&rarr;</button>';
        }
        container.innerHTML = html;
        container.querySelectorAll('.page-btn').forEach(function (btn) {
            btn.addEventListener('click', function () {
                onPageChange(parseInt(btn.dataset.page));
            });
        });
    }

    function buildArchive(items) {
        var tree = {};
        items.forEach(function (item) {
            var yr = item.dataset.year;
            var mo = item.dataset.month;
            var title = item.dataset.title;
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
            html += '<details class="archive-year" open><summary class="archive-year-label">' + yr + '</summary>';
            var months = Object.keys(tree[yr]);
            months.sort(function (a, b) { return MONTH_ORDER.indexOf(b) - MONTH_ORDER.indexOf(a); });
            months.forEach(function (mo) {
                var count = tree[yr][mo].length;
                html += '<details class="archive-month"><summary class="archive-month-label">' + mo + ' <span class="archive-count">(' + count + ')</span></summary>';
                html += '<ul class="archive-list">';
                tree[yr][mo].forEach(function (p) {
                    html += '<li><a href="' + p.href + '">' + p.title + '</a></li>';
                });
                html += '</ul></details>';
            });
            html += '</details>';
        });
        sidebar.innerHTML = html;
    }

    return { PAGE_SIZE: PAGE_SIZE, renderPagination: renderPagination, buildArchive: buildArchive };
}());

/* search.js : site search over the index that templates/search.html embeds
   as JSON. Every query word must match a record's name, tags, headings,
   summary, or extra text; matches in the name weigh most. The query lives in
   the URL (?q=), so a search can be shared and survives a reload. */
(function () {
    var form = document.querySelector('.search-box');
    var input = document.getElementById('search-input');
    var results = document.getElementById('search-results');
    var hint = document.getElementById('search-hint');
    var data = document.getElementById('search-data');
    if (!form || !input || !results || !data || !window.HtmlSafe) return;

    var MAX_RESULTS = 50;
    var records;
    try {
        records = JSON.parse(data.textContent);
    } catch (e) {
        return;
    }

    // Escaping and URL checks: js/html-safe.js. Record text comes from data
    // files and may hold HTML entities such as &amp;, so it is decoded first.
    var escape = HtmlSafe.escape, safeUrl = HtmlSafe.safeUrl, decodeHtml = HtmlSafe.decodeHtml;

    function normalize(text) {
        return decodeHtml(text).normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
    }

    function words(text) {
        return normalize(text).split(/[^a-z0-9]+/).filter(Boolean);
    }

    // Field weights for an exact word match; a prefix match scores two thirds.
    var FIELDS = [['n', 10], ['k', 6], ['h', 3], ['s', 2], ['x', 1]];

    records.forEach(function (r) {
        r.n = decodeHtml(r.n);
        r.s = decodeHtml(r.s || '');
        r.words = {};
        FIELDS.forEach(function (f) {
            var value = r[f[0]];
            r.words[f[0]] = words(Array.isArray(value) ? value.join(' ') : (value || ''));
        });
    });

    function scoreWord(record, term) {
        var best = 0;
        FIELDS.forEach(function (f) {
            var list = record.words[f[0]];
            for (var i = 0; i < list.length; i++) {
                var w = list[i];
                var s = w === term ? f[1] : (w.indexOf(term) === 0 ? f[1] * 2 / 3 : 0);
                if (s > best) best = s;
            }
        });
        return best;
    }

    // A post whose headings match shows the first matching heading as context.
    function contextFor(record, terms) {
        if (record.s) return record.s;
        var heads = record.h || [];
        for (var i = 0; i < heads.length; i++) {
            var hw = words(heads[i]);
            if (terms.some(function (t) { return hw.some(function (w) { return w.indexOf(t) === 0; }); })) {
                return decodeHtml(heads[i]);
            }
        }
        return '';
    }

    function search(query) {
        var terms = words(query);
        if (!terms.length) return [];
        var hits = [];
        records.forEach(function (r) {
            var total = 0;
            for (var i = 0; i < terms.length; i++) {
                var s = scoreWord(r, terms[i]);
                if (!s) return;
                total += s;
            }
            // A name that is exactly the query outranks names that only contain it.
            if (r.words.n.join(' ') === terms.join(' ')) total += 5;
            hits.push({ record: r, score: total });
        });
        hits.sort(function (a, b) {
            return b.score - a.score || String(b.record.d || '').localeCompare(String(a.record.d || ''));
        });
        return hits.slice(0, MAX_RESULTS).map(function (h) {
            return { record: h.record, context: contextFor(h.record, terms) };
        });
    }

    function render(query) {
        if (!query.trim()) {
            results.innerHTML = '';
            hint.textContent = 'Type to search.';
            return;
        }
        var hits = search(query);
        if (!hits.length) {
            results.innerHTML = '';
            hint.textContent = 'No results.';
            return;
        }
        hint.textContent = hits.length + (hits.length === MAX_RESULTS ? '+' : '') + ' result' + (hits.length === 1 ? '' : 's');
        var html = '';
        hits.forEach(function (hit) {
            var href = safeUrl(hit.record.u);
            if (!href) return;
            html += '<li class="search-item">' +
                '<a href="' + escape(href) + '" class="search-link">' +
                '<span class="search-label">' + escape(hit.record.t) + '</span>' +
                '<span class="search-text">' +
                '<span class="search-title">' + escape(hit.record.n) + '</span>' +
                (hit.context ? '<span class="search-context">' + escape(hit.context) + '</span>' : '') +
                '</span></a></li>';
        });
        results.innerHTML = html;
    }

    function setQuery(query) {
        var url = query ? '?q=' + encodeURIComponent(query) : location.pathname;
        history.replaceState(null, '', url);
    }

    var timer;
    input.addEventListener('input', function () {
        clearTimeout(timer);
        timer = setTimeout(function () {
            render(input.value);
            setQuery(input.value.trim());
        }, 80);
    });

    form.addEventListener('submit', function (event) {
        event.preventDefault();
        clearTimeout(timer);
        render(input.value);
        setQuery(input.value.trim());
    });

    var initial = new URLSearchParams(location.search).get('q');
    if (initial) {
        input.value = initial;
        render(initial);
    }
}());

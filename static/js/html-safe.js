/* html-safe.js : the one boundary for text and URLs that scripts put into
   markup. escape() any text placed inside HTML; safeUrl() any value placed in
   an href, which keeps only site-relative and http(s) URLs, so a value such as
   "javascript:..." is dropped; decodeHtml() turns entities in data text (such
   as &amp;) back into characters before the text is escaped again. */
var HtmlSafe = (function () {
    "use strict";

    function escape(s) {
        return String(s).replace(/[&<>"']/g, function (c) {
            return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
        });
    }

    function safeUrl(ref) {
        var c = ref.charAt(0);
        if (c === '/' || c === '#' || c === '?') return ref;
        var m = /^([a-z][a-z0-9+.\-]*):/i.exec(ref);
        if (m && (m[1].toLowerCase() === 'http' || m[1].toLowerCase() === 'https')) return ref;
        return '';
    }

    function decodeHtml(text) {
        var ta = document.createElement('textarea');
        ta.innerHTML = String(text || '');
        return ta.value;
    }

    return { escape: escape, safeUrl: safeUrl, decodeHtml: decodeHtml };
}());

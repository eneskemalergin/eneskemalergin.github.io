/* research-tabs.js : keyboard-accessible tabs for the Research page.
   The markup holds real tab buttons and one <section> per panel. CSS shows
   the tabs only when <html> has the "js" class (set by theme.js); this script
   adds the tab-panel semantics, the mouse and keyboard behavior, and opens the
   panel that a URL fragment points into. */
(function () {
    "use strict";

    function init() {
        var list = document.querySelector(".research-tabs");
        if (!list) return;
        var tabs = Array.prototype.slice.call(list.querySelectorAll('[role="tab"]'));
        if (!tabs.length) return;

        tabs.forEach(function (tab) {
            var panel = document.getElementById(tab.getAttribute("aria-controls"));
            if (!panel) return;
            panel.setAttribute("role", "tabpanel");
            panel.setAttribute("aria-labelledby", tab.id);
            panel.setAttribute("tabindex", "0");
        });

        function select(tab, moveFocus) {
            tabs.forEach(function (t) {
                var selected = t === tab;
                var panel = document.getElementById(t.getAttribute("aria-controls"));
                t.classList.toggle("active", selected);
                t.setAttribute("aria-selected", selected ? "true" : "false");
                t.setAttribute("tabindex", selected ? "0" : "-1");
                if (panel) panel.classList.toggle("active", selected);
            });
            if (moveFocus) tab.focus();
        }

        // A link to a panel, or to something inside one, opens that panel.
        function showTarget() {
            var id = decodeURIComponent(location.hash.slice(1));
            var target = id && document.getElementById(id);
            var panel = target && target.closest(".research-panel");
            if (!panel) return;
            var tab = tabs.filter(function (t) { return t.getAttribute("aria-controls") === panel.id; })[0];
            if (tab) select(tab, false);
            if (target !== panel) target.scrollIntoView();
        }
        showTarget();
        window.addEventListener("hashchange", showTarget);

        list.addEventListener("click", function (event) {
            var tab = event.target.closest('[role="tab"]');
            if (tab) select(tab, false);
        });

        list.addEventListener("keydown", function (event) {
            var index = tabs.indexOf(document.activeElement);
            if (index < 0) return;
            var next = null;
            if (event.key === "ArrowRight") next = tabs[(index + 1) % tabs.length];
            else if (event.key === "ArrowLeft") next = tabs[(index - 1 + tabs.length) % tabs.length];
            else if (event.key === "Home") next = tabs[0];
            else if (event.key === "End") next = tabs[tabs.length - 1];
            if (!next) return;
            event.preventDefault();
            select(next, true);
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
}());

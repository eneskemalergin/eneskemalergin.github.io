(function () {
    "use strict";

    var storageKey = "eneskemalergin-theme";
    var preferences = ["system", "dark", "light"];
    var html = document.documentElement;
    var mediaQuery = null;
    var preference = "system";

    try {
        if (typeof window.matchMedia === "function") {
            mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
        }
    } catch (error) {
        mediaQuery = null;
    }

    function isValidPreference(value) {
        return preferences.indexOf(value) !== -1;
    }

    function readPreference() {
        try {
            var saved = window.localStorage.getItem(storageKey);
            return isValidPreference(saved) ? saved : "system";
        } catch (error) {
            return "system";
        }
    }

    function prefersDark() {
        return mediaQuery !== null && mediaQuery.matches === true;
    }

    function isDarkMode(value) {
        return value === "dark" || (value === "system" && prefersDark());
    }

    function updateCodeTheme() {
        var codeTheme = document.getElementById("hljs-theme");
        if (!codeTheme) return;
        var lightHref = codeTheme.getAttribute("data-light-href");
        var darkHref = codeTheme.getAttribute("data-dark-href");
        if (!lightHref || !darkHref) return;
        codeTheme.href = isDarkMode(preference) ? darkHref : lightHref;
    }

    function nextPreference() {
        var currentIndex = preferences.indexOf(preference);
        return preferences[(currentIndex + 1) % preferences.length];
    }

    function updateControl() {
        var button = document.querySelector(".theme-toggle");
        if (!button) return;

        var actual = isDarkMode(preference) ? "dark" : "light";
        var next = nextPreference();
        var icon = button.querySelector(".toggle-icon i");
        var iconClass = preference === "system"
            ? "fa-circle-half-stroke"
            : actual === "dark" ? "fa-moon" : "fa-sun";
        var label = "Theme: " + preference + " (" + actual + "). Switch to " + next + ".";

        if (icon) {
            icon.classList.remove("fa-circle-half-stroke", "fa-moon", "fa-sun");
            icon.classList.add(iconClass);
        }
        button.setAttribute("aria-label", label);
        button.setAttribute("title", label);
        button.setAttribute("data-theme-preference", preference);
        updateCodeTheme();
    }

    function applyPreference(value, persist) {
        preference = isValidPreference(value) ? value : "system";
        html.classList.toggle("dark", isDarkMode(preference));
        html.classList.toggle("theme-light", preference === "light");
        html.setAttribute("data-theme-preference", preference);

        if (persist) {
            try {
                window.localStorage.setItem(storageKey, preference);
            } catch (error) {
                // Private browsing or a storage policy may disable persistence.
            }
        }

        updateControl();
    }

    function handleSystemThemeChange() {
        if (preference === "system") {
            applyPreference("system", false);
        }
    }

    applyPreference(readPreference(), false);

    if (mediaQuery !== null) {
        if (typeof mediaQuery.addEventListener === "function") {
            mediaQuery.addEventListener("change", handleSystemThemeChange);
        } else if (typeof mediaQuery.addListener === "function") {
            mediaQuery.addListener(handleSystemThemeChange);
        }
    }

    window.addEventListener("storage", function (event) {
        if (event.key === storageKey) {
            applyPreference(event.newValue || "system", false);
        }
    });

    document.addEventListener("DOMContentLoaded", function () {
        var button = document.querySelector(".theme-toggle");
        if (!button) return;
        updateControl();
        button.addEventListener("click", function () {
            applyPreference(nextPreference(), true);
        });
    });
}());

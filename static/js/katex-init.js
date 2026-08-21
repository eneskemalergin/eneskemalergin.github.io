(function () {
    "use strict";

    document.addEventListener("DOMContentLoaded", function () {
        if (typeof window.renderMathInElement !== "function") return;

        window.renderMathInElement(document.body, {
            delimiters: [
                { left: "$$", right: "$$", display: true },
                { left: "$", right: "$", display: false },
                { left: "\\[", right: "\\]", display: true },
                { left: "\\(", right: "\\)", display: false }
            ]
        });
    });
}());

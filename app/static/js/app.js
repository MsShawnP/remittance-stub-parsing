/**
 * Remittance Stub Parser — Minimal JS for SSE and HTMX support.
 *
 * Lean on HTMX for interactivity. This file handles SSE event
 * processing and PDF viewer toggling that HTMX cannot do alone.
 */

(function () {
    "use strict";

    /**
     * Connect to an SSE endpoint and render progress events.
     *
     * @param {string} url - SSE endpoint URL
     * @param {HTMLElement} targetEl - Container to append progress events into
     * @param {Function} onComplete - Called with parsed result data when done
     */
    function connectSSE(url, targetEl, onComplete) {
        var source = new EventSource(url);

        source.addEventListener("extraction_started", function (e) {
            var data = JSON.parse(e.data);
            appendProgress(targetEl, data.message, false);
        });

        source.addEventListener("tables_found", function (e) {
            var data = JSON.parse(e.data);
            appendProgress(targetEl, data.message, false);
        });

        source.addEventListener("validation_running", function (e) {
            var data = JSON.parse(e.data);
            appendProgress(targetEl, data.message, false);
        });

        source.addEventListener("result_ready", function (e) {
            var data = JSON.parse(e.data);
            appendProgress(targetEl, data.message, true);
            source.close();
            if (typeof onComplete === "function") {
                onComplete(data);
            }
        });

        source.onerror = function () {
            appendProgress(targetEl, "Connection lost", true);
            source.close();
        };

        return source;
    }

    /**
     * Append a progress line to the target container.
     */
    function appendProgress(container, message, isComplete) {
        var div = document.createElement("div");
        div.className = "progress-event";

        var indicator = document.createElement("div");
        indicator.className = "progress-indicator";

        var dot = document.createElement("span");
        dot.className = "progress-dot " + (isComplete ? "dot-complete" : "dot-active");

        var msg = document.createElement("span");
        msg.className = "progress-message";
        msg.textContent = message;

        indicator.appendChild(dot);
        indicator.appendChild(msg);
        div.appendChild(indicator);
        container.appendChild(div);

        // Mark previous dots as complete
        var dots = container.querySelectorAll(".dot-active");
        for (var i = 0; i < dots.length - 1; i++) {
            dots[i].className = "progress-dot dot-complete";
        }
    }

    // Expose connectSSE globally for use in templates
    window.RspApp = {
        connectSSE: connectSSE
    };
})();

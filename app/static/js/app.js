(function () {
    "use strict";

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

        var dots = container.querySelectorAll(".dot-active");
        for (var i = 0; i < dots.length - 1; i++) {
            dots[i].className = "progress-dot dot-complete";
        }
    }

    function initTour() {
        var dataEl = document.getElementById("tour-data");
        if (!dataEl) return;

        var steps = JSON.parse(dataEl.textContent);
        var totalSteps = steps.length;
        var currentStep = 1;
        var completedSteps = {};

        function goToStep(stepNum) {
            currentStep = stepNum;

            document.querySelectorAll(".tour-step-btn").forEach(function (btn) {
                btn.classList.remove("tour-step-active");
                if (parseInt(btn.dataset.step) === stepNum) {
                    btn.classList.add("tour-step-active");
                }
            });

            var step = steps[stepNum - 1];
            var intro = document.getElementById("step-intro");
            intro.innerHTML =
                '<h2 class="tour-step-retailer">' + step.retailer + "</h2>" +
                '<p class="tour-step-desc">' + step.description + "</p>" +
                '<button class="btn btn-primary" id="run-step-btn">Run Pipeline</button>';
            intro.style.display = "block";

            document.getElementById("step-progress").innerHTML = "";
            document.getElementById("step-result").innerHTML = "";

            if (completedSteps[stepNum]) {
                intro.querySelector("#run-step-btn").textContent = "Re-run Pipeline";
            }

            updateNavButtons();
        }

        function runTourStep(stepNum) {
            var step = steps[stepNum - 1];
            var intro = document.getElementById("step-intro");
            var runBtn = intro.querySelector("#run-step-btn");
            runBtn.disabled = true;
            runBtn.textContent = "Processing...";

            var progressEl = document.getElementById("step-progress");
            progressEl.innerHTML = "";

            var resultEl = document.getElementById("step-result");
            resultEl.innerHTML = "";

            connectSSE(
                "/tour/stream/" + step.filename,
                progressEl,
                function (data) {
                    completedSteps[stepNum] = data;

                    fetch("/tour/step/" + stepNum + "/result")
                        .then(function (response) { return response.text(); })
                        .then(function (html) {
                            resultEl.innerHTML = html;
                            runBtn.textContent = "Re-run Pipeline";
                            runBtn.disabled = false;

                            document.getElementById("tour-nav-buttons").classList.remove("is-hidden");
                            updateNavButtons();

                            if (stepNum === totalSteps) {
                                document.getElementById("tour-summary").classList.remove("is-hidden");
                                document.getElementById("next-step-btn").classList.add("is-hidden");
                            }
                        });
                }
            );
        }

        function nextStep() {
            if (currentStep < totalSteps) {
                goToStep(currentStep + 1);
            }
        }

        function prevStep() {
            if (currentStep > 1) {
                goToStep(currentStep - 1);
            }
        }

        function updateNavButtons() {
            var prevBtn = document.getElementById("prev-step-btn");
            var nextBtn = document.getElementById("next-step-btn");

            if (currentStep > 1) {
                prevBtn.classList.remove("is-hidden");
            } else {
                prevBtn.classList.add("is-hidden");
            }
            if (currentStep < totalSteps) {
                nextBtn.classList.remove("is-hidden");
            } else {
                nextBtn.classList.add("is-hidden");
            }
        }

        document.getElementById("tour-nav").addEventListener("click", function (e) {
            var btn = e.target.closest(".tour-step-btn");
            if (btn) goToStep(parseInt(btn.dataset.step));
        });

        document.getElementById("tour-content").addEventListener("click", function (e) {
            if (e.target.closest("#run-step-btn")) {
                runTourStep(currentStep);
            }
        });

        document.getElementById("prev-step-btn").addEventListener("click", prevStep);
        document.getElementById("next-step-btn").addEventListener("click", nextStep);
    }

    function initCaseStudyForm() {
        var form = document.querySelector(".report-selector-form");
        if (!form) return;

        form.addEventListener("submit", function (e) {
            e.preventDefault();
            var checked = document.querySelectorAll("input[name=stub_select]:checked");
            if (checked.length === 0) {
                alert("Select at least one stub.");
                return;
            }
            var names = Array.from(checked).map(function (c) { return c.value; }).join(",");
            window.location.href = "/report?stubs=" + encodeURIComponent(names);
        });
    }

    window.RspApp = { connectSSE: connectSSE };

    document.addEventListener("DOMContentLoaded", function () {
        initTour();
        initCaseStudyForm();
    });
})();

document.addEventListener("DOMContentLoaded", () => {
    const mobileMenuButton = document.getElementById("mobile-menu-button");
    const mobileCloseButton = document.getElementById("mobile-close-button");
    const mobileSidebar = document.getElementById("mobile-sidebar");
    const mobileOverlay = document.getElementById("mobile-overlay");

    if (mobileMenuButton && mobileCloseButton && mobileSidebar && mobileOverlay) {
        const openMobileMenu = () => {
            mobileSidebar.classList.remove("-translate-x-full", "pointer-events-none");
            mobileOverlay.classList.remove("pointer-events-none", "opacity-0");
            mobileMenuButton.setAttribute("aria-expanded", "true");
            document.body.classList.add("overflow-hidden");
        };

        const closeMobileMenu = () => {
            mobileSidebar.classList.add("-translate-x-full", "pointer-events-none");
            mobileOverlay.classList.add("pointer-events-none", "opacity-0");
            mobileMenuButton.setAttribute("aria-expanded", "false");
            document.body.classList.remove("overflow-hidden");
        };

        mobileMenuButton.addEventListener("click", openMobileMenu);
        mobileCloseButton.addEventListener("click", closeMobileMenu);
        mobileOverlay.addEventListener("click", closeMobileMenu);

        mobileSidebar.querySelectorAll("a").forEach((link) => {
            link.addEventListener("click", closeMobileMenu);
        });

        document.addEventListener("keydown", (event) => {
            if (event.key === "Escape") {
                closeMobileMenu();
            }
        });

        window.addEventListener("resize", () => {
            if (window.innerWidth >= 768) {
                closeMobileMenu();
            }
        });
    }

    const form = document.getElementById("prediction-form");
    const submitButton = document.getElementById("submit-button");
    const textarea = document.getElementById("job_text");

    if (form && submitButton) {
        form.addEventListener("submit", () => {
            submitButton.disabled = true;
            submitButton.classList.add("opacity-80", "cursor-not-allowed");

            const buttonLabel = submitButton.querySelector(".button-label");
            const loadingLabel = submitButton.querySelector(".loading-label");

            if (buttonLabel && loadingLabel) {
                buttonLabel.classList.add("hidden");
                loadingLabel.classList.remove("hidden");
            }
        });
    }

    const sampleButtons = document.querySelectorAll("[data-sample]");
    if (textarea && sampleButtons.length) {
        sampleButtons.forEach((button) => {
            button.addEventListener("click", () => {
                textarea.value = button.dataset.sample || "";
                textarea.focus();
                textarea.dispatchEvent(new Event("input", { bubbles: true }));
            });
        });
    }

    if (textarea) {
        const resizeTextarea = () => {
            textarea.style.height = "auto";
            textarea.style.height = `${Math.max(textarea.scrollHeight, 220)}px`;
        };

        const updateCounter = () => {
            const counter = document.getElementById("char-count");
            if (counter) {
                counter.textContent = String(textarea.value.length);
            }
        };

        textarea.addEventListener("input", () => {
            resizeTextarea();
            updateCounter();
        });
        resizeTextarea();
        updateCounter();
    }

    const chartCanvas = document.getElementById("predictionChart");
    if (chartCanvas && window.Chart) {
        const fraudCount = Number(chartCanvas.dataset.fraud || 0);
        const legitimateCount = Number(chartCanvas.dataset.legit || 0);

        new Chart(chartCanvas, {
            type: "doughnut",
            data: {
                labels: ["Fraudulent", "Legitimate"],
                datasets: [{
                    data: [fraudCount, legitimateCount],
                    backgroundColor: ["#c84b47", "#1f8f5f"],
                    hoverBackgroundColor: ["#db6b67", "#33a974"],
                    borderWidth: 0,
                    hoverOffset: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: "62%",
                plugins: {
                    tooltip: {
                        callbacks: {
                            label(context) {
                                return ` ${context.label}: ${context.raw}`;
                            }
                        }
                    },
                    legend: {
                        position: "bottom",
                        labels: {
                            usePointStyle: true,
                            padding: 16,
                            color: "#334155",
                            font: {
                                family: "Nunito",
                                size: 12
                            }
                        }
                    }
                },
                animation: {
                    duration: 500
                }
            }
        });
    }
});

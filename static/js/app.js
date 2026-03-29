document.addEventListener("DOMContentLoaded", () => {
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

        textarea.addEventListener("input", resizeTextarea);
        resizeTextarea();
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
                    backgroundColor: ["#b5473c", "#1c8b58"],
                    hoverBackgroundColor: ["#d86a5d", "#35a46f"],
                    borderWidth: 0,
                    hoverOffset: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: "68%",
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
                            padding: 18,
                            color: "#334155",
                            font: {
                                family: "IBM Plex Sans",
                                size: 12
                            }
                        }
                    }
                },
                animation: {
                    duration: 900
                }
            }
        });
    }
});

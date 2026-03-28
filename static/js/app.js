document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("prediction-form");
    const submitButton = document.getElementById("submit-button");

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
                    backgroundColor: ["#dc4c64", "#1f9d63"],
                    borderWidth: 0,
                    hoverOffset: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: "68%",
                plugins: {
                    legend: {
                        position: "bottom",
                        labels: {
                            usePointStyle: true,
                            padding: 18
                        }
                    }
                }
            }
        });
    }
});

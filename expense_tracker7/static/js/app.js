document.querySelectorAll("form[data-confirm]").forEach((form) => {
  form.addEventListener("submit", (event) => {
    if (!window.confirm(form.dataset.confirm)) {
      event.preventDefault();
    }
  });
});

const moneyTooltip = (context) => {
  const value = Number(context.parsed.y || context.parsed);
  return `$${value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
};

if (window.pennywiseOverview && window.Chart) {
  const canvas = document.getElementById("overviewChart");
  if (canvas) {
    new Chart(canvas, {
      type: "bar",
      data: {
        labels: window.pennywiseOverview.labels,
        datasets: [
          { label: "Income", data: window.pennywiseOverview.income, backgroundColor: "#71bd9d", borderRadius: 5, maxBarThickness: 24 },
          { label: "Expenses", data: window.pennywiseOverview.expenses, backgroundColor: "#f1a08c", borderRadius: 5, maxBarThickness: 24 }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: "bottom", labels: { usePointStyle: true, boxWidth: 7, padding: 18 } }, tooltip: { callbacks: { label: moneyTooltip } } },
        scales: {
          x: { grid: { display: false }, border: { display: false }, ticks: { color: "#90979b" } },
          y: { beginAtZero: true, grid: { color: "#f0f1f0" }, border: { display: false }, ticks: { color: "#90979b", callback: (value) => `$${value}` } }
        }
      }
    });
  }
}

if (window.pennywiseReport && window.Chart) {
  const categoryCanvas = document.getElementById("categoryChart");
  if (categoryCanvas) {
    new Chart(categoryCanvas, {
      type: "doughnut",
      data: {
        labels: window.pennywiseReport.categoryLabels,
        datasets: [{ data: window.pennywiseReport.categoryValues, backgroundColor: ["#6eaa8f", "#efaa7b", "#8581be", "#e9877c", "#62a9b0", "#d0b766", "#a3a9a7"], borderWidth: 0, hoverOffset: 5 }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: "68%",
        plugins: { legend: { position: "bottom", labels: { usePointStyle: true, boxWidth: 7, padding: 16 } }, tooltip: { callbacks: { label: moneyTooltip } } }
      }
    });
  }
  const dailyCanvas = document.getElementById("dailyChart");
  if (dailyCanvas) {
    new Chart(dailyCanvas, {
      type: "line",
      data: {
        labels: window.pennywiseReport.dayLabels,
        datasets: [{ label: "Expenses", data: window.pennywiseReport.dayValues, borderColor: "#6eaa8f", backgroundColor: "rgba(110, 170, 143, .12)", fill: true, tension: .35, pointRadius: 3, pointBackgroundColor: "#6eaa8f" }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false }, tooltip: { callbacks: { label: moneyTooltip } } },
        scales: {
          x: { grid: { display: false }, border: { display: false }, ticks: { color: "#90979b" } },
          y: { beginAtZero: true, grid: { color: "#f0f1f0" }, border: { display: false }, ticks: { color: "#90979b", callback: (value) => `$${value}` } }
        }
      }
    });
  }
}

document.addEventListener("DOMContentLoaded", function () {
    const chartDataElement = document.getElementById("chartDataJSON");
    if (!chartDataElement) return;

    const chartData = JSON.parse(chartDataElement.textContent);

    const labels = chartData.map(data => `${data.topic} (${data.date})`);
    const scores = chartData.map(data => data.score);
    const totals = chartData.map(data => data.total);

    const ctx = document.getElementById('scoreChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Quiz Score',
                data: scores,
                backgroundColor: 'rgba(54, 162, 235, 0.6)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }, {
                label: 'Total Questions',
                data: totals,
                backgroundColor: 'rgba(200, 200, 200, 0.3)',
                borderColor: 'rgba(200, 200, 200, 0.8)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: { beginAtZero: true }
            },
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: 'Your Quiz Scores Over Time'
                }
            }
        }
    });
});

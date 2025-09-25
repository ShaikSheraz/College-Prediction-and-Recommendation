function renderCharts(labels, data) {
    // Horizontal bar chart
    const ctx = document.getElementById('recChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Admission Probability (%)',
                data: data,
                backgroundColor: data.map(p => p>=70 ? 'green' : p>=40 ? 'orange' : 'red')
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            scales: { x: { beginAtZero:true, max:100 } }
        }
    });

    // Pie chart for top 5 colleges
    const pieCtx = document.getElementById('pieChart').getContext('2d');
    new Chart(pieCtx, {
        type: 'pie',
        data: {
            labels: labels.slice(0,5),
            datasets: [{
                data: data.slice(0,5),
                backgroundColor: ['green','blue','orange','red','purple']
            }]
        },
        options: { responsive:true }
    });
}

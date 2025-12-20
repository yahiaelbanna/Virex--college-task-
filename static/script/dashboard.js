var overviewOptions = {
    chart: {
        height: 350,
        type: "area"
    },
    dataLabels: {
        enabled: false
    },
    series: [
        {
            name: "Series 1",
            data: [45, 52, 38, 45, 19, 23, 2]
        },
        {
            name: "Series 2",
            data: [52, 45, 48, 25, 60, 23, 2]
        }
    ],
    fill: {
        type: "gradient",
        gradient: {
            shadeIntensity: 1,
            opacityFrom: 0.7,
            opacityTo: 0.9,
            stops: [0, 90, 100]
        }
    },
    xaxis: {
        categories: [
            "01 Jan",
            "02 Jan",
            "03 Jan",
            "04 Jan",
            "05 Jan",
            "06 Jan",
            "07 Jan"
        ]
    }
};
var socialOptions = {
    series: [44, 55, 41, 17, 15],
    chart: {
        height: 350,
        type: 'donut',
    },
    responsive: [{
        breakpoint: 480,
        options: {
            chart: {
                width: 200
            },
            legend: {
                position: 'bottom'
            }
        }
    }]
};

var overviewChart = new ApexCharts(document.querySelector("#overview"), overviewOptions);
var socialChart = new ApexCharts(document.querySelector("#social"), socialOptions);

overviewChart.render();
socialChart.render();

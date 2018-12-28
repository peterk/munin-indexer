/* eslint-disable object-shorthand */
/* global Chart, CustomTooltips, getStyle, hexToRgba */
/* eslint-disable no-magic-numbers */
// Disable the on-canvas tooltip
Chart.defaults.global.pointHitDetectionRadius = 1;
Chart.defaults.global.tooltips.enabled = true;
Chart.defaults.global.tooltips.mode = 'index';
Chart.defaults.global.tooltips.position = 'nearest';

var mainChart = new Chart($('#main-chart'), {
  type: 'line',
  data: {
    labels: [{{stat_labels}}],
    datasets: [{
      label: 'Warcs created',
      backgroundColor: hexToRgba(getStyle('--info'), 10),
      borderColor: getStyle('--info'),
      pointHoverBackgroundColor: '#fff',
      borderWidth: 2,
      data: [{{warcs_created_last7}}]
    }, {
      label: 'Seed queue',
      backgroundColor: 'transparent',
      borderColor: getStyle('--success'),
      pointHoverBackgroundColor: '#fff',
      borderWidth: 2,
      data: [{{seed_queue_last7}}]
    }, {
      label: 'Post queue',
      yAxisID: 'B',
      backgroundColor: 'transparent',
      borderColor: getStyle('--danger'),
      pointHoverBackgroundColor: '#fff',
      borderWidth: 2,
      data: [{{post_queue_last7}}]
    }]
  },
  options: {
    maintainAspectRatio: false,
    legend: {
      display: true
    },
    scales: {
      xAxes: [{
        gridLines: {
          drawOnChartArea: false
        },
        ticks: {
          maxTicksLimit: 8,
          stepSize: 12,
        },
      }],
      yAxes: [{
        id: 'A',
        ticks: {
          beginAtZero: true,
          maxTicksLimit: 5,
          stepSize: 100,
        }
      },
      {
        id: 'B',
        position: 'right',
      }
    ]
    },
    elements: {
      point: {
        radius: 0,
        hitRadius: 10,
        hoverRadius: 4,
        hoverBorderWidth: 3
      }
    }
  }
});

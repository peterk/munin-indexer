{% autoescape off %}
var chart = bb.generate({
    bindto: '#main-chart',
    data: {
      x: 'hour',
      columns: [
        ['hour', {{stat_labels}}],
        ['Warcs created', {{warcs_created_last7}}],
        ['Post queue (right y)', {{post_queue_last7}}],
        ['Seed queue', {{seed_queue_last7}}],
      ],
      axes: {
        "Warcs created": "y",
        "Seed queue": "y",
        "Post queue (right y)": "y2",
      },
      colors: {
        "Warcs created": "#4fa6d3",
        "Seed queue": "#6666ff",
        "Post queue (right y)": "#ff9999",
      },
      type: 'spline',
      types: {
        "Warcs created": "bar",
      },
      order: 'desc',
    },
    axis: {
      x: {
        type: "category",
        tick: {
          tooltip: true
        },
      },
      y2: {
        show: true
      },
    },
    point: {
        show: false
    },
    spline: {
        classes: [
          "main-chart-line",
          "main-chart-line"
        ]
      },
});
{% endautoescape %}
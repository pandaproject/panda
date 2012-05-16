PANDA.views.Dashboard = Backbone.View.extend({
    initialize: function() {
        _.bindAll(this);
    },

    reset: function(path) {
        this.render();
    },

    render: function() {
        Redd.ajax({
            url: "/dashboard/",
            dataType: "html",
            success: _.bind(function(response) {
                $("#content").html(response);
                this.draw_charts();
            }, this)
        });
    },

    draw_charts: function() {
        var wrapper_width = $("#search-chart-wrapper").width();
        $("#searches-by-day").width(wrapper_width).height(wrapper_width * 2 / 3);

        $.plot($("#searches-by-day"), [window.DASHBOARD.search_data], {
            color: "rgb(255, 0, 0)",
            series: {
                lines: { show: true },
                points: { show: true },
                color: "rgb(255, 0, 0)"
            },
            xaxis: {
                min: 0,
                ticks: window.DASHBOARD.search_ticks
            },
            yaxis: {
                min: 0,
                minTickSize: 1,
                tickDecimals: 0
            },
            grid: {
                borderWidth: 0
            }
        });
        
        wrapper_width = $("#users-chart-wrapper").width();
        $("#users-by-day").width(wrapper_width).height(wrapper_width * 1 / 5);

        $.plot($("#users-by-day"), [window.DASHBOARD.user_data], {
            series: {
                lines: { show: true },
                points: { show: true },
                color: "rgb(255, 0, 0)"
            },
            xaxis: {
                min: 0,
                ticks: window.DASHBOARD.user_ticks
            },
            yaxis: {
                min: 0,
                minTickSize: 1,
                tickDecimals: 0
            },
            grid: {
                borderWidth: 0
            }
        });
    }
});


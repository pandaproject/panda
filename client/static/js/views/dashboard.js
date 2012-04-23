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
            series: {
                bars: { show: true }
            },
            xaxis: {
                ticks: window.DASHBOARD.search_ticks
            }
        });
        
        wrapper_width = $("#users-chart-wrapper").width();
        $("#users-by-day").width(wrapper_width).height(wrapper_width * 1 / 5);

        $.plot($("#users-by-day"), [window.DASHBOARD.user_data], {
            series: {
                bars: { show: true }
            },
            xaxis: {
                ticks: window.DASHBOARD.user_ticks
            }
        });
    }
});


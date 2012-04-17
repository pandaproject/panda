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
            })
        });
    }
});


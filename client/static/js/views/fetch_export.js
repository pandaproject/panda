PANDA.views.FetchExport = Backbone.View.extend({
    el: $("#content"),

    initialize: function() {
        _.bindAll(this);
    },

    reset: function(id) {
        this.render();

        $("#export-download").attr("src", "/api/1.0/export/" + id + "/download/");
    },

    render: function() {
        var context = PANDA.utils.make_context({});

        this.el.html(PANDA.templates.fetch_export(context));
    }
});


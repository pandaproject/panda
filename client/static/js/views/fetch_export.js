PANDA.views.FetchExport = Backbone.View.extend({
    initialize: function() {
        _.bindAll(this);
    },

    reset: function(id) {
        this.render();
        
        PANDA.utils.csrf_download("/api/1.0/export/" + id + "/download/");
    },

    render: function() {
        var context = PANDA.utils.make_context({});

        this.$el.html(PANDA.templates.fetch_export(context));
    }
});


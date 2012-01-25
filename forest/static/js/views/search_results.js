PANDA.views.SearchResults = Backbone.View.extend({
    initialize: function(options) {
        _.bindAll(this);

        this.search = options.search;

        this.collection.bind("reset", this.render);
    },

    render: function() {
        var context = this.collection.meta;
        context["settings"] = PANDA.settings;

        context["query"] = this.search.query,
        context["root_url"] = "#search/" + this.search.query;

        context["pager_unit"] = "dataset";
        context["row_count"] = null;

        context["pager"] = PANDA.templates.pager(context);
        context["datasets"] = this.collection.results();

        this.el.html(PANDA.templates.search_results(context));
    }
});


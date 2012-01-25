PANDA.views.SearchResults = Backbone.View.extend({
    initialize: function(options) {
        _.bindAll(this);

        this.search = options.search;

        this.collection.bind("reset", this.render);
    },

    render: function() {
        var context = PANDA.make_context(this.collection.meta);

        context["query"] = this.search.query,
        context["root_url"] = "#search/" + this.search.query;
        context["pager_unit"] = "dataset";
        context["row_count"] = null;
        context["datasets"] = this.collection.results();

        context["pager"] = PANDA.templates.inline_pager(context);

        this.el.html(PANDA.templates.search_results(context));
    }
});


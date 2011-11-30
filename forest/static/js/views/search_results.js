PANDA.views.SearchResults = Backbone.View.extend({
    template: PANDA.templates.search_results,
    pager_template: PANDA.templates.pager,

    initialize: function(options) {
        _.bindAll(this, "render");

        this.search = options.search;

        this.collection.bind("reset", this.render);
    },

    render: function() {
        context = this.collection.meta;
        context["settings"] = PANDA.settings;

        context["query"] = this.search.query,
        context["root_url"] = "#search/" + this.search.query;

        context["pager"] = this.pager_template(context);
        context["datasets"] = this.collection.results();

        this.el.html(this.template(context));
    }
});


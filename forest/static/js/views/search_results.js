PANDA.views.SearchResults = Backbone.View.extend({
    template: PANDA.templates.search_results,

    initialize: function(options) {
        _.bindAll(this, "render");

        search = options.search;

        this.collection.bind("reset", this.render);
    },

    render: function() {
        results = this.collection.results();
        results['query'] = search.query;
        this.el.html(this.template(results));

        $("a.prev, a.next").click(this.scroll_to_top);
    },

    scroll_to_top: function() {
        window.scrollTo(0, 0);
    }
});


PANDA.views.SearchResults = Backbone.View.extend({
    template: PANDA.templates.search_results,

    events: {
        "click a.prev": "scroll_to_top",
        "click a.next": "scroll_to_top"
    },

    initialize: function(options) {
        _.bindAll(this, "render");

        search = options.search;

        this.collection.bind("reset", this.render);
    },

    render: function() {
        results = this.collection.results();
        results['query'] = search.query;
        console.log(results);
        this.el.html(this.template(results));
    },

    scroll_to_top: function() {
        window.scrollTo(0, this.el.offset());
    }
});


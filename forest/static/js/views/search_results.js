PANDA.views.SearchResults = Backbone.View.extend({
    template: PANDA.templates.search_results,

    events: {
        "click a.prev": "scroll_to_top",
        "click a.next": "scroll_to_top"
    },

    initialize: function() {
        _.bindAll(this, "render");

        this.collection.bind("reset", this.render);
    },

    render: function() {
        this.el.html(this.template(this.collection.results()));
    },

    scroll_to_top: function() {
        window.scrollTo(0, this.el.offset());
    }
});


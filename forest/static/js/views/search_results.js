Redd.views.SearchResults = Backbone.View.extend({
    template: JST.search_results,

    events: {
        "click a.prev": "previous",
        "click a.next": "next"
    },

    initialize: function() {
        _.bindAll(this, "render");

        this.collection.bind("reset", this.render);
    },

    render: function() {
        this.el.html(this.template(this.collection.results()));
    },

    previous: function() {
        this.collection.previous_page();
        return false;
    },

    next: function() {
        this.collection.next_page();
        return false;
    }
});


PANDA.views.DatasetSearch = Backbone.View.extend({
    el: $("#content"),

    template: PANDA.templates.dataset_search,

    events: {
        "submit #dataset-search-form":      "search_event"
    },

    dataset: null,
    query: null,

    initialize: function(options) {
        _.bindAll(this, "render");

        this.results = new PANDA.views.DatasetResults({ search: this });
    },

    reset: function(dataset_id, query) {
        this.query = query;
        
        this.dataset = new PANDA.models.Dataset({ id: dataset_id });
        
        this.dataset.fetch({ success: _.bind(function(model) {
            this.results.set_dataset(this.dataset); 
            this.render();
        }, this) });
    },

    render: function() {
        this.el.html(this.template({ query: this.query, dataset: this.dataset.results() }));
        this.results.el = $("#dataset-search-results");

    },

    search_event: function() {
        this.query = $("#dataset-search-form #dataset-search-query").val();

        window.location = "#dataset/" + this.dataset.get("id") + "/search/" + this.query;

        return false;
    },

    search: function(query, limit, page) {
        this.query = query;

        this.dataset.search(query, limit, page);
    }
});



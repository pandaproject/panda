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
        this.view = new PANDA.views.DatasetView();
    },

    reset: function(dataset_id, query) {
        this.query = query;
        
        this.dataset = new PANDA.models.Dataset({ resource_uri: "/api/1.0/dataset/" + dataset_id + "/" });
        this.dataset.fetch({ success: _.bind(function(model, response) {
            this.results.set_dataset(model);
            this.view.set_dataset(model);
            this.render();
        }, this) });
    },

    render: function() {
        this.el.html(this.template({ query: this.query, dataset: this.dataset.results() }));
        this.results.el = $("#dataset-search-results");
        this.view.el = $("#dataset-search-results");

        if (!this.query) {
            this.view.render();
        }
    },

    search_event: function() {
        this.query = $("#dataset-search-form #dataset-search-query").val();

        window.location = "#dataset/" + this.dataset.get("id") + "/search/" + this.query;

        return false;
    },

    search: function(query, limit, page) {
        this.query = query;

        if (this.query) { 
            this.dataset.search(query, limit, page);
        }
    }
});



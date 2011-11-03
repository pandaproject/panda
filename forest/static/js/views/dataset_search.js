PANDA.views.DatasetSearch = Backbone.View.extend({
    el: $("#content"),

    template: PANDA.templates.dataset_search,

    events: {
        "submit #dataset-search-form":      "search_event"
    },

    dataset: null,
    query: null,

    initialize: function(options) {
        _.bindAll(this, "render", "dataset_changed");

        this.results = new PANDA.views.DatasetResults({ search: this });
    },

    reset: function(dataset_id, query) {
        this.query = query;

        if (this.dataset) {
            this.dataset.unbind();
        }
        
        this.dataset = new PANDA.models.Dataset({ id: dataset_id });
        this.dataset.bind("change", this.dataset_changed);
        
        this.dataset.fetch();
    },

    dataset_changed: function() {
        this.results.set_dataset(this.dataset); 
        this.render();
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



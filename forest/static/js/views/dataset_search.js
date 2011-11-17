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

    reset: function(dataset_id, query, success_callback) {
        this.query = query;
        
        this.dataset = new PANDA.models.Dataset({ resource_uri: PANDA.API + "/dataset/" + dataset_id + "/" });

        this.dataset.fetch({
            async: false,
            success: _.bind(function(model, response) {
                this.results.set_dataset(model);
                this.view.set_dataset(model);
                this.render();
            }, this),
            error: _.bind(function(model, response) {
                if (response.status == 404) {
                    Redd.goto_not_found(); 
                } else {
                    Redd.goto_server_error();
                }
            }, this)
        });
    },

    render: function() {
        this.el.html(this.template({ query: this.query, dataset: this.dataset.results() }));
        this.results.el = $("#dataset-search-results");
        this.view.el = $("#dataset-search-results");

        task = this.dataset.current_task;

        if (task && task.get("task_name") == "redd.tasks.DatasetImportTask") {
            if (task.get("status") == "STARTED") {
                $("#dataset-search-form .alert-message").alert("info block-message", "<p><strong>Import in progress!</strong> This dataset is currently being made searchable. It will not yet appear in search results.</p>Status of import: " + task.get("message") + ".");
            } else if (task.get("status") == "PENDING") {
                $("#dataset-search-form .alert-message").alert("info block-message", "<p><strong>Queued for import!</strong> This dataset is currently waiting to be made searchable. It will not yet appear in search results.</p>");
            } else if (task.get("status") == "FAILURE") {
                $("#dataset-search-form .alert-message").alert("error block-message", '<p><strong>Import failed!</strong> The process to make this dataset searchable failed. It will not appear in search results. <input type="button" class="btn inline" data-controls-modal="dataset-traceback-modal" data-backdrop="true" data-keyboard="true" value="Show detailed error message" /></p>');
            } 
        }
        
        if (!this.query) {
            this.view.render();
        }
    },

    search_event: function() {
        this.query = $("#dataset-search-form #dataset-search-query").val();

        Redd.goto_dataset_search(this.dataset.get("id"), this.query);

        return false;
    },

    search: function(query, limit, page) {
        this.query = query;

        this.dataset.search(query, limit, page);
    }
});



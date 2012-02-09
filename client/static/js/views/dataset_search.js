PANDA.views.DatasetSearch = Backbone.View.extend({
    el: $("#content"),

    events: {
        "submit #dataset-search-form":      "search_event"
    },

    dataset: null,
    query: null,

    initialize: function(options) {
        _.bindAll(this);

        this.results = new PANDA.views.DatasetResults({ search: this });
        this.view = new PANDA.views.DatasetView();
    },

    reset: function(dataset_slug, query, success_callback) {
        this.query = query;
        
        this.dataset = new PANDA.models.Dataset({ resource_uri: PANDA.API + "/dataset/" + dataset_slug + "/" });

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
        // Nuke old modals
        $("#modal-dataset-traceback").remove();

        var context = PANDA.utils.make_context({
            query: this.query,
            dataset: this.dataset.results()
        });

        this.el.html(PANDA.templates.dataset_search(context));
        this.results.el = $("#dataset-search-results");
        this.view.el = $("#dataset-search-results");

        var task = this.dataset.current_task;

        if (task && task.get("task_name").startsWith("panda.tasks.import")) {
            if (task.get("status") == "STARTED") {
                $("#dataset-search .alert").alert_block("alert-info", "Import in progress!", "<p>Data is being made searchable. It will not yet appear in search results.</p><p>Status of import: " + task.get("message") + ".</p>", false);
            } else if (task.get("status") == "PENDING") {
                $("#dataset-search .alert").alert_block("alert-info", "Queued for import!", "<p>Data is waiting to be made searchable. It will not yet appear in search results.</p>", false);
            } else if (task.get("status") == "FAILURE") {
                $("#dataset-search .alert").alert_block("alert-error", "Import failed!", '<p>The process to make data searchable failed. It will not appear in search results. <a href="#modal-dataset-traceback" class="btn inline" data-toggle="modal" data-backdrop="true" data-keyboard="true">Show detailed error message</a></p>', false);
            } 
        }
        
        if (!this.query) {
            this.view.render();
        }

        $('a[rel="popover"]').popover();
    },

    search_event: function() {
        this.query = $("#dataset-search-form #dataset-search-query").val();

        Redd.goto_dataset_search(this.dataset.get("slug"), this.query);

        return false;
    },

    search: function(query, limit, page) {
        this.query = query;

        this.render();
        this.dataset.search(query, limit, page);
    }
});



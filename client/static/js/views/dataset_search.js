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
        this.decode_query(query);

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

        if (task) {
            if (task.get("task_name").startsWith("panda.tasks.import")) {
                if (task.get("status") == "STARTED") {
                    $("#dataset-search .alert").alert_block("alert-info", "Import in progress!", "<p>Data is being made searchable. Search results may be incomplete.</p><p>Status: " + task.get("message") + ".</p>", false);
                } else if (task.get("status") == "PENDING") {
                    $("#dataset-search .alert").alert_block("alert-info", "Queued for import!", "<p>Data is waiting to be made searchable. Search results may be incomplete.</p>", false);
                } else if (task.get("status") == "FAILURE") {
                    $("#dataset-search .alert").alert_block("alert-error", "Import failed!", '<p>The process to make data searchable failed. Search results may be incomplete. <a href="#modal-dataset-traceback" class="btn inline" data-toggle="modal" data-backdrop="true" data-keyboard="true">Show detailed error message</a></p>', false);
                }
            }
            else if (task.get("task_name").startsWith("panda.tasks.reindex")) {
                if (task.get("status") == "STARTED") {
                    $("#dataset-search .alert").alert_block("alert-info", "Reindexing in progress!", "<p>Data is being made searchable. Search results may be incomplete.</p><p>Status: " + task.get("message") + ".</p>", false);
                } else if (task.get("status") == "PENDING") {
                    $("#dataset-search .alert").alert_block("alert-info", "Queued for reindexing!", "<p>Data is waiting to be made searchable. Search results may be incomplete.</p>", false);
                } else if (task.get("status") == "FAILURE") {
                    $("#dataset-search .alert").alert_block("alert-error", "Reindexing failed!", '<p>The process to make data searchable failed. Search results may be incomplete. <a href="#modal-dataset-traceback" class="btn inline" data-toggle="modal" data-backdrop="true" data-keyboard="true">Show detailed error message</a></p>', false);
                }
            }
        }
        
        if (!this.query) {
            this.view.render();
        }

        $('a[rel="popover"]').popover();
    },

    search_event: function() {
        this.query = this.encode_query();

        Redd.goto_dataset_search(this.dataset.get("slug"), this.query);

        return false;
    },

    search: function(query, limit, page) {
        this.decode_query(query);

        console.log(query);
        console.log(this.query);

        console.log("search");
        this.render();
        this.dataset.search(this.query, limit, page);
    },

    encode_query: function() {
        /*
         * Convert arguments from the search fields into a URL. 
         */
        var text = $("#dataset-search-query").val();
        var query = escape(text);

        // for each column search field
        // escape key and value
        // add to query string

        return query;
    },

    decode_query: function(query) {
        /*
         * Parse a query from the URL into form values and a raw query.
         * TODO - set values to forms
         */
        if (query) {
            this.query = "";

            var parts = query.split(/\|/);

            _.each(parts, _.bind(function(p, i) {
                if (i == 0) {
                    this.query = unescape(p);
                } else {
                    column_and_value = p.split(":");
                    this.query += " " + unescape(column_and_value[0]) + ":" + unescape(column_and_value[1]);
                }
            }, this));
        } else {
            this.query = null;
        }
    }
});



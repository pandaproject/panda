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
        this.decode_query_string(query);
        
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
        this.query = this.encode_query_string();

        Redd.goto_dataset_search(this.dataset.get("slug"), this.query);

        return false;
    },

    search: function(query, limit, page) {
        this.decode_query_string(query);

        this.render();
        this.dataset.search(this.make_solr_query(), limit, page);
    },

    encode_query_string: function() {
        /*
         * Convert arguments from the search fields into a URL. 
         */
        var full_text = $("#dataset-search-query").val();
        var query = escape(full_text);

        _.each(this.dataset.get("column_schema"), function(c, i) {
            if (!c["indexed"]) {
                return;
            }

            var value = $("#dataset-column-" + i).val();

            if (value) {
                query += "|" + escape(c["name"]) + ":" + escape(value);
            }
        });

        return query;
    },

    decode_query_string: function(query_string) {
        /*
         * Parse a query from the URL into form values and a query object.
         */
        if (query_string) {
            this.query = {};

            var parts = query_string.split(/\|/);

            _.each(parts, _.bind(function(p, i) {
                if (i == 0) {
                    this.query["__all__"] = unescape(p);
                } else {
                    var column_and_value = p.split(":");
                    var column_name = unescape(column_and_value[0]);
                    var column_value = unescape(column_and_value[1]);

                    this.query[column_name] = column_value;
                }
            }, this));
        } else {
            this.query = null;
        }
    },

    make_solr_query: function() {
        /*
         * Convert the internal query object into a Solr query string.
         */
        if (!this.query) {
            return "";
        }

        var q = this.query["__all__"];

        _.each(this.query, _.bind(function(v, k) {
            if (k == "__all__") {
                return;
            }

            var c = _.find(this.dataset.get("column_schema"), function(c) {
                return c["name"] == k;
            });

            q += " " + c["indexed_name"] + ":" + v;
        }, this));

        return q;
    }
});



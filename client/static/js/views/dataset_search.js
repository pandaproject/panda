PANDA.views.DatasetSearch = Backbone.View.extend({
    el: $("#content"),

    events: {
        "submit #dataset-search-form":      "search_event",
        "click #toggle-advanced-search":    "toggle_advanced_search"
    },

    dataset: null,
    query: null,
    search_filters: null,
    results: null,
    view: null,

    initialize: function(options) {
        _.bindAll(this, "reset", "render", "search_event", "search", "encode_query_string", "decode_query_string", "make_solr_query");

        this.search_filters = new PANDA.views.DatasetSearchFilters({ search: this });
        this.results = new PANDA.views.DatasetResults({ search: this });
        this.view = new PANDA.views.DatasetView();
    },

    reset: function(dataset_slug, query_string, success_callback) {
        this.decode_query_string(query_string);
        
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

        // Render search filters, if enabled for any column
        if (_.any(this.dataset.get("column_schema"), function(c) { return c["indexed"] && c["type"] && c["type"] != "unicode"; })) {
            this.search_filters.el = $("#dataset-search-filters");
            this.search_filters.render();
        }

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
        // Clear any existing error text
        $("#dataset-search-filters .help-wrapper").hide();

        try {
            query_string = this.encode_query_string();
        } catch(e) {
            if (e instanceof PANDA.errors.FilterValidationError) {
                _.each(e.errors, function(message, i) {
                    var filter = $("#filter-" + i);
                
                    // Render error
                    filter.find(".help-wrapper").show();
                    filter.find(".help-inline").text(message);
                });
            } else {
                throw e;
            }

            return false;
        }

        Redd.goto_dataset_search(this.dataset.get("slug"), query_string);

        return false;
    },

    toggle_advanced_search: function() {
        $(".search-help").toggle();
        $("#dataset-search-filters").toggle();

        if ($("#dataset-search-filters").is(":visible")) {
            $("#toggle-advanced-search").text("Fewer search options");
        } else {
            $("#toggle-advanced-search").text("More search options");
        };

        return false;
    },

    search: function(query, limit, page) {
        this.decode_query_string(query);

        this.render();
        this.dataset.search(
            this.make_solr_query(),
            limit,
            page,
            _.bind(function(dataset) {
                this.results.render();
            }, this),
            function() {
                // TODO: error handler
            }
        );
    },

    encode_query_string: function() {
        /*
         * Convert arguments from the search fields into a URL. 
         */
        var full_text = $(".dataset-search-query").val();
        var query = full_text;
        var filters = this.search_filters.encode();

        if (filters) {
            query += "|||" + filters;
        }

        return escape(query);
    },

    decode_query_string: function(query_string) {
        /*
         * Parse a query from the URL into form values and a query object.
         */
        if (query_string) {
            this.query = {};

            var parts = unescape(query_string).split("\|\|\|");

            _.each(parts, _.bind(function(p, i) {
                if (i == 0) {
                    this.query["__all__"] = p;
                } else {
                    var parts = p.split(":::");
                    var column_name = parts[0];
                    var column_operator = parts[1];
                    var column_value = parts[2];
                    var column_range_value = parts[3];

                    this.query[column_name] = { "operator": column_operator, "value": column_value, "range_value": column_range_value };
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

            // Convert datetimes to Solr format
            if (c["type"] == "datetime") {
                v["value"] = v["value"].replace(" ", "T") + ":00Z";
                
                if (v["range_value"]) {
                    v["range_value"] = v["range_value"].replace(" ", "T") + ":00Z";
                }
            } else if (c["type"] == "date") {
                v["value"] = v["value"] + "T00:00:00Z";
                
                if (v["range_value"]) {
                    v["range_value"] = v["range_value"] + "T00:00:00Z";
                }
            } else if (c["type"] == "time") {
                v["value"] = "9999-12-31T" + v["value"] + ":00Z";
                
                if (v["range_value"]) {
                    v["range_value"] = "9999-12-31T" + v["range_value"] + ":00Z";
                }
            }

            if (v["operator"] == "is") {
                q += " AND " + c["indexed_name"] + ':"' + v["value"] + '"';
            } else if (v["operator"] == "is_greater") {
                q += " AND " + c["indexed_name"] + ":[" + v["value"] + " TO *]";
            } else if (v["operator"] == "is_less") {
                q += " AND " + c["indexed_name"] + ":[* TO " + v["value"] + "]";
            } else if (v["operator"] == "is_range") {
                q += " AND " + c["indexed_name"] + ":[" + v["value"] + " TO " + v["range_value"] + "]";
            }
        }, this));

        return q;
    }
});


PANDA.views.DatasetSearch = Backbone.View.extend({
    events: {
        "submit #dataset-search-form":      "search_event",
        "click #toggle-advanced-search":    "toggle_advanced_search"
    },

    dataset: null,
    query: null,
    since: "all",
    search_filters: null,
    results: null,
    view: null,

    text: PANDA.text.DatasetSearch(),

    initialize: function(options) {
        _.bindAll(this, "reset", "render", "search_event", "search", "encode_query_string", "encode_human_readable", "decode_query_string", "make_solr_query");

        this.search_filters = new PANDA.views.DatasetSearchFilters();
        this.results = new PANDA.views.DatasetResults();
        this.view = new PANDA.views.DatasetView();
    },

    reset: function(dataset_slug, query_string, success_callback) {
        this.decode_query_string(query_string);
        this.since = "all";
        
        this.dataset = new PANDA.models.Dataset({ resource_uri: PANDA.API + "/dataset/" + dataset_slug + "/" });

        this.dataset.fetch({
            async: false,
            success: _.bind(function(model, response) {
                this.search_filters.reset(this);
                this.results.reset(this);
                this.view.reset(this.dataset);
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
        var context = PANDA.utils.make_context({
            text: this.text,
            query: this.query,
            dataset: this.dataset.results()
        });

        this.$el.html(PANDA.templates.dataset_search(context));

        this.search_filters.setElement("#dataset-search-filters");
        this.search_filters.render();

        this.results.setElement("#dataset-search-results");
        this.view.setElement("#dataset-search-results");

        var task = this.dataset.current_task;

        if (task) {
            if (task.get("task_name").startsWith("panda.tasks.import")) {
                if (task.get("status") == "STARTED") {
                    var alert_body = interpolate(gettext("<p>This dataset is being made searchable. Search results may be incomplete.</p><p>Status: %(message)s. <a href=\"javascript:location.reload(true)\">Refresh to see updated status &raquo;</a></p>"), { message: task.get("message") }, true);
                    $("#dataset-search .alert").alert_block("alert-info", gettext("Import in progress!"), alert_body, false);
                } else if (task.get("status") == "PENDING") {
                    $("#dataset-search .alert").alert_block("alert-info", gettext("Import queued!"), gettext("<p>This dataset is waiting to be made searchable. Search results may be incomplete. <a href=\"javascript:location.reload(true)\">Refresh to see updated status &raquo;</a</p>"), false);
                } else if (task.get("status") == "FAILURE") {
                    $("#dataset-search .alert").alert_block("alert-error", gettext("Import failed!"), gettext('<p>The process to make this dataset searchable failed. Search results may be incomplete. <a href="#modal-dataset-traceback" class="btn inline" data-toggle="modal" data-backdrop="true" data-keyboard="true">Show detailed error message</a></p>'), false);
                } else if (task.get("status") == "ABORTED") {
                    $("#dataset-search .alert").alert_block("alert-error", gettext("Import aborted!"), gettext('<p>The process to make data searchable was aborted by an administrator. Search results may be incomplete.</p>'), false);
                }
            }
            else if (task.get("task_name").startsWith("panda.tasks.reindex")) {
                if (task.get("status") == "STARTED") {
                    var alert_body = interpolate(gettext("<p>Search data for this dataset is being updated. Search results may be incomplete.</p><p>Status: %(message)s. <a href=\"javascript:location.reload(true)\">Refresh to see updated status &raquo;</a></p>"), { message: task.get("message") }, true);
                    $("#dataset-search .alert").alert_block("alert-info", gettext("Reindexing in progress!"), alert_body, false);
                } else if (task.get("status") == "PENDING") {
                    $("#dataset-search .alert").alert_block("alert-info", gettext("Reindexing queued!"), gettext("<p>This dataset is waiting to have its search data updated. Search results may be incomplete. <a href=\"javascript:location.reload(true)\">Refresh to see updated status &raquo;</a</p>"), false);
                } else if (task.get("status") == "FAILURE") {
                    $("#dataset-search .alert").alert_block("alert-error", gettext("Reindexing failed!"), gettext('<p>The process to make update this dataset\'s search data failed. Search results may be incomplete. <a href="#modal-dataset-traceback" class="btn inline" data-toggle="modal" data-backdrop="true" data-keyboard="true">Show detailed error message</a></p>'), false);
                } else if (task.get("status") == "ABORTED") {
                    $("#dataset-search .alert").alert_block("alert-error", gettext("Reindexing aborted!"), gettext('<p>The process to udpate this dataset\'s search data was aborted by an administrator. Search results may be incomplete.</p>'), false);
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

    slow_query_warning: function() {
        /*
         * Display a warning when a query is taking a very long time to return.
         */
        this.$("#dataset-search-results").html(gettext("<strong>Warning!</strong> This query seems to be taking a very long time. It may still finish or it may have failed."));
    },

    search_error: function(error) {
        /*
         * Display a server error resulting from search.
         */
        this.$("#dataset-search-results").html(interpolate(gettext("<h3>Error executing query!</h3> <p>%(error)s</p>"), { error: error.error_message }, true));
    },

    search: function(query, since, limit, page) {
        /*
         * Execute a search.
         */
        this.decode_query_string(query);
        this.since = since || "all";

        this.render();

        var slow_query_timer = setTimeout(this.slow_query_warning, PANDA.settings.SLOW_QUERY_TIMEOUT);

        this.dataset.search(
            this.make_solr_query(),
            since,
            limit,
            page,
            _.bind(function(dataset) {
                clearTimeout(slow_query_timer);
                this.results.render();
            }, this),
            _.bind(function(dataset, error) {
                clearTimeout(slow_query_timer);
                this.search_error(error);
                
            }, this)
        );
    },

    encode_query_string: function() {
        /*
         * Convert arguments from the search fields into a URL. 
         */
        var full_text = $(".dataset-search-query").val();
        var q = full_text;
        var filters = this.search_filters.encode();

        if (filters) {
            q += "|||" + filters;
        }

        return escape(q);
    },

    encode_human_readable: function() {
        var human = "";
        var full_text = null;
        var parts = [];

        _.each(this.query, function(v, k) {
            if (k == "__all__") {
                if (v) {
                    full_text = interpolate(gettext("Search for <code class=\"full-text\">%(full_text_query)s</code>"), { full_text_query: v }, true);
                }
            } else {
                var column = _.find(this.dataset.get("column_schema"), function(c) {
                    return c["name"] == k;
                });

                var operation_text = this.search_filters.operations[column["type"]][v["operator"]]["name"];
                var value = v["value"];
                var range_value = v["range_value"];

                if (column["type"] == "datetime") {
                    value = moment(value, "YYYY-MM-DD HH:mm:ss").format("YYYY-MM-DD HH:mm")
                } else if (column["type"] == "date") {
                    value = moment(value, "YYYY-MM-DD HH:mm:ss").format("YYYY-MM-DD")
                } else if (column["type"] == "time") {
                    value = moment(value, "YYYY-MM-DD HH:mm:ss").format("HH:mm")
                }

                var part = "<code class=\"column\">" + k + "</code> " + operation_text + " <code class=\"value\">" + value + "</code>";

                if (range_value) {
                    if (column["type"] == "datetime") {
                        range_value = moment(range_value, "YYYY-MM-DD HH:mm:ss").format("YYYY-MM-DD HH:mm")
                    } else if (column["type"] == "date") {
                        range_value = moment(range_value, "YYYY-MM-DD HH:mm:ss").format("YYYY-MM-DD")
                    } else if (column["type"] == "time") {
                        range_value = moment(range_value, "YYYY-MM-DD HH:mm:ss").format("HH:mm")
                    }

                    part += " to <code class=\"value\">" + range_value + "</code>";
                }

                parts.push(part);
            }
        }, this);

        if (full_text) {
            parts.unshift(full_text);
        }

        human = parts.join(" and ");

        return human;
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

            if (q) {
                q += " AND ";
            }

            if (v["operator"] == "is_like") {
                q += c["indexed_name"] + ':(' + v["value"] + ')';
            } else if (v["operator"] == "is") {
                q += c["indexed_name"] + ':"' + v["value"] + '"';
            } else if (v["operator"] == "is_greater") {
                q += c["indexed_name"] + ":[" + v["value"] + " TO *]";
            } else if (v["operator"] == "is_less") {
                q += c["indexed_name"] + ":[* TO " + v["value"] + "]";
            } else if (v["operator"] == "is_range") {
                q += c["indexed_name"] + ":[" + v["value"] + " TO " + v["range_value"] + "]";
            }
        }, this));

        return q;
    }
});


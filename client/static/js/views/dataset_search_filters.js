PANDA.views.DatasetSearchFilters = Backbone.View.extend({
    operations: {
        "int": {
            "is": {
                "name": "is",
                "widget": "single_input",
                "parser": "parse_single_input"
            },
            "is_greater": {
                "name": "is greater than or equal to",
                "widget": "single_input",
                "parser": "parse_single_input"
            },
            "is_less": {
                "name": "is less than or equal to",
                "widget": "single_input",
                "parser": "parse_single_input"
            },
            "is_range": {
                "name": "is in the range",
                "widget": "double_input",
                "parser": "parse_double_input"
            }
        },
        "float": {
            "is": {
                "name": "is",
                "widget": "single_input",
                "parser": "parse_single_input"
            },
            "is_greater": {
                "name": "is greater than or equal to",
                "widget": "single_input",
                "parser": "parse_single_input"
            },
            "is_less": {
                "name": "is less than or equal to",
                "widget": "single_input",
                "parser": "parse_single_input"
            },
            "is_range": {
                "name": "is in the range",
                "widget": "single_input",
                "parser": "parse_single_input"
            }
        },
        "bool": {
            "is": {
                "name": "is",
                "widget": "single_input",
                "parser": "parse_single_input"
            }
        },
        "datetime": {
            "is": {
                "name": "is",
                "widget": "single_input",
                "parser": "parse_single_input"
            },
            "is_greater": {
                "name": "is on or after",
                "widget": "single_input",
                "parser": "parse_single_input"
            },
            "is_less": {
                "name": "is on or before",
                "widget": "single_input",
                "parser": "parse_single_input"
            },
            "is_range": {
                "name": "is in the range",
                "widget": "single_input",
                "parser": "parse_single_input"
            }
        },
        "date": {
            "is": {
                "name": "is",
                "widget": "single_input",
                "parser": "parse_single_input"
            },
            "is_greater": {
                "name": "is on or after",
                "widget": "single_input",
                "parser": "parse_single_input"
            },
            "is_less": {
                "name": "is on or before",
                "widget": "single_input",
                "parser": "parse_single_input"
            },
            "is_range": {
                "name": "is in the range",
                "widget": "single_input",
                "parser": "parse_single_input"
            }
        },
        "time": {
            "is": {
                "name": "is",
                "widget": "single_input",
                "parser": "parse_single_input"
            },
            "is_greater": {
                "name": "is at or after",
                "widget": "single_input",
                "parser": "parse_single_input"
            },
            "is_less": {
                "name": "is at or before",
                "widget": "single_input",
                "parser": "parse_single_input"
            },
            "is_range": {
                "name": "is in the range",
                "widget": "single_input",
                "parser": "parse_single_input"
            }
        }
    },

    widgets: {
        "single_input": '<input value="<%= value %>" />',
        "double_input": '<input value="<%= value %>" /> to <input value="<%= range_value %>" />'
    },

    el: null,

    search: null,
    dataset: null,

    initialize: function(options) {
        _.bindAll(this);

        this.search = options.search;

        _.each(this.widgets, _.bind(function(v, k) {
            this.widgets[k] = _.template(v);
        }, this));
    },

    set_dataset: function(dataset) {
        this.dataset = dataset;
    },

    render: function() {
        var context = PANDA.utils.make_context({
            "dataset": this.dataset.results(),
            "render_filter": this.render_filter
        });

        this.el.html(PANDA.templates.dataset_search_filters(context));

        _.each(this.dataset.get("column_schema"), _.bind(function(c, i) {
            if (this.column_is_filterable(c) && this.column_has_query(c)) {
                $("#filter-" + i).show();
            }
        }, this));

        $("#add-filter").change(this.add_filter);
        $(".operator").change(this.change_operator);
        $(".remove-filter").click(this.remove_filter);
    },

    column_is_filterable: function(c) {
        /*
         * Determine if a column is filterable.
         */
        return c["indexed"] && c["type"] && c["type"] != "unicode";
    },

    column_has_query: function(c) {
        /*
         * Determine if a column has a current value.
         */
        return this.search.query && this.search.query[c["name"]];
    },

    render_filter: function(c) {
        /*
         * Render a single column filter to a string.
         */
        var query = this.get_column_query(c);
        var operation = this.get_column_operation(c, query);
        var operations = this.get_column_operations(c);
        var widget = this.get_column_widget(operation);

        filter_context = PANDA.utils.make_context({
            "column": c,
            "query": query,
            "operation": operation,
            "operations": operations,
            "widget": widget
        });
        
        return PANDA.templates.inline_search_filter(filter_context);    
    },

    get_column_query: function(c) {
        /*
         * Fetch a column's query or return a default query data structure.
         */
        if (this.column_has_query(c)) {
            return this.search.query[c["name"]];
        } else {
            return { "operator": "is", "value": "", "range_value": "" };
        }
    },

    get_column_operation: function(c, q) {
        /*
         * Fetch an operation object based a column's type and currently
         * selected operation.
         */
        console.log(c);
        console.log(q);
        console.log(this.operations);
        console.log(this.operations[c["type"]]);
        return this.operations[c["type"]][q["operator"]];
    },

    get_column_operations: function(c) {
        /*
         * Get a list of all possible operations for a given column's type.
         */
        return this.operations[c["type"]];
    },

    get_column_widget: function(column_operation) {
        /*
         * Get an appropriate widget template based on a column's operation.
         */
        return this.widgets[column_operation["widget"]]
    },

    add_filter: function() {
        /*
         * Add a column filter.
         */
        var i = $("#add-filter").val();
        var filter = $("#filter-" + i);

        if (filter.is(":hidden")) {
            var c = this.dataset.get("column_schema")[i];

            filter.html(this.render_filter(c));
            filter.show();

            filter.find(".operator").change(this.change_operator);
            filter.find(".remove-filter").click(this.remove_filter);
        }
        
        $("#add-filter").val("");
    },

    change_operator: function(e) {
        /*
         * When the selected operation is changed, update to use the new widget.
         */
        var last_op = $(e.currentTarget).data("last-value");
        var new_op = $(e.currentTarget).val();

        var filter = $(e.currentTarget).parents(".filter");
        var filter_id = filter.data("filter-id");
        var c = this.dataset.get("column_schema")[filter_id];

        var column_query = this.get_column_query(c); 
        var last_operation = this.get_column_operation(c, column_query);
        column_query["operator"] = new_op;
        var column_operation = this.get_column_operation(c, column_query);

        // Parse values before swapping widgets, so they will be carried over
        var values = this[last_operation["parser"]](filter);
        $.extend(column_query, values);

        filter.find(".widget").html(this.get_column_widget(column_operation)(column_query));

        $(e.currentTarget).data("last-value", new_op);
    },

    remove_filter: function(e) {
        /*
         * Remove a column filter.
         */
        $(e.currentTarget).parents(".filter").hide();
        $(e.currentTarget).parents(".filter").empty();
    },

    encode: function() {
        /*
         * Encode selected filters into query string format.
         */
        var terms = [];

        _.each(this.dataset.get("column_schema"), _.bind(function(c, i) {
            if (!c["indexed"] || !c["type"] || c["type"] == "unicode") {
                return;
            }

            var filter = $("#filter-" + i);

            if (filter.is(":hidden")) {
                return;
            }

            var operator = filter.find(".operator").val();
            var parser = this.operations[c["type"]][operator]["parser"];
            var values = this[parser](filter);

            if (values["value"]) {
                terms.push(c["name"] + ":::" + operator + ":::" + values["value"] + ":::" + values["range_value"]);
            }
        }, this));

        return terms.join("|||");
    },

    /* Value parsers */

    parse_single_input: function(filter) {
        return { "value": filter.find("input").val(), "range_value": "" };
    },
    
    parse_double_input: function(filter) {
        var values = filter.find("input").val();
        return { "value": values[0], "range_value": values[1] };
    }
});


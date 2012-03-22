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
        var context = PANDA.utils.make_context({});
        
        context["operations"] = this.operations;
        context["widgets"] = this.widgets;
        context["dataset"] = this.dataset.results();
        context["query"] = this.search.query;

        var prerendered_filters = {};

        _.each(this.dataset.get("column_schema"), _.bind(function(c, i) {
            if (!this.search.query || !this.search.query[c["name"]]) {
                return;
            }

            var filter_context = context;
            filter_context["c"] = c;
            filter_context["i"] = i;
            prerendered_filters[i] = PANDA.templates.inline_search_filter(filter_context);
        }, this));

        context["prerendered_filters"] = prerendered_filters;

        this.el.html(PANDA.templates.dataset_search_filters(context));

        _.each(prerendered_filters, function(v, k) {
             $("#filter-" + k).show();
        });

        $("#add-filter").change(this.add_filter);
        $(".operator").change(this.change_operator);
        $(".remove-filter").click(this.remove_filter);
    },

    add_filter: function() {
        var i = $("#add-filter").val();
        var filter = $("#filter-" + i);

        if (filter.is(":hidden")) {
            context = PANDA.utils.make_context({});

            context["operations"] = this.operations;
            context["widgets"] = this.widgets;
            context["dataset"] = this.dataset.results();
            context["query"] = this.search.query;
            context["c"] = this.dataset.get("column_schema")[i];
            context["i"] = i;

            filter.html(PANDA.templates.inline_search_filter(context));
            filter.show();

            filter.find(".operator").change(this.change_operator);
            filter.find(".remove-filter").click(this.remove_filter);
        }
        
        $("#add-filter").val("");
    },

    change_operator: function(e) {
        // TODO - parse values before replacing widget, then reset them
        var last_op = $(e.currentTarget).data("last-value");
        var new_op = $(e.currentTarget).val();
        var filter = $(e.currentTarget).parents(".filter");
        var filter_id = filter.data("filter-id");
        var c = this.dataset.get("column_schema")[filter_id];

        var column_name = c["name"];
        var column_type = c["type"];
        var column_query = this.query && this.query[column_name] ? query[column_name] : { "operator": "is", "value": "", "range_value": "" }
        column_query["operator"] = new_op;
        
        var column_operation = this.operations[column_type][column_query["operator"]];

        var values = this[column_operation["parser"]](filter);
        $.extend(column_query, values);

        filter.find(".widget").html(this.widgets[column_operation["widget"]](column_query));

        $(e.currentTarget).data("last-value", new_op);
    },

    remove_filter: function(e) {
        $(e.currentTarget).parents(".filter").hide();
        $(e.currentTarget).parents(".filter").empty();
    },

    encode: function() {
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


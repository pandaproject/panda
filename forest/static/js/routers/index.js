PANDA.routers.Index = Backbone.Router.extend({
    routes: {
        "":                                         "search",
        "search/:query":                            "search",
        "search/:query/:limit":                     "search",
        "search/:query/:limit/:page":               "search",
        "upload":                                   "upload",
        "datasets":                                 "list_datasets",
        "dataset/:id":                              "edit_dataset",
        "dataset/:id/search":                       "search_dataset"
        "dataset/:id/search/:query":                "search_dataset"
        "dataset/:id/search/:query/:limit":         "search_dataset"
        "dataset/:id/search/:query/:limit/:page":   "search_dataset"
    },

    initialize: function(options) {
        this.controller = options.controller;
    },

    search: function(query, limit, page) {
        this.controller.search(query, limit, page);
    },

    upload: function() {
        this.controller.upload();
    },

    list_datasets: function() {
        this.controller.list_datasets();
    },

    edit_dataset: function(id) {
        this.controller.edit_dataset(id);
    }

    search_dataset: function(id, query, limit, page) {
        this.controller.search_dataset(id, query, limit, page);
    }
});

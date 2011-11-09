PANDA.routers.Index = Backbone.Router.extend({
    routes: {
        "login":                                    "login",
        "register":                                 "register",
        "":                                         "search",
        "search/:query":                            "search",
        "search/:query/:limit":                     "search",
        "search/:query/:limit/:page":               "search",
        "upload":                                   "upload",
        "datasets":                                 "list_datasets",
        "datasets/:limit":                          "list_datasets",
        "datasets/:limit/:page":                    "list_datasets",
        "dataset/:id":                              "edit_dataset",
        "dataset/:id/search":                       "search_dataset",
        "dataset/:id/search/:query":                "search_dataset",
        "dataset/:id/search/:query/:limit":         "search_dataset",
        "dataset/:id/search/:query/:limit/:page":   "search_dataset",
        "*path":                                    "not_found"
    },

    initialize: function(options) {
        this.controller = options.controller;
    },

    login: function() {
        this.controller.login();
    },

    register: function() {
        this.controller.register();
    },

    search: function(query, limit, page) {
        this.controller.search(query, limit, page);
    },

    upload: function() {
        this.controller.upload();
    },

    list_datasets: function(limit, page) {
        this.controller.list_datasets(limit, page);
    },

    edit_dataset: function(id) {
        this.controller.edit_dataset(id);
    },

    search_dataset: function(id, query, limit, page) {
        this.controller.search_dataset(id, query, limit, page);
    },

    not_found: function(path) {
        this.controller.not_found(path);
    }
});

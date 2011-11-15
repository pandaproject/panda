PANDA.routers.Index = Backbone.Router.extend({
    routes: {
        "login":                                    "login",
        "logout":                                   "logout",
        "register":                                 "register",
        "":                                         "search",
        "search/:query":                            "search",
        "search/:query/:limit":                     "search",
        "search/:query/:limit/:page":               "search",
        "upload":                                   "upload",
        "datasets":                                 "list_datasets",
        "datasets/:limit":                          "list_datasets",
        "datasets/:limit/:page":                    "list_datasets",
        "dataset/:id":                              "search_dataset",
        "dataset/:id/edit":                         "edit_dataset",
        "dataset/:id/search/:query":                "search_dataset",
        "dataset/:id/search/:query/:limit":         "search_dataset",
        "dataset/:id/search/:query/:limit/:page":   "search_dataset",
        "*path":                                    "not_found"
    },

    initialize: function(options) {
        this.controller = options.controller;
    },

    login: function() {
        this.controller.goto_login();
    },

    logout: function() {
        this.controller.goto_logout();
    },

    register: function() {
        this.controller.goto_register();
    },

    search: function(query, limit, page) {
        this.controller.goto_search(query, limit, page);
    },

    upload: function() {
        this.controller.goto_upload();
    },

    list_datasets: function(limit, page) {
        this.controller.goto_list_datasets(limit, page);
    },

    edit_dataset: function(id) {
        this.controller.goto_edit_dataset(id);
    },

    search_dataset: function(id, query, limit, page) {
        this.controller.goto_search_dataset(id, query, limit, page);
    },

    not_found: function(path) {
        this.controller.goto_not_found(path);
    }
});

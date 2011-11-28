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
        "datasets":                                 "datasets_search",
        "datasets/:query":                          "datasets_search",
        "datasets/:query/:limit":                   "datasets_search",
        "datasets/:query/:limit/:page":             "datasets_search",
        "category/:id":                             "category",
        "category/:id/:query":                      "category",
        "category/:id/:query/:limit":               "category",
        "category/:id/:query/:limit/:page":         "category",
        "dataset/:id":                              "dataset_view",
        "dataset/:id/edit":                         "dataset_edit",
        "dataset/:id/search/:query":                "dataset_search",
        "dataset/:id/search/:query/:limit":         "dataset_search",
        "dataset/:id/search/:query/:limit/:page":   "dataset_search",
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

    datasets_search: function(query, limit, page) {
        this.controller.goto_datasets_search(null, query, limit, page);
    },

    category: function(id, query, limit, page) {
        this.controller.goto_datasets_search(id, query, limit, page);
    },

    dataset_view: function(id) {
        this.controller.goto_dataset_view(id);
    },

    dataset_edit: function(id) {
        this.controller.goto_dataset_edit(id);
    },

    dataset_search: function(id, query, limit, page) {
        this.controller.goto_dataset_search(id, query, limit, page);
    },

    not_found: function(path) {
        this.controller.goto_not_found();
    }
});

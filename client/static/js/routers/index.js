PANDA.routers.Index = Backbone.Router.extend({
    routes: {
        "activate/:activation_key":                     "activate",
        "login":                                        "login",
        "logout":                                       "logout",
        "":                                             "search",
        "search/:query":                                "search",
        "search/:query/:limit":                         "search",
        "search/:query/:limit/:page":                   "search",
        "upload":                                       "data_upload",
        "dataset/:dataset_slug/upload":                 "data_upload",
        "datasets/:category":                           "datasets_search",
        "datasets/:category/:query":                    "datasets_search",
        "datasets/:category/:query/:limit":             "datasets_search",
        "datasets/:category/:query/:limit/:page":       "datasets_search",
        "dataset/:slug":                                "dataset_view",
        "dataset/:slug/search":                         "dataset_view",
        "dataset/:slug/search/:query":                  "dataset_search",
        "dataset/:slug/search/:query/:limit":           "dataset_search",
        "dataset/:slug/search/:query/:limit/:page":     "dataset_search",
        "user/:id":                                     "user",
        "dashboard":                                    "dashboard",
        "*path":                                        "not_found"
    },

    initialize: function(options) {
        this.controller = options.controller;
    },

    activate: function(activation_key) {
        this.controller.goto_activate(activation_key);
    },

    login: function() {
        this.controller.goto_login();
    },

    logout: function() {
        this.controller.goto_logout();
    },

    search: function(query, limit, page) {
        this.controller.goto_search(query, limit, page);
    },

    data_upload: function(dataset_slug) {
        this.controller.goto_data_upload(dataset_slug);
    },

    datasets_search: function(category, query, limit, page) {
        this.controller.goto_datasets_search(category, query, limit, page);
    },

    dataset_view: function(slug) {
        this.controller.goto_dataset_view(slug);
    },

    dataset_search: function(slug, query, limit, page) {
        this.controller.goto_dataset_search(slug, query, limit, page);
    },
    
    user: function(id) {
        this.controller.goto_user(id);
    },

    dashboard: function() {
        this.controller.goto_dashboard();
    },

    not_found: function(path) {
        this.controller.goto_not_found();
    }
});

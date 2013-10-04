PANDA.routers.Index = Backbone.Router.extend({
    routes: {
        "activate/:activation_key":                         "activate",
        "reset\-password/:activation_key":                   "reset_password",
        "login":                                            "login",
        "logout":                                           "logout",
        "":                                                 "search",
        "search":                                           "search",
        "search/:category":                                 "search",
        "search/:category/:query":                          "search",
        "search/:category/:query/:since":                   "search",
        "search/:category/:query/:since/:limit":            "search",
        "search/:category/:query/:since/:limit/:page":      "search",
        "upload":                                           "data_upload",
        "dataset/:dataset_slug/upload":                     "data_upload",
        "datasets/:category":                               "datasets_search",
        "datasets/:category/:query":                        "datasets_search",
        "datasets/:category/:query/:limit":                 "datasets_search",
        "datasets/:category/:query/:limit/:page":           "datasets_search",
        "dataset/:slug":                                    "dataset_view",
        "dataset/:slug/search/:query":                      "dataset_search",
        "dataset/:slug/search/:query/:since":               "dataset_search",
        "dataset/:slug/search/:query/:since/:limit":        "dataset_search",
        "dataset/:slug/search/:query/:since/:limit/:page":  "dataset_search",
        "notifications":                                    "notifications",
        "notifications/:limit":                             "notifications",
        "notifications/:limit/:page":                       "notifications",
        "user/:id":                                         "user",
        "dashboard":                                        "dashboard",
        "welcome":                                          "welcome",
        "export/:id":                                       "fetch_export",
        "*path":                                            "not_found"
    },

    _percent_twenty_fix: function(param) {
        /*
         * The latest FF encodes urls in a non-standard way, as documented
         * in these Backbone tickets:
         * https://github.com/documentcloud/backbone/pull/1156
         * https://github.com/documentcloud/backbone/pull/1219
         * 
         * As of 2013.02.21 it is also effecting Chrome
         * changes made to work across browsers
         * also fixes a related rendering error in the newest firefox
         */
        if (param) {
            return param.replace("%20", " ");
        } else {
            return param;
        }
    },

    initialize: function(options) {
        this.controller = options.controller;
    },

    activate: function(activation_key) {
        this.controller.goto_activate(activation_key);
    },

    reset_password: function(activation_key) {
        this.controller.goto_reset_password(activation_key);
    },

    login: function() {
        this.controller.goto_login();
    },

    logout: function() {
        this.controller.goto_logout();
    },

    search: function(category, query, since, limit, page) {
        this.controller.goto_search(category, this._percent_twenty_fix(query), since, limit, page);
    },

    data_upload: function(dataset_slug) {
        this.controller.goto_data_upload(dataset_slug);
    },

    datasets_search: function(category, query, limit, page) {
        this.controller.goto_datasets_search(category, this._percent_twenty_fix(query), limit, page);
    },

    dataset_view: function(slug) {
        this.controller.goto_dataset_view(slug);
    },

    dataset_search: function(slug, query, since, limit, page) {
        this.controller.goto_dataset_search(slug, this._percent_twenty_fix(query), since, limit, page);
    },
    
    notifications: function(limit, page) {
        this.controller.goto_notifications(limit, page);
    },

    user: function(id) {
        this.controller.goto_user(id);
    },

    dashboard: function() {
        this.controller.goto_dashboard();
    },

    welcome: function() {
        this.controller.goto_welcome();
    },

    fetch_export: function(id) {
        this.controller.goto_fetch_export(id);
    },

    not_found: function(path) {
        this.controller.goto_not_found();
    }
});

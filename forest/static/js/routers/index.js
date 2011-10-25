PANDA.routers.Index = Backbone.Router.extend({
    routes: {
        "":                             "index",
        "search/:query":                "search",
        "search/:query/:limit":         "search",
        "search/:query/:limit/:page": "search",
        "upload":                       "upload",
        "datasets":                     "list_datasets",
        "dataset/:id":                  "edit_dataset"
    },

    initialize: function(options) {
        this.controller = options.controller;
    },

    index: function() {
        this.controller.index();
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
});

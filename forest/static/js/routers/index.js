PANDA.routers.Index = Backbone.Router.extend({
    routes: {
        "":                     "index",
        "search/:query":        "search",
        "upload":               "upload",
        "dataset/:id":          "edit_dataset"
    },

    index: function(query) {
        new PANDA.views.Index();
    },

    search: function(query) {
        new PANDA.views.Search({ collection: Data });
    },

    upload: function() {
        new PANDA.views.Upload();
    },

    edit_dataset: function(id) {
        d = new PANDA.models.Dataset({ id: id });
        d.fetch({ success: function() {
            new PANDA.views.EditDataset({ dataset: d });
        }});
    },
});

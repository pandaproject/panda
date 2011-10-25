PANDA.views.Root = Backbone.View.extend({
    el: $("body"),

    events: {
        "submit #search-form":      "search_event"
    },

    current_workspace: null,

    initialize: function() {
        this.data = new PANDA.collections.Data();
        this.router = new PANDA.routers.Index({ controller: this });

        Backbone.history.start();

        return this;
    },

    search_event: function() {
        query = $("#search-form #search-query").val();

        this.router.navigate("search/" + query, true);

        return false;
    },

    search: function(query, limit, page) {
        // TKTK: if workspace is already search, reuse--don't recreate
        this.current_workspace = new PANDA.views.Search({ collection: this.data, query: query });

        if (!_.isUndefined(query)) {
            this.data.search(query, limit, page);
        }
    },

    upload: function() {
        this.current_workspace = new PANDA.views.Upload();
    },

    list_datasets: function() {
        this.current_workspace = new PANDA.views.ListDatasets();
    },

    edit_dataset: function(id) {        
        // TKTK - should not be hardcoded
        resource_uri = PANDA.API + "/dataset/" + id + "/";
        d = new PANDA.models.Dataset({ resource_uri: resource_uri });
        d.fetch({ success: function() {
            this.current_workspace = new PANDA.views.EditDataset({ dataset: d });
        }});
    }
});

PANDA.views.Root = Backbone.View.extend({
    el: $("body"),

    events: {
        "submit #search-form":      "search_event"
    },

    current_workspace: null,

    initialize: function() {
        this.data = new PANDA.models.Data();
        this.router = new PANDA.routers.Index({ controller: this });

        Backbone.history.start();

        return this;
    },

    index: function() {
        this.current_workspace = new PANDA.views.Index();
    },

    search_event: function() {
        query = $("#search-form #search-query").val();

        this.router.navigate("search/" + query, true);

        return false;
    },

    search: function(query) {
        this.current_workspace = new PANDA.views.SearchResults({ collection: this.data, el: $("#content") });
        this.data.search(query, 10, 0);
    },

    upload: function() {
        this.current_workspace = new PANDA.views.Upload();
    },

    edit_dataset: function(id) {        
        d = new PANDA.models.Dataset({ id: id });
        d.fetch({ success: function() {
            this.current_workspace = new PANDA.views.EditDataset({ dataset: d });
        }});
    }
});

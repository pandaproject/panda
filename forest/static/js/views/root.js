PANDA.views.Root = Backbone.View.extend({
    el: $("body"),

    views: {},
    search_view: null,
    upload_view: null,
    list_datasets_view: null,
    edit_dataset_view: null,

    current_content_view: null,

    initialize: function() {
        this.data = new PANDA.collections.Data();
        this.router = new PANDA.routers.Index({ controller: this });

        Backbone.history.start();

        return this;
    },

    get_or_create_view: function(name, options) {
        /*
         * Register each view as it is created and never create more than one.
         */
        if (name in this.views) {
            return this.views[name];
        }

        this.views[name] = new PANDA.views[name](options);

        return this.views[name];
    },

    search: function(query, limit, page) {
        // This little trick avoids rerendering the Search view if
        // its already visible. Only the nested results need to be
        // rerendered.
        if (!(this.current_content_view instanceof PANDA.views.Search)) {
            this.current_content_view = this.get_or_create_view("Search", { collection: this.data });
            this.current_content_view.reset(query);
        }

        this.data.search(query, limit, page);
    },

    upload: function() {
        this.current_content_view = this.get_or_create_view("Upload", {});
        this.current_content_view.reset();
    },

    list_datasets: function() {
        this.current_content_view = this.get_or_create_view("ListDatasets", {});
        this.current_content_view.reset();
    },

    edit_dataset: function(id) {        
        resource_uri = PANDA.API + "/dataset/" + id + "/";

        d = new PANDA.models.Dataset({ resource_uri: resource_uri });

        d.fetch({ success: _.bind(function() {
            this.current_content_view = this.get_or_create_view("EditDataset", {});
            this.current_content_view.dataset = d;
            this.current_content_view.reset();
        }, this)});
    },

    search_dataset: function(id, query, limit, page) {
        alert("search dataset TKTK");
    }
});

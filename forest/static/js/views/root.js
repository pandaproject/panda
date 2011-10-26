PANDA.views.Root = Backbone.View.extend({
    el: $("body"),

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

    search: function(query, limit, page) {
        if (!this.search_view) {
            this.search_view = new PANDA.views.Search({ collection: this.data });
        }

        this.current_content_view = this.search_view;
        this.current_content_view.reset(query);

        this.data.search(query, limit, page);
    },

    upload: function() {
        if (!this.upload_view) {
            this.upload_view =  new PANDA.views.Upload();
        }

        this.current_content_view = this.upload_view;
        this.current_content_view.reset();
    },

    list_datasets: function() {
        if (!this.list_datasets_view) {
            this.list_datasets_view = new PANDA.views.ListDatasets();
        }

        this.current_content_view = this.list_datasets_view;
        this.current_content_view.reset();
    },

    edit_dataset: function(id) {        
        resource_uri = PANDA.API + "/dataset/" + id + "/";

        d = new PANDA.models.Dataset({ resource_uri: resource_uri });

        d.fetch({ success: function() {
            if (!this.edit_dataset_view) {
                this.edit_dataset_view = new PANDA.views.EditDataset({ dataset: d });
            } else {
                this.edit_dataset_view.dataset.dataset = d; 
            }
            
            this.current_content_view = this.edit_dataset_view;
            this.current_content_view.reset();
        }});
    }
});

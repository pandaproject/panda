PANDA.models.Dataset = Backbone.Model.extend({
    /*
    Equivalent of redd.models.Dataset.
    */
    urlRoot: PANDA.API + "/dataset",

    upload: null,

    parse: function(response) {
        /*
        Fetch related objects.
        */


        return response 
    },

    fetch_data_upload: function(success_callback) {
        upload = new PANDA.models.Upload({ resource_uri: this.get("data_upload") });
        upload.fetch({ success: function() {
            success_callback(upload); 
        }});
    },

    import_data: function(success_callback) {
        /*
        Kick off the dataset import and update the model with
        the task id and status.

        TKTK - error callback
        */
        $.getJSON(
            this.url() + "import",
            {},
            _.bind(function(response) {
                this.set(response);
                success_callback(this); 
            }, this)
        );
    }
});

PANDA.collections.Datasets = Backbone.Collection.extend({
    /*
    A collection of redd.models.Dataset equivalents.
    */
    model: PANDA.models.Dataset,
    url: PANDA.API + "/dataset"
});


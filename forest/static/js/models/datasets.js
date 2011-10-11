PANDA.models.Dataset = Backbone.Model.extend({
    /*
    Equivalent of redd.models.Dataset.
    */
    urlRoot: PANDA.API + "/dataset",

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

PANDA.models.Datasets = Backbone.Collection.extend({
    /*
    A collection of redd.models.Dataset equivalents.
    */
    model: PANDA.models.Dataset,
    url: PANDA.API + "/dataset"
});


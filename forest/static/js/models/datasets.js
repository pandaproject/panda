Redd.models.Dataset = Backbone.Model.extend({
    /*
    Equivalent of redd.models.Dataset.
    */
    urlRoot: Redd.API + "/dataset",

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

Redd.models.Datasets = Backbone.Collection.extend({
    /*
    A collection of redd.models.Dataset equivalents.
    */
    model: Redd.models.Dataset,
    url: Redd.API + "/dataset"
});

window.Datasets = new Redd.models.Datasets();


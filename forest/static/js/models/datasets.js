PANDA.models.Dataset = Backbone.Model.extend({
    /*
    Equivalent of redd.models.Dataset.
    */
    urlRoot: PANDA.API + "/dataset",

    data_upload: null,
    current_task: null,

    initialize: function(options) {
        if ("data_upload" in options) {
            this.data_upload = options.data_upload;
        }
        
        if ("current_task" in options) {
            this.current_task = options.current_task;
        }
    },

    parse: function(response) {
        /*
         * Extract embedded models from serialized data.
         */
        if (response.data_upload != null) {
            this.data_upload = new PANDA.models.Upload(response.data_upload);
            delete response['data_upload'];
        }

        if (response.current_task != null) {
            this.current_task = new PANDA.models.Task(response.current_task);
            delete response['current_task'];
        }

        return response 
    },

    toJSON: function() {
        /*
         * Append embedded models to serialized data.
         */
        js = Backbone.Model.prototype.toJSON.call(this);

        if (this.data_upload != null) {
            js['data_upload'] = this.data_upload.toJSON();
        } else {
            js['data_upload'] = null;
        }

        if (this.current_task != null) {
            js['current_task'] = this.current_task.toJSON();
        } else {
            js['current_task'] = null;
        }

        return js
    },

    import_data: function(success_callback) {
        /*
         * Kick off the dataset import and update the model with
         * the task id and status.
         *
         * TKTK - error callback
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
     * A collection of PANDA.models.Dataset equivalents.
     */
    model: PANDA.models.Dataset,
    url: PANDA.API + "/dataset"
});


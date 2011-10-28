PANDA.models.Dataset = Backbone.Model.extend({
    /*
    Equivalent of redd.models.Dataset.
    */
    urlRoot: PANDA.API + "/dataset",

    data_upload: null,
    current_task: null,
    data: null,

    initialize: function(options) {
        if ("data_upload" in options) {
            this.data_upload = new PANDA.models.Upload(options.data_upload);
        }
        
        if ("current_task" in options) {
            this.current_task = new PANDA.models.Task(options.current_task);
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
    },

    search: function(query, limit, page) {
        // TKTK
    }
});

PANDA.collections.Datasets = Backbone.Collection.extend({
    /*
     * A collection of PANDA.models.Dataset equivalents.
     */
    model: PANDA.models.Dataset,
    url: PANDA.API + "/dataset",
    
    page: 1,
    limit: 10,
    offset: 0,
    next: null,
    previous: null,
    total_count: 0,

    parse: function(response) {
        /*
        Parse page metadata in addition to objects.
        */
        this.limit = response.meta.limit;
        this.offset = response.meta.offset;
        this.next = response.meta.next;
        this.previous = response.meta.previous;
        this.total_count = response.meta.total_count;
        this.page = this.offset / this.limit;

        return response.objects;
    }

    search: function(query, limit, page) {
        /*
        Query the search endpoint.

        TKTK -- success and error callbacks
        */
        if (!_.isUndefined(limit)) {
            this.limit = limit;
        } else {
            this.limit = 10;
        }
        
        if (!_.isUndefined(page)) {
            this.page = page;
            this.offset = this.limit * (this.page - 1);
        } else {
            this.page = 1;
            this.offset = 0;
        }

        $.getJSON(
            PANDA.API + "/data/search/",
            { q: query, limit: this.limit, offset: this.offset },
            _.bind(function(response) {
                // TKTK
                var objs = this.parse(response);
                this.reset(objs);
            }, this)
        );
    },

    results: function() {
        /*
        Grab the current data in a simplified data structure appropriate
        for templating.

        TKTK - fix
        */
        return {
            query: this.query,
            limit: this.limit,
            offset: this.offset,
            page: this.page,
            next: this.next,
            previous: this.previous,
            total_count: this.total_count,
            groups: this.groups,
            rows: this.toJSON()
        }
    } 
});


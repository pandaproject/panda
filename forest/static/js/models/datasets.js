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

        this.data = new PANDA.collections.Data();
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

        // Does this dataset have embedded search results?
        if (response.objects != null) {
            this.data.add(this.data.parse(response));

            delete response["meta"];
            delete response["objects"];
        }

        return response 
    },

    toJSON: function() {
        /*
         * Append embedded models to serialized data.
         *
         * NOTE: never serialize embedded data from search results.
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

    results: function() {
        /*
         * Render this object with embedded search results data for templating.
         */
        results = this.toJSON();
        _.extend(results, this.data.results());

        return results;
    },

    import_data: function(success_callback) {
        /*
         * Kick off the dataset import and update the model with
         * the task id and status.
         *
         * TKTK - error callback
         */
        $.ajax({
            url: this.url() + "import",
            dataType: 'json',
            headers: $.get_auth_headers(),
            success: _.bind(function(response) {
                this.set(response);
                success_callback(this); 
            }, this)
        });
    },

    search: function(query, limit, page, success) {
        /*
        Query the dataset search endpoint.

        TKTK -- success and error callbacks
        */
        if (limit) {
            this.data.meta.limit = limit;
        } else {
            this.data.meta.limit = PANDA.settings.PANDA_DEFAULT_SEARCH_ROWS;
        }
        
        if (page) {
            this.data.meta.page = page;
            this.data.meta.offset = this.data.meta.limit * (this.data.meta.page - 1);
        } else {
            this.data.meta.page = 1;
            this.data.meta.offset = 0;
        }

        $.ajax({
            url: PANDA.API + "/dataset/" + this.get("id") + "/search/",
            dataType: 'json',
            headers: $.get_auth_headers(),
            data: { q: query, limit: this.data.meta.limit, offset: this.data.meta.offset },
            success: _.bind(function(response) {
                objs = this.data.parse(response);
                delete response["meta"];
                delete response["objects"];

                this.set(response);

                this.data.reset(objs);
            }, this)
        });
    }
});

PANDA.collections.Datasets = Backbone.Collection.extend({
    /*
     * A collection of PANDA.models.Dataset equivalents.
     */
    model: PANDA.models.Dataset,
    url: PANDA.API + "/dataset",
    
    meta: {
        page: 1,
        limit: PANDA.settings.PANDA_DEFAULT_SEARCH_GROUPS,
        offset: 0,
        next: null,
        previous: null,
        total_count: 0
    },

    parse: function(response) {
        /*
        Parse page metadata in addition to objects.
        */
        this.meta = response.meta;
        this.meta.page = this.meta.offset / this.meta.limit;

        return response.objects;
    },

    search: function(query, limit, page) {
        /*
        Query the search endpoint.

        TKTK -- success and error callbacks
        */
        if (limit) {
            this.meta.limit = limit;
        } else {
            this.meta.limit = PANDA.settings.PANDA_DEFAULT_SEARCH_GROUPS;
        }
        
        if (page) {
            this.meta.page = page;
            this.meta.offset = this.meta.limit * (this.meta.page - 1);
        } else {
            this.meta.page = 1;
            this.meta.offset = 0;
        }

        $.ajax({
            url: PANDA.API + "/data/search/",
            dataType: 'json',
            headers: $.get_auth_headers(),
            data: { q: query, limit: this.meta.limit, offset: this.meta.offset },
            success: _.bind(function(response) {
                var objs = this.parse(response);

                datasets = _.map(objs, function(obj) {
                    d = new PANDA.models.Dataset();
                    d.set(d.parse(obj));

                    return d;
                });

                this.reset(datasets);
            }, this)
        });
    },

    results: function() {
        /*
        Grab the current data in a simplified data structure appropriate
        for templating.
        */
        return {
            meta: this.meta,
            datasets: _.invoke(this.models, "results") 
        }
    } 
});


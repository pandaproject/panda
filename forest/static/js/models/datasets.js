PANDA.models.Dataset = Backbone.Model.extend({
    /*
     * Equivalent of redd.models.Dataset.
     */
    urlRoot: PANDA.API + "/dataset",

    categories: null,
    creator: null,
    data_upload: null,
    current_task: null,
    data: null,

    initialize: function(attributes) {
        if ("categories" in attributes) {
            this.categories = new PANDA.collections.Categories(attributes.categories);
        } else {
            this.categories = new PANDA.collections.Categories();
        }

        if ("creator" in attributes) {
            this.creator = new PANDA.models.User(attributes.creator);
        }
        
        if ("current_task" in attributes) {
            this.current_task = new PANDA.models.Task(attributes.current_task);
        }

        if ("uploads" in attributes) {
            this.uploads = new PANDA.collections.Uploads(attributes.uploads);
        } else {
            this.uploads = new PANDA.collections.Uploads();
        }

        this.data = new PANDA.collections.Data();
    },

    parse: function(response) {
        /*
         * Extract embedded models from serialized data.
         */
        this.categories = new PANDA.collections.Categories(response.categories);

        if (response.creator != null) {
            this.creator = new PANDA.models.User(response.creator);
        }
        
        if (response.current_task != null) {
            this.current_task = new PANDA.models.Task(response.current_task);
        }

        this.uploads = new PANDA.collections.Uploads(response.uploads);
        
        delete response["categories"];
        delete response["creator"];
        delete response["current_task"];
        delete response["uploads"];

        // Does this dataset have embedded search results?
        if (response.objects != null) {
            this.data.add(this.data.parse(response));

            delete response["meta"];
            delete response["objects"];
        }

        return response 
    },

    toJSON: function(full) {
        /*
         * Append embedded models to serialized data.
         *
         * NOTE: never serialize embedded data from search results.
         */
        js = Backbone.Model.prototype.toJSON.call(this);

        if (full) {
            js['categories'] = this.categories.toJSON();
        } else {
            js['categories'] = this.categories.map(function(cat) { return cat.id });
        }

        if (this.creator != null) {
            if (full) {
                js['creator'] = this.creator.toJSON();
            } else {
                js['creator'] = this.creator.id;
            }
        } else {
            js['creator'] = null;
        }

        if (this.current_task != null) {
            if (full) {
                js['current_task'] = this.current_task.toJSON();
            } else {
                js['current_task'] = this.current_task.id;
            }
        } else {
            js['current_task'] = null;
        }

        if (this.data_upload != null) {
            if (full) {
                js['data_upload'] = this.data_upload.toJSON();
            } else {
                js['data_upload'] = this.data_upload.id;
            }
        } else {
            js['data_upload'] = null;
        }

        if (full) {
            js['uploads'] = this.uploads.toJSON();
        } else {
            js['uploads'] = this.uploads.map(function(upload) { return upload.id });
        }

        return js
    },

    results: function() {
        /*
         * Render this object with embedded search results data for templating.
         */
        results = this.toJSON(true);
        _.extend(results, this.data.results());

        return results;
    },

    import_data: function(upload_id, success_callback) {
        /*
         * Kick off the dataset import and update the model with
         * the task id and status.
         *
         * TODO - error callback
         */
        Redd.ajax({
            url: this.url() + "import/" + upload_id + "/",
            dataType: 'json',
            success: _.bind(function(response) {
                this.set(response);
                success_callback(this); 
            }, this)
        });
    },

    patch: function(attributes, options) {
        /*
         * Update a dataset in place using the PATCH verb.
         *
         * A special-case for the dataset edit page so that readonly attributes
         * are not lost.
         */
        this.set(attributes);

        Redd.ajax({
            url: this.url(),
            type: 'PATCH',
            data: JSON.stringify(this.toJSON()),
            contentType: 'application/json',
            dataType: 'json',
            success: _.bind(function(response) {
                this.set(response);

                if ('success' in options) {
                    options['success'](this, response);
                }
            }, this),
            error: _.bind(function(xhr, status, error) {
                if ('error' in options) {
                    options['error'](this, xhr.responseText);
                }
            }, this)
        });
    },

    search: function(query, limit, page) {
        /*
         * Query the dataset search endpoint.
         *
         * TODO -- success and error callbacks
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

        Redd.ajax({
            url: PANDA.API + "/dataset/" + this.get("slug") + "/data/",
            dataType: 'json',
            data: { q: query, limit: this.data.meta.limit, offset: this.data.meta.offset },
            success: _.bind(this.process_search_results, this)
        });
    },

    process_search_results: function(response) {
        objs = this.data.parse(response);
        delete response["meta"];
        delete response["objects"];

        this.set(response);

        this.data.reset(objs);
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
        this.meta.page = Math.floor(this.meta.offset / this.meta.limit) + 1;

        return response.objects;
    },

    search: function(query, limit, page) {
        /*
         * Query the data search endpoint.
         *
         * TODO -- success and error callbacks
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

        Redd.ajax({
            url: PANDA.API + "/data/",
            dataType: 'json',
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

    search_meta: function(category, query, limit, page) {
        /*
         * Query the metadata search endpoint. By default, returns everything.
         *
         * Note: Models returned from this are not complete.
         */
        if (limit) {
            this.meta.limit = limit;
        }
        
        if (page) {
            this.meta.page = page;
            this.meta.offset = this.meta.limit * (this.meta.page - 1);
        }

        data = {
            offset: this.meta.offset,
            simple: "true"
        };

        if (query) {
            data['q'] = query;
        }

        if (limit) {
            data['limit'] = limit;
        }

        if (category) {
            data["category"] = category;
        }

        Redd.ajax({
            url: PANDA.API + "/dataset/",
            dataType: "json",
            data: data,
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
         * Grab the current data in a simplified data structure appropriate
         * for templating.
         */
        return {
            meta: this.meta,
            datasets: _.invoke(this.models, "results") 
        }
    } 
});


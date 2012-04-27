PANDA.models.Dataset = Backbone.Model.extend({
    /*
     * Equivalent of panda.models.Dataset.
     */
    urlRoot: PANDA.API + "/dataset",

    categories: null,
    creator: null,
    data_uploads: null,
    related_uploads: null,
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

        if ("data_uploads" in attributes) {
            this.data_uploads = new PANDA.collections.DataUploads(attributes.data_uploads);
        } else {
            this.data_uploads = new PANDA.collections.DataUploads();
        }

        if ("related_uploads" in attributes) {
            this.related_uploads = new PANDA.collections.RelatedUploads(attributes.related_uploads);
        } else {
            this.related_uploads = new PANDA.collections.RelatedUploads();
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

        this.data_uploads = new PANDA.collections.DataUploads(response.data_uploads);
        this.related_uploads = new PANDA.collections.RelatedUploads(response.related_uploads);
        
        delete response["categories"];
        delete response["creator"];
        delete response["current_task"];
        delete response["data_uploads"];
        delete response["related_uploads"];

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
        var js = Backbone.Model.prototype.toJSON.call(this);

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

        if (full) {
            js['data_uploads'] = this.data_uploads.toJSON();
        } else {
            js['data_uploads'] = this.data_uploads.map(function(data_uploads) { return data_uploads.id });
        }
        
        if (full) {
            js['related_uploads'] = this.related_uploads.toJSON();
        } else {
            js['related_uploads'] = this.related_uploads.map(function(related_uploads) { return related_uploads.id });
        }

        return js
    },

    results: function() {
        /*
         * Render this object with embedded search results data for templating.
         */
        var results = this.toJSON(true);
        _.extend(results, this.data.results());

        return results;
    },

    import_data: function(data_uploads_id, success_callback, error_callback) {
        /*
         * Kick off the dataset import and update the model with
         * the task id and status.
         *
         * NB: Runs synchronously.
         */
        Redd.ajax({
            url: this.url() + "import/" + data_uploads_id + "/",
            async: false,
            dataType: 'json',
            success: _.bind(function(response) {
                this.set(response);

                if (success_callback) {
                    success_callback(this);
                }
            }, this),
            error: function(xhr, textStatus) {
                error = JSON.parse(xhr.responseText);

                if (error_callback) {
                    error_callback(error);
                }
            }
        });
    },

    reindex_data: function(indexed, column_types, success_callback, error_callback) {
        /*
         * Kick off the dataset reindexing and update the model with
         * the task id and status.
         *
         * NB: Runs synchronously.
         */
        data = {
            typed_columns: typed_columns.join(','),
            column_types: column_types.join(',')
        };

        Redd.ajax({
            url: this.url() + "reindex/",
            async: false,
            dataType: 'json',
            data: data,
            success: _.bind(function(response) {
                this.set(response);

                if (success_callback) {
                    success_callback(this);
                }
            }, this),
            error: function(xhr, textStatus) {
                error = JSON.parse(xhr.responseText);

                if (error_callback) {
                    error_callback(error);
                }
            }
        });
    },

    export_data: function(success_callback, error_callback) {
        /*
         * Kick off the dataset export and update the model with
         * the task id and status.
         */
        Redd.ajax({
            url: this.url() + "export/",
            dataType: 'json',
            success: _.bind(function(response) {
                this.set(response);

                if (success_callback) {
                    success_callback(this); 
                }
            }, this),
            error: function(xhr, textStatus) {
                var error = JSON.parse(xhr.responseText);

                if (error_callback) {
                    error_callback(error);
                }
            }
        });
    },

    patch: function(attributes, success_callback, error_callback) {
        /*
         * Update a dataset in place using the PATCH verb.
         *
         * A special-case for the dataset edit page so that readonly attributes
         * are not lost.
         */
        this.set(attributes || {});

        Redd.ajax({
            url: this.url() + "?patch=true",
            type: 'PUT',
            data: JSON.stringify(this.toJSON()),
            contentType: 'application/json',
            dataType: 'json',
            async: false,
            success: _.bind(function(response) {
                this.set(response);

                if (success_callback) {
                    success_callback(response);
                }
            }, this),
            error: _.bind(function(xhr, status, error) {
                if (error_callback) {
                    error_callback(this, xhr.responseText);
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
            this.data.meta.limit = PANDA.settings.DEFAULT_SEARCH_ROWS;
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
        var objs = this.data.parse(response);
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
    urlRoot: PANDA.API + "/dataset",
    
    meta: {
        page: 1,
        limit: PANDA.settings.DEFAULT_SEARCH_GROUPS,
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
            this.meta.limit = PANDA.settings.DEFAULT_SEARCH_GROUPS;
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

    search_meta: function(category, query, limit, page, success_callback, error_callback) {
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

        var data = {
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

                if (success_callback) {
                    success_callback(this, response);
                }
            }, this),
            error: _.bind(function(xhr, status, error) {
                if (error_callback) {
                    error_callback(this, xhr.responseText);
                }
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


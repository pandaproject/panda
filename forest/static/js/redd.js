(function() {
    window.Redd = {};
    Redd.controllers = {};
    Redd.model = {};
    Redd.app = {};
    Redd.ui = {};

    Redd.API = "/api/1.0"

    Redd.model.Dataset = Backbone.Model.extend({
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

    Redd.model.DatasetSet = Backbone.Collection.extend({
        /*
        A collection of redd.models.Dataset equivalents.
        */
        model: Redd.model.Dataset,
        url: Redd.API + "/dataset"
    });

    window.Datasets = new Redd.model.DatasetSet();
    
    Redd.model.Datum = Backbone.Model.extend({
        /*
        An individual row of data.
        */
        urlRoot: Redd.API + "/data"
    });

    Redd.model.DatumSet = Backbone.Collection.extend({
        /*
        A collection of individual Datums, together with
        metadata related to paging.
        */
        model: Redd.model.Datum,
        url: Redd.API + "/data",

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
        },

        fetch: function(options) {
            /*
            Pass page metadata as querystring parameters when fetching.
            */
            typeof(options) != "undefined" || (options = {});

            options.data = {};
            options.data.limit = this.limit;
            options.data.offset = this.offset;

            return Backbone.Collection.prototype.fetch.call(this, options);
        },

        search: function(query) {
            /*
            Query the search endpoint.

            TKTK -- success and error callbacks
            */
            this.offset = 0;

            $.getJSON(
                this.url + "/search",
                { q: query, limit: this.limit, offset: this.offset },
                _.bind(function(response) {
                    var objs = this.parse(response);
                    this.reset(objs);
                }, this)
            );
        },

        results: function() {
            /*
            Grab the current data in a simplified data structure appropriate
            for templating.
            */
            return {
                limit: this.limit,
                offset: this.offset,
                page: this.page,
                next: this.next,
                previous: this.previous,
                total_count: this.total_count,
                rows: this.toJSON()
            }
        },

        next_page: function() {
            /*
            Fetch the next page of results.

            TKTK - validate this.next is not none
            */
            $.getJSON(
                this.next,
                _.bind(function(response) {
                    var objs = this.parse(response);
                    this.reset(objs);
                }, this));
        },

        previous_page: function() {
            /*
            Fetch the previous page of results.

            TKTK - validate this.previous is not none
            */
            $.getJSON(
                this.previous,
                _.bind(function(response) {
                    var objs = this.parse(response);
                    this.reset(objs);
                }, this));
        }
    });

    window.Data = new Redd.model.DatumSet();
})();


PANDA.models.Datum = Backbone.Model.extend({
    /*
    An individual row of data.
    */
    urlRoot: PANDA.API + "/data"
});

PANDA.collections.Data = Backbone.Collection.extend({
    /*
    A collection of individual Datums, together with
    metadata related to paging.
    */
    model: PANDA.models.Datum,
    url: PANDA.API + "/data",

    page: 1,
    limit: 10,
    offset: 0,
    next: null,
    previous: null,
    total_count: 0,

    groups: {},

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

        this.groups = response.groups;
        
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
            groups: this.groups,
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


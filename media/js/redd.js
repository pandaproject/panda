(function() {
    window.Redd = {};
    Redd.controllers = {};
    Redd.model = {};
    Redd.app = {};
    Redd.ui = {};

    Redd.API = "/api/1.0"

    Redd.model.Dataset = Backbone.Model.extend({
        urlRoot: Redd.API + "/dataset"
    });

    Redd.model.DatasetSet = Backbone.Collection.extend({
        model: Redd.model.Dataset,
        url: Redd.API + "/dataset"
    });

    window.Datasets = new Redd.model.DatasetSet();
    
    Redd.model.Datum = Backbone.Model.extend({
        urlRoot: Redd.API + "/data"
    });

    Redd.model.DatumSet = Backbone.Collection.extend({
        model: Redd.model.Datum,
        url: Redd.API + "/data",

        page: 1,
        limit: 10,
        offset: 0,
        next: null,
        previous: null,
        total_count: 0,

        parse: function(response) {
            this.limit = response.meta.limit;
            this.offset = response.meta.offset;
            this.next = response.meta.next;
            this.previous = response.meta.previous;
            this.total_count = response.meta.total_count;
            this.page = this.offset / this.limit;
            
            return response.objects;
        },

        fetch: function(options) {
            typeof(options) != 'undefined' || (options = {});

            options.data = {};
            options.data.limit = this.limit;
            options.data.offset = this.offset;

            return Backbone.Collection.prototype.fetch.call(this, options);
        },

        search: function(query) {
            this.offset = 0;

            $.getJSON(
                this.url + '/search',
                { q: query, limit: this.limit, offset: this.offset },
                _.bind(function(response) {
                    var objs = this.parse(response);
                    this.reset(objs);
                }, this));
        },

        results: function() {
            return {
                limit: this.limit,
                offset: this.offset,
                page: this.page,
                total_count: this.total_count,
                rows: this.toJSON()
            }
        },

        next_page: function() {
            // TKTK - validate this.next is not none

            $.getJSON(
                this.next,
                _.bind(function(response) {
                    var objs = this.parse(response);
                    this.reset(objs);
                }, this));
        },

        previous_page: function() {
            // TKTK - validate this.previous is not none

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


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
            this.reset();
            this.offset = 0;

            $.getJSON(
                this.url + '/search',
                { q: query, limit: this.limit, offset: this.offset },
                _.bind(function(response) {
                    var objs = this.parse(response);
                    this.add(objs);
                }, this));
        },

        next: function() {
        },

        previous: function() {
        }
    });

    window.Data = new Redd.model.DatumSet();
})();


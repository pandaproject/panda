PANDA.models.Datum = Backbone.Model.extend({
    /* A single unit of data. */
});

PANDA.collections.Data = Backbone.Collection.extend({
    /*
    A collection of individual Datums for a single Dataset,
    together with metadata related to paging.
    */
    model: PANDA.models.Datum,

    meta: {
        page: 1,
        limit: 10,
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

    results: function() {
        /*
         * Render data with embedded data for templating.
         */
        return {
            meta: this.meta,
            data: this.toJSON()
        }
    }
});


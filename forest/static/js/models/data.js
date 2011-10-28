PANDA.models.Datum = Backbone.Model.extend({
    /* A single unit of data. */
});

PANDA.collections.Data = Backbone.Collection.extend({
    /*
    A collection of individual Datums for a single Dataset,
    together with metadata related to paging.
    */
    model: PANDA.models.Datum,

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

    results: function() {
        /*
         * Render data with embedded data for templating.
         */
        return {
            limit: this.limit,
            offset: this.offset,
            page: this.page,
            next: this.next,
            previous: this.previous,
            total_count: this.total_count,
            data: this.toJSON()
        }
    }
});


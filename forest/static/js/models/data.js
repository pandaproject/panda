PANDA.models.Datum = Backbone.Model.extend({});

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
    }
});


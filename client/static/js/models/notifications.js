PANDA.models.Notification = Backbone.Model.extend({
    /*
    Equivalent of panda.models.Notification.
    */
    urlRoot: PANDA.API + "/notification"
});

PANDA.collections.Notifications = Backbone.Collection.extend({
    /*
    A collection of panda.models.Notification equivalents.
    */
    model: PANDA.models.Notification,
    urlRoot: PANDA.API + "/notification",

    meta: null,

    parse: function(response) {
        /*
        Parse page metadata in addition to objects.
        */
        this.meta = response.meta;
        this.meta.page = Math.floor(this.meta.offset / this.meta.limit) + 1;

        return response.objects;
    },
    
    comparator: function(note) {
        /*
         * Ensure notes render in  order.
         */
        return -moment(note.get("sent_at"), "YYYY-MM-DD HH:mm:ss").valueOf();
    }
});


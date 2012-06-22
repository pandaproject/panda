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
    
    comparator: function(note) {
        /*
         * Ensure notes render in  order.
         */
        return -moment(note.get("sent_at"), "YYYY-MM-DD HH:mm:ss").valueOf();
    }
});


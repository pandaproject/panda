PANDA.models.Notification = Backbone.Model.extend({
    /*
    Equivalent of redd.models.Notification.
    */
    urlRoot: PANDA.API + "/notification"
});

PANDA.collections.Notifications = Backbone.Collection.extend({
    /*
    A collection of PANDA.models.Notification equivalents.
    */
    model: PANDA.models.Notification,
    url: PANDA.API + "/notification"
});


PANDA.models.SearchSubscription = Backbone.Model.extend({
    /*
    Equivalent of panda.models.Notification.
    */
    urlRoot: PANDA.API + "/search_subscription"
});

PANDA.collections.SearchSubscriptions = Backbone.Collection.extend({
    /*
    A collection of panda.models.Notification equivalents.
    */
    model: PANDA.models.SearchSubscription,
    urlRoot: PANDA.API + "/search_subscription"
});


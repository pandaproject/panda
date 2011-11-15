PANDA.models.User = Backbone.Model.extend({
    /*
    Equivalent of django.contrib.auth.models.User.
    */
    urlRoot: PANDA.API + "/user",

    notifications: null,

    initialize: function(attributes) {
        if ("notifications" in attributes) {
            this.notifications = new PANDA.collections.Notifications(attributes.notifications);
        } else {
            this.notifications = new PANDA.collections.Notifications();
        }
    },

    refresh_notifications: function(success) {
        this.notifications.fetch({ success: success });
    }
});

PANDA.collections.Users = Backbone.Collection.extend({
    /*
    A collection of django.contrib.auth.models.User equivalents.
    */
    model: PANDA.models.User,
    url: PANDA.API + "/user"
});


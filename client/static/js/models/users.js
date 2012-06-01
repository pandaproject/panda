PANDA.models.User = Backbone.Model.extend({
    /*
    Equivalent of django.contrib.auth.models.User.
    */
    urlRoot: PANDA.API + "/user",

    notifications: null,
    subscriptions: null,

    initialize: function(attributes) {
        if ("notifications" in attributes) {
            this.notifications = new PANDA.collections.Notifications(attributes.notifications);
        } else {
            this.notifications = new PANDA.collections.Notifications();
        }

        if ("subscriptions" in attributes) {
            this.subscriptions = new PANDA.collections.SearchSubscriptions(attributes.subscriptions);
        } else {
            this.subscriptions = new PANDA.collections.SearchSubscriptions();
        }
    },

    refresh_notifications: function(success_callback, error_callback) {
        /*
         * Refresh notifications list from the server.
         *
         * NB: Returns up to a thousand notifications.
         * This may need to be tweaked later.
         */
        this.notifications.fetch({
            data: {
                read_at__isnull: true,
                limit: 1000
            },
            success: _.bind(function(response) {
                if (success_callback) {
                    success_callback(this, response);
                }
            }, this),
            error: function(xhr, textStatus) {
                error = JSON.parse(xhr.responseText);

                if (error_callback) {
                    error_callback(this, error);
                }
            }
        });
    },

    mark_notifications_read: function(success_callback) {
        /*
         * Mark all notifications as read.
         *
         * TODO: bulk update
         */
        var now = moment().format("YYYY-MM-DDTHH:mm:ss");

        this.notifications.each(function(note) {
            note.save({ read_at: now }, { async: false });
        });

        this.notifications.reset();
        success_callback();
    },

    refresh_subscriptions: function(success_callback, error_callback) {
        /*
         * Refresh subscriptions list from the server.
         *
         * NB: Returns up to a thousand subscriptions.
         * This may need to be tweaked later.
         */
        this.subscriptions.fetch({
            async: false,
            data: {
                limit: 1000
            },
            success: _.bind(function(response) {
                if (success_callback) {
                    success_callback(this, response);
                }
            }, this),
            error: function(xhr, textStatus) {
                error = JSON.parse(xhr.responseText);

                if (error_callback) {
                    error_callback(this, error);
                }
            }
        });
    },

    toJSON: function(full) {
        /*
         * Append embedded models to serialized data.
         *
         * NOTE: never serialize embedded data from search results.
         */
        var js = Backbone.Model.prototype.toJSON.call(this);

        if (full) {
            js['notifications'] = this.notifications.toJSON();
        } else {
            js['notifications'] = this.notifications.map(function(note) { return note.id });
        }

        if (full) {
            js['subscriptions'] = this.subscriptions.toJSON();
        } else {
            js['subscriptions'] = this.subscriptions.map(function(sub) { return sub.id });
        }

        return js;
    }
});

PANDA.collections.Users = Backbone.Collection.extend({
    /*
    A collection of django.contrib.auth.models.User equivalents.
    */
    model: PANDA.models.User,
    urlRoot: PANDA.API + "/user"
});


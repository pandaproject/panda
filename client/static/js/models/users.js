PANDA.models.User = Backbone.Model.extend({
    /*
    Equivalent of django.contrib.auth.models.User.
    */
    urlRoot: PANDA.API + "/user",

    notifications: null,
    datasets: null,
    exports: null,
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

        if ("datasets" in attributes) {
            this.datasets = new PANDA.collections.Datasets(attributes.datasets);
        } else {
            this.datasets = new PANDA.collections.Datasets();
        }

        if ("exports" in attributes) {
            this.exports = new PANDA.collections.Exports(attributes.exports);
        } else {
            this.exports = new PANDA.collections.Exports();
        }
    },

    parse: function(response) {
        /*
         * Extract embedded models from serialized data.
         */
        if ("notifications" in response) {
            this.notifications = new PANDA.collections.Notifications(response.notifications);
        } else {
            this.notifications = new PANDA.collections.Notifications();
        }

        if ("subscriptions" in response) {
            this.subscriptions = new PANDA.collections.SearchSubscriptions(response.subscriptions);
        } else {
            this.subscriptions = new PANDA.collections.SearchSubscriptions();
        }

        if ("datasets" in response) {
            this.datasets = new PANDA.collections.Datasets(response.datasets);
        } else {
            this.datasets = new PANDA.collections.Datasets();
        }

        if ("exports" in response) {
            this.exports = new PANDA.collections.Exports(response.exports);
        } else {
            this.exports = new PANDA.collections.Exports();
        }

        return response 
    },

    patch: function(attributes, success_callback, error_callback) {
        /*
         * Update a user in place using the PATCH verb.
         *
         * A special-case for the user edit page so that readonly attributes
         * are not lost.
         */
        this.set(attributes || {});

        Redd.ajax({
            url: this.url() + "?patch=true",
            type: "PUT",
            data: JSON.stringify(this.toJSON()),
            contentType: "application/json",
            dataType: "json",
            async: false,
            success: _.bind(function(response) {
                this.set(response);

                if (success_callback) {
                    success_callback(this);
                }
            }, this),
            error: _.bind(function(xhr, status, error) {
                if (error_callback) {
                    error_callback(this, xhr.responseText);
                }
            }, this)
        });
    },

    refresh_notifications: function(success_callback, error_callback) {
        /*
         * Refresh notifications list from the server.
         */
        this.notifications.fetch({
            data: {
                limit: PANDA.settings.NOTIFICATIONS_TO_SHOW 
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

    mark_notifications_read: function() {
        /*
         * Mark all notifications as read.
         */
        var now = moment().format("YYYY-MM-DDTHH:mm:ss");

        var patch = { objects: [] };

        this.notifications.each(function(note) {
            if (!note.get("read_at")) {
                note.set({ read_at: now });
                patch.objects.push({ resource_uri: note.id, read_at: now });
            }
        });

        if (patch.objects.length == 0) {
            return;
        }

        $.ajax({
            url: this.notifications.url() + "?patch=true",
            contentType: "application/json",
            dataType: "json",
            type: "PUT",
            data: JSON.stringify(patch)
        });
    },

    set_show_login_help: function(value, success_callback, error_callback) {
        $.ajax({
            url: this.url() + "login_help/",
            contentType: "application/json",
            dataType: "json",
            type: "POST",
            data: JSON.stringify({ "show_login_help": value }),
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
            js["notifications"] = this.notifications.toJSON();
        } else {
            js["notifications"] = this.notifications.map(function(note) { return note.id });
        }

        if (full) {
            js["subscriptions"] = this.subscriptions.toJSON();
        } else {
            js["subscriptions"] = this.subscriptions.map(function(sub) { return sub.id });
        }

        if (full) {
            js["datasets"] = this.datasets.toJSON();
        } else {
            js["datasets"] = this.datasets.map(function(dataset) { return dataset.id });
        }

        if (full) {
            js["exports"] = this.exports.toJSON();
        } else {
            js["exports"] = this.exports.map(function(exp) { return exp.id });
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


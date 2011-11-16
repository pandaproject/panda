PANDA.views.Root = Backbone.View.extend({
    /*
     * The singleton view which manages all others. Essentially, a "controller".
     *
     * A single instance of this object exists in the global namespace as "Redd".
     */
    el: $("body"),

    views: {},

    _current_user: null,
    _categories: null,
    current_content_view: null,

    initialize: function() {
        // Bind local methods
        _.bindAll(this, "get_categories", "get_category_by_id");

        // Override Backbone's sync handler with the authenticated version
        Backbone.noAuthSync = Backbone.sync;
        Backbone.sync = _.bind(this.sync, this);

        // Create objects from bootstrap data
        this._categories = new PANDA.collections.Categories(PANDA.bootstrap.categories);

        // Setup global router
        this.router = new PANDA.routers.Index({ controller: this });

        // Attempt to authenticate from cookies
        this.authenticate();

        // Configure the global topbar
        this.configure_topbar();

        $("#topbar-notifications .clear-unread").live("click", _.bind(this.clear_unread_notifications, this));

        return this;
    },

    start_routing: function() {
        /*
         * Start Backbone routing. Separated from initialize() so that the
         * global controller is available for any preset routes (direct links).
         */
        Backbone.history.start();
    },

    authenticate: function() {
        /*
         * Verifies that the current user is authenticated, first by checking
         * for an active user and then by checking for a cookie. Redirects
         * to login if authentication fails.
         */
        if (this._current_user) {
            return true;
        }

        email = $.cookie("email");
        api_key = $.cookie("api_key");

        if (email && api_key) {
            this.set_current_user(new PANDA.models.User({ "email": email, "api_key": api_key }));

            // Fetch latest notifications (doubles as a verification of the user's credentials)
            this._current_user.refresh_notifications(_.bind(this.configure_topbar, this));

            return true;
        }

        window.location = "#login";

        return false;
    },

    get_current_user: function() {
        /*
         * Gets the current system user.
         */
        return this._current_user;
    },

    set_current_user: function(user) {
        /*
         * Sets the current system user. Assumes that user has already authenticated.
         */
        this._current_user = user;

        if (this._current_user) {
            $.cookie('email', this._current_user.get("email"));
            $.cookie('api_key', this._current_user.get("api_key"));
        } else {
            $.cookie('email', null);
            $.cookie('api_key', null);
        }
            
        this.configure_topbar();
    },

    get_categories: function() {
        return this._categories;
    },

    get_category_by_id: function(id) {
        return this._categories.find(function(cat) { return cat.get("id") == id; });
    },

    ajax: function(options) {
        /*
         * Makes an authenticated ajax request to the API.
         */
        var dfd = new $.Deferred();

        this.authenticate();

        // Handle authentication failures
        dfd.fail(function(responseXhr, status, error) {
            if (responseXhr.status == 401) {
                this.set_current_user(null);
                window.location = "#login";
            }
        });

        // Trigger original error handler after checking for auth issues
        dfd.fail(options.error);
        options.error = dfd.reject;

        dfd.request = $.ajax(options);

        return dfd;
    },

    sync: function(method, model, options) {
        /*
         * Custom Backbone sync handler to attach authorization headers
         * and handle failures.
         */
        var dfd = new $.Deferred();

        this.authenticate();

        // Handle authentication failures
        dfd.fail(function(xhr, status, error) {
            if (xhr.status == 401) {
                window.location = "#login";
            }
        });

        // Trigger original error handler after checking for auth issues
        dfd.fail(options.error);
        options.error = dfd.reject;

        dfd.request = Backbone.noAuthSync(method, model, options);

        return dfd;
    },

    configure_topbar: function() {
        /*
         * Reconfigures the Bootstrap topbar based on the current user.
         */
        if (!this._current_user) {
            $("#topbar-email").hide();
            $("#topbar-notifications").hide();
            $("#topbar-logout").hide();
            $("#topbar-login").css("display", "block");
            $("#topbar-register").css("display", "block");
        } else {
            $("#topbar-email a").text(this._current_user.get("email"));

            $("#topbar-notifications .dropdown-menu").html("");

            if (this._current_user.notifications.models.length > 0) {
                $("#topbar-notifications .count").addClass("important");

                this._current_user.notifications.each(function(note) {
                    related_dataset = note.get("related_dataset");

                    if (related_dataset) {
                        slash = related_dataset.lastIndexOf("/", related_dataset.length - 2);
                        link = "#dataset/" + related_dataset.substring(slash + 1, related_dataset.length - 1);
                    } else {
                        link = "#";
                    }

                    $("#topbar-notifications .dropdown-menu").append('<li><a href="' + link + '">' + note.get("message") + '</a></li>');
                });
            } else {
                $("#topbar-notifications .count").removeClass("important");
                $("#topbar-notifications .dropdown-menu").append('<li><a href="#">No new notifications</a></li>');
            }
            
            $("#topbar-notifications .dropdown-menu").append('<li class="divider"></li>');

            if (this._current_user.notifications.models.length > 0) {
                $("#topbar-notifications .dropdown-menu").append('<li class="clear-unread"><a href="#">Clear unread</a></li>');
            }

            $("#topbar-notifications .dropdown-menu").append('<li><a href="#">View all notifications (TODO)</a></li>');
            
            $("#topbar-notifications .count").text(this._current_user.notifications.length);

            $("#topbar-email").css("display", "block");
            $("#topbar-notifications").css("display", "block");
            $("#topbar-logout").css("display", "block");
            $("#topbar-login").hide();
            $("#topbar-register").hide();
        }
    },

    clear_unread_notifications: function() {
        this._current_user.mark_notifications_read(_.bind(function() {
            this.configure_topbar();
        }, this));

        return false;
    },

    get_or_create_view: function(name, options) {
        /*
         * Register each view as it is created and never create more than one.
         */
        if (name in this.views) {
            return this.views[name];
        }

        this.views[name] = new PANDA.views[name](options);

        return this.views[name];
    },

    goto_login: function() {
        this.current_content_view = this.get_or_create_view("Login");
        this.current_content_view.reset();
    },
    
    goto_logout: function() {
        this.set_current_user(null);

        window.location = "#login";
    },

    goto_register: function() {
        this.current_content_view = this.get_or_create_view("Register");
        this.current_content_view.reset();
    },

    goto_search: function(query, limit, page) {
        // This little trick avoids rerendering the Search view if
        // its already visible. Only the nested results need to be
        // rerendered.
        if (!this.authenticate()) {
            return;
        }

        if (!(this.current_content_view instanceof PANDA.views.Search)) {
            this.current_content_view = this.get_or_create_view("Search");
            this.current_content_view.reset(query);
        }

        this.current_content_view.search(query, limit, page);
    },

    goto_upload: function() {
        if (!this.authenticate()) {
            return;
        }

        this.current_content_view = this.get_or_create_view("Upload");
        this.current_content_view.reset();
    },

    goto_list_datasets: function(category, limit, page) {
        if (!this.authenticate()) {
            return;
        }

        this.current_content_view = this.get_or_create_view("ListDatasets");
        this.current_content_view.reset(category, limit, page);
    },

    goto_dataset_view: function(id) {
        if (!this.authenticate()) {
            return;
        }

        this.current_content_view = this.get_or_create_view("DatasetSearch");
        this.current_content_view.reset(id, null);
    },

    goto_dataset_edit: function(id) {
        if (!this.authenticate()) {
            return;
        }

        resource_uri = PANDA.API + "/dataset/" + id + "/";

        d = new PANDA.models.Dataset({ resource_uri: resource_uri });

        d.fetch({ success: _.bind(function() {
            this.current_content_view = this.get_or_create_view("DatasetEdit");
            this.current_content_view.dataset = d;
            this.current_content_view.reset();
        }, this)});
    },

    goto_dataset_search: function(id, query, limit, page) {
        if (!this.authenticate()) {
            return;
        }

        if (!(this.current_content_view instanceof PANDA.views.DatasetSearch)) {
            this.current_content_view = this.get_or_create_view("DatasetSearch");
            this.current_content_view.reset(id, query);
        }

        this.current_content_view.search(query, limit, page);
    },

    goto_not_found: function(path) {
        if (!(this.current_content_view instanceof PANDA.views.NotFound)) {
            this.current_content_view = this.get_or_create_view("NotFound");
            this.current_content_view.reset(path);
        }

        this.current_content_view.reset(path);
    }
});

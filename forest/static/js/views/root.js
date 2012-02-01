PANDA.views.Root = Backbone.View.extend({
    /*
     * The singleton view which manages all others. Essentially, a "controller".
     *
     * A single instance of this object exists in the global namespace as "Redd".
     */
    el: $("body"),

    views: {},

    _router: null,
    _current_user: null,
    _categories: null,

    notifications_refresh_timer_id: null,

    current_content_view: null,

    initialize: function() {
        // Bind local methods
        _.bindAll(this);

        // Track Ajax events
        this.track_ajax_events();

        // Override Backbone's sync handler with the authenticated version
        Backbone.noAuthSync = Backbone.sync;
        Backbone.sync = _.bind(this.sync, this);

        // Create objects from bootstrap data
        this._categories = new PANDA.collections.Categories(PANDA.bootstrap.categories);

        // Setup global router
        this._router = new PANDA.routers.Index({ controller: this });

        // Configure the global navbar
        this.configure_navbar();

        $("#navbar-notifications .clear-unread").live("click", _.bind(this.clear_unread_notifications, this));

        // Setup occasional updates of notifications
        this.notifications_refresh_timer_id = window.setInterval(this.refresh_notifications, PANDA.settings.NOTIFICATIONS_INTERVAL);

        return this;
    },

    track_ajax_events: function() {
        $(document).ajaxStart(function() {
            $("#loading-indicator img").show();
        });

        $(document).ajaxComplete(function() {
            $("#loading-indicator img").hide();
        });
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

        var email = $.cookie("email");
        var api_key = $.cookie("api_key");
        var is_staff = $.cookie("is_staff") === "true" ? true : false;

        if (email && api_key) {
            this.set_current_user(new PANDA.models.User({
                "email": email,
                "api_key": api_key,
                "is_staff": is_staff
            }));

            // Fetch latest notifications (doubles as a verification of the user's credentials)
            this.refresh_notifications();

            return true;
        }

        this.goto_login(window.location.hash);

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
            $.cookie("email", this._current_user.get("email"));
            $.cookie("api_key", this._current_user.get("api_key"));
            $.cookie("is_staff", this._current_user.get("is_staff").toString());
        } else {
            $.cookie("email", null);
            $.cookie("api_key", null);
            $.cookie("is_staff", null);
        }
            
        this.configure_navbar();
    },

    get_categories: function() {
        /*
         * Retrieve global list of categories that was bootstrapped onto the page.
         */
        return this._categories;
    },

    get_category_by_slug: function(slug) {
        /*
         * Retrieve a specific category by slug.
         */
        return this._categories.find(function(cat) { return cat.get("slug") == slug; });
    },

    ajax: function(options) {
        /*
         * Makes an authenticated ajax request to the API.
         */
        var dfd = new $.Deferred();

        this.authenticate();

        // Handle authentication failures
        dfd.fail(_.bind(function(responseXhr, status, error) {
            if (responseXhr.status == 401) {
                this.set_current_user(null);

                this.goto_login(window.location.hash);
            }
        }, this));

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
                this.goto_login(window.location.hash);
            }
        });

        // Trigger original error handler after checking for auth issues
        dfd.fail(options.error);
        options.error = dfd.reject;

        dfd.request = Backbone.noAuthSync(method, model, options);

        return dfd;
    },

    configure_navbar: function() {
        /*
         * Reconfigures the Bootstrap navbar based on the current user.
         */
        if (!this._current_user) {
            $(".navbar").hide();
            $("body").css("background-color", "#404040");
        } else {
            $("body").css("background-color", "#fff");

            $("#navbar-email a").text(this._current_user.get("email"));

            $("#navbar-notifications .dropdown-menu").html("");

            if (this._current_user.notifications.models.length > 0) {
                $("#navbar-notifications .count").addClass("important");

                this._current_user.notifications.each(function(note) {
                    var related_dataset = note.get("related_dataset");

                    if (related_dataset) {
                        var slash = related_dataset.lastIndexOf("/", related_dataset.length - 2);
                        var link = "#dataset/" + related_dataset.substring(slash + 1, related_dataset.length - 1);
                    } else {
                        var link = "#";
                    }

                    $("#navbar-notifications .dropdown-menu").append('<li><a href="' + link + '">' + note.get("message") + '</a></li>');
                });
            } else {
                $("#navbar-notifications .count").removeClass("important");
                $("#navbar-notifications .dropdown-menu").append('<li><a href="#">No new notifications</a></li>');
            }
            
            $("#navbar-notifications .dropdown-menu").append('<li class="divider"></li>');

            if (this._current_user.notifications.models.length > 0) {
                $("#navbar-notifications .dropdown-menu").append('<li class="clear-unread"><a href="#">Clear unread</a></li>');
            }

            $("#navbar-notifications .dropdown-menu").append('<li><a href="javascript:alert(\'View all notifications (TODO)\');">View all notifications</a></li>');
            
            $("#navbar-notifications .count").text(this._current_user.notifications.length);

            $("#navbar-admin").toggle(this._current_user.get("is_staff"));
            $(".navbar").show();
            window.scrollTo(0, 0); 
        }
    },

    refresh_notifications: function() {
        if (this._current_user) {
            this._current_user.refresh_notifications(_.bind(function() {
                this.configure_navbar();
            }, this));
        }
    },

    clear_unread_notifications: function() {
        /*
         * Marks all of the current user's notifications as read.
         */
        this._current_user.mark_notifications_read(_.bind(function() {
            this.configure_navbar();
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

    goto_activate: function(activation_key) {
        this.current_content_view = this.get_or_create_view("Activate");
        this.current_content_view.reset(activation_key);

        this._router.navigate("activate/" + activation_key);
    },

    goto_login: function(next) {
        this.current_content_view = this.get_or_create_view("Login");
        this.current_content_view.reset(next);

        this._router.navigate("login");
    },
    
    goto_logout: function() {
        this.set_current_user(null);

        this.goto_login();
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

        var path = "search/";

        if (query) {
            path += query;
        }
        
        if (limit) {
            path += "/" + limit;
        }

        if (page) {
            path += "/" + page;
        }

        this._router.navigate(path);
    },

    goto_data_upload: function(dataset_slug) {
        if (!this.authenticate()) {
            return;
        }

        this.current_content_view = this.get_or_create_view("DataUpload");
        this.current_content_view.reset(dataset_slug);

        if (dataset_slug) {
            this._router.navigate("dataset/" + dataset_slug + "/upload");
        } else {
            this._router.navigate("upload");
        }
    },

    goto_datasets_search: function(category, query, limit, page) {
        if (!this.authenticate()) {
            return;
        }

        this.current_content_view = this.get_or_create_view("DatasetsSearch");
        this.current_content_view.reset(category, query, limit, page);

        if (category) {
            var path = "category/" + category;
        } else {
            var path = "datasets";
        }

        if (query) {
            path += "/" + query;
        }
    
        if (limit) {
            path += "/" + limit;
        }

        if (page) {
            path += "/" + page;
        }

        this._router.navigate(path);
    },

    goto_dataset_view: function(slug) {
        if (!this.authenticate()) {
            return;
        }

        this.current_content_view = this.get_or_create_view("DatasetSearch");
        this.current_content_view.reset(slug, null);

        this._router.navigate("dataset/" + slug);
    },

    goto_dataset_search: function(slug, query, limit, page) {
        if (!this.authenticate()) {
            return;
        }

        if (!(this.current_content_view instanceof PANDA.views.DatasetSearch)) {
            this.current_content_view = this.get_or_create_view("DatasetSearch");
            this.current_content_view.reset(slug, query);
        }

        this.current_content_view.search(query, limit, page);

        var path = "dataset/" + slug + "/search";

        if (query) {
            path += "/" + query;
        }
        
        if (limit) {
            path += "/" + limit;
        }

        if (page) {
            path += "/" + page;
        }

        this._router.navigate(path);
    },

    goto_not_found: function() {
        if (!(this.current_content_view instanceof PANDA.views.NotFound)) {
            this.current_content_view = this.get_or_create_view("NotFound");
        }

        this.current_content_view.reset();
    },

    goto_server_error: function() {
        if (!(this.current_content_view instanceof PANDA.views.ServerError)) {
            this.current_content_view = this.get_or_create_view("ServerError");
        }

        this.current_content_view.reset();
    }
});

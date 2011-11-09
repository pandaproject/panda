PANDA.views.Root = Backbone.View.extend({
    el: $("body"),

    views: {},

    current_content_view: null,

    initialize: function() {
        this.router = new PANDA.routers.Index({ controller: this });

        this.configure_topbar();

        Backbone.history.start();

        return this;
    },

    configure_topbar: function() {
        username = $.cookie("username");
        api_key = $.cookie("api_key");

        if (username === null || api_key === null) {
            $("#topbar-username").hide();
            $("#topbar-logout").hide();
            $("#topbar-login").css("display", "block");
            $("#topbar-register").css("display", "block");
        } else {
            $("#topbar-username a").text(username);

            $("#topbar-username").css("display", "block");
            $("#topbar-logout").css("display", "block");
            $("#topbar-login").hide();
            $("#topbar-register").hide();
        }
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

    login: function() {
        this.current_content_view = this.get_or_create_view("Login");
        this.current_content_view.reset();
    },
    
    logout: function() {
        $.cookie("username", null);
        $.cookie("api_key", null);

        Redd.configure_topbar();

        window.location = "#login";
    },

    register: function() {
        this.current_content_view = this.get_or_create_view("Register");
        this.current_content_view.reset();
    },

    search: function(query, limit, page) {
        // This little trick avoids rerendering the Search view if
        // its already visible. Only the nested results need to be
        // rerendered.
        if (!check_auth_cookies()) {
            return;
        }

        if (!(this.current_content_view instanceof PANDA.views.Search)) {
            this.current_content_view = this.get_or_create_view("Search");
            this.current_content_view.reset(query);
        }

        this.current_content_view.search(query, limit, page);
    },

    upload: function() {
        if (!check_auth_cookies()) {
            return;
        }

        this.current_content_view = this.get_or_create_view("Upload");
        this.current_content_view.reset();
    },

    list_datasets: function(limit, page) {
        if (!check_auth_cookies()) {
            return;
        }

        this.current_content_view = this.get_or_create_view("ListDatasets");
        this.current_content_view.reset(limit, page);
    },

    edit_dataset: function(id) {
        if (!check_auth_cookies()) {
            return;
        }

        resource_uri = PANDA.API + "/dataset/" + id + "/";

        d = new PANDA.models.Dataset({ resource_uri: resource_uri });

        d.fetch({ success: _.bind(function() {
            this.current_content_view = this.get_or_create_view("EditDataset");
            this.current_content_view.dataset = d;
            this.current_content_view.reset();
        }, this)});
    },

    search_dataset: function(id, query, limit, page) {
        if (!check_auth_cookies()) {
            return;
        }

        if (!(this.current_content_view instanceof PANDA.views.DatasetSearch)) {
            this.current_content_view = this.get_or_create_view("DatasetSearch");
            this.current_content_view.reset(id, query);
        }

        this.current_content_view.search(query, limit, page);
    },

    not_found: function(path) {
        if (!(this.current_content_view instanceof PANDA.views.NotFound)) {
            this.current_content_view = this.get_or_create_view("NotFound");
            this.current_content_view.reset(path);
        }

        this.current_content_view.reset(path);
    }
});

describe("Root view / global controller", function() {
    beforeEach(function() {
        this.xhr = sinon.useFakeXMLHttpRequest();
        var requests = this.requests = [];

        this.xhr.onCreate = function(xhr) {
            requests.push(xhr);
        };

        // Fake out the Root view so its initialize won't fire
        FakeController = function() {}; 
        FakeController.prototype = PANDA.views.Root.prototype;
        window.Redd = new FakeController();

        this.auth_stub = sinon.stub(Redd, "authenticate").returns(true);
        this.navbar_stub = sinon.stub(Redd, "configure_navbar");
        this.refresh_notifications_stub = sinon.stub(Redd, "refresh_notifications");

        // Initialize with auth stubbed out
        Redd.initialize();

        this.auth_stub.restore();
        this.refresh_notifications_stub.restore();
        this.navbar_stub.restore();
        
        sandbox({ id: "body" });
    });

    afterEach(function () {
        this.xhr.restore();
    });

    describe("Initialization", function() {
        it("should override backbone sync", function() {
            expect(Backbone.noAuthSync).toBeDefined();
        });

        it("should create categories from bootstrap data", function() {
            expect(Redd._categories).not.toBeNull();
            expect(Redd._categories.length).toEqual(0);
        });

        it("should setup the global router", function() {
            expect(Redd._router).not.toBeNull();
        });

        it("should set a timer to refresh notifications", function() {
            expect(Redd.notifications_refresh_timer_id).not.toBeNull();
        });
    });

    describe("Miscellaneous", function() {
        it("should exit early if a user is already authenticated", function() {
            var user = new PANDA.models.User({ "email": "user@pandaproject.net", "api_key": "edfe6c5ffd1be4d3bf22f69188ac6bc0fc04c84c" });

            Redd._current_user = user;

            var set_current_user_stub = sinon.stub(Redd, "set_current_user");
            
            authenticated = Redd.authenticate();

            expect(authenticated).toBeTruthy();
            expect(set_current_user_stub).not.toHaveBeenCalled();

            set_current_user_stub.restore();
        });

        // Can't set cookies on file://localhost
        xit("should authenticate from a cookie", function() {
            var set_current_user_stub = sinon.stub(Redd, "set_current_user");
            var refresh_notifications_stub = sinon.stub(Redd, "refresh_notifications");

            Redd._current_user = null;
            $.cookie("email", "user@pandaproject.net");
            $.cookie("api_key", "edfe6c5ffd1be4d3bf22f69188ac6bc0fc04c84c");

            authenticated = Redd.authenticate();

            expect(authenticated).toBeTruthy();
            expect(set_current_user_stub).toHaveBeenCalledOnce();
            expect(refresh_notifications_stub).toHaveBeenCalledOnce();

            set_current_user_stub.restore();
        });

        it("should route to login if not authenticated", function() {
            var set_current_user_stub = sinon.stub(Redd, "set_current_user");
            var goto_login_stub = sinon.stub(Redd, "goto_login");

            Redd._current_user = null;
            $.cookie("email", null);
            $.cookie("api_key", null);

            authenticated = Redd.authenticate();

            expect(authenticated).toBeFalsy();
            expect(set_current_user_stub).not.toHaveBeenCalled();
            expect(this.refresh_notifications_stub).not.toHaveBeenCalled();
            expect(goto_login_stub).toHaveBeenCalledOnce();

            goto_login_stub.restore();
            set_current_user_stub.restore();
        });
    });

    describe("Ajax", function() {
        beforeEach(function() {
            this.auth_stub = sinon.stub(Redd, "authenticate").returns(true);
            this.set_current_user_stub = sinon.stub(Redd, "set_current_user");
            this.goto_login_stub = sinon.stub(Redd, "goto_login");
        });

        afterEach(function() {
            this.goto_login_stub.restore();
            this.set_current_user_stub.restore();
            this.auth_stub.restore();
        });

        it("should check authentication on ajax requests", function() {
            Redd.ajax({})

            expect(this.auth_stub).toHaveBeenCalledOnce();
        });

        it("should route to login if ajax returns 401", function () {
            Redd.ajax({})

            expect(this.requests.length).toEqual(1);

            this.requests[0].respond(401);

            expect(this.set_current_user_stub).toHaveBeenCalledOnce();
            expect(this.goto_login_stub).toHaveBeenCalledOnce();
        });

        it("should call the original failure callback", function() {
            var test_callback = sinon.spy();

            Redd.ajax({ error: test_callback })

            expect(this.requests.length).toEqual(1);

            this.requests[0].respond(500);

            expect(test_callback).toHaveBeenCalledOnce();
        });

        it("should call the original success callback", function() {
            var test_callback = sinon.spy();

            Redd.ajax({ success: test_callback })

            expect(this.requests.length).toEqual(1);

            this.requests[0].respond(200);

            expect(test_callback).toHaveBeenCalledOnce();
        });

        it("should return a deferred", function() {
            var result = Redd.ajax({});

            expect(result).not.toBeNull();
            expect(result.then).toBeDefined();
        });
    });

    describe("Subordinate views", function() {
        beforeEach(function() {
            this.fake_view = {
                reset: sinon.spy(),
                search: sinon.spy()
            };

            this.auth_stub = sinon.stub(Redd, "authenticate").returns(true);
            this.get_or_create_view_stub = sinon.stub(Redd, "get_or_create_view").returns(this.fake_view);
            this.navigate_stub = sinon.stub(Redd._router, "navigate");
        });

        afterEach(function() {
            this.navigate_stub.restore();
            this.get_or_create_view_stub.restore();
            this.auth_stub.restore();
        });

        it("should load the login view", function() {
            Redd.goto_login();

            expect(this.get_or_create_view_stub).toHaveBeenCalledWith("Login");
            expect(this.fake_view.reset).toHaveBeenCalledOnce();
            expect(this.navigate_stub).toHaveBeenCalledWith("login");
        });

        it("should logout and route to the login view", function() {
            this.set_current_user_stub = sinon.stub(Redd, "set_current_user");
            this.goto_login_stub = sinon.stub(Redd, "goto_login");

            Redd.goto_logout();

            expect(this.set_current_user_stub).toHaveBeenCalledWith(null);
            expect(this.goto_login_stub).toHaveBeenCalledOnce();

            this.goto_login_stub.restore();
            this.set_current_user_stub.restore();
        });

        it("should load the search view", function() {
            Redd.goto_search("test", "10", "2");

            expect(this.auth_stub).toHaveBeenCalledOnce();
            expect(this.get_or_create_view_stub).toHaveBeenCalledWith("Search");
            expect(this.fake_view.reset).toHaveBeenCalledWith("test");
            expect(this.fake_view.search).toHaveBeenCalledWith("test", "10", "2");
            expect(this.navigate_stub).toHaveBeenCalledWith("search/test/10/2");
        });

        it("should load the upload view", function() {
            Redd.goto_data_upload();

            expect(this.auth_stub).toHaveBeenCalledOnce();
            expect(this.get_or_create_view_stub).toHaveBeenCalledWith("DataUpload");
            expect(this.fake_view.reset).toHaveBeenCalledOnce();
            expect(this.navigate_stub).toHaveBeenCalledWith("upload");
        });

        it("should load the datasets view", function() {
            Redd.goto_datasets_search("all", null, "10", "2");

            expect(this.auth_stub).toHaveBeenCalledOnce();
            expect(this.get_or_create_view_stub).toHaveBeenCalledWith("DatasetsSearch");
            expect(this.fake_view.reset).toHaveBeenCalledWith("all", null, "10", "2");
            expect(this.navigate_stub).toHaveBeenCalledWith("datasets/all/10/2");
        });

        it("should load the dataset view", function() {
            Redd.goto_dataset_view("12");

            expect(this.auth_stub).toHaveBeenCalledOnce();
            expect(this.get_or_create_view_stub).toHaveBeenCalledWith("DatasetSearch");
            expect(this.fake_view.reset).toHaveBeenCalledWith("12");
            expect(this.navigate_stub).toHaveBeenCalledWith("dataset/12");
        });

        it("should load the dataset search view", function() {
            Redd.goto_dataset_search("12", "test", "10", "2");

            expect(this.auth_stub).toHaveBeenCalledOnce();
            expect(this.get_or_create_view_stub).toHaveBeenCalledWith("DatasetSearch");
            expect(this.fake_view.reset).toHaveBeenCalledWith("12", "test");
            expect(this.fake_view.search).toHaveBeenCalledWith("test", "10", "2");
            expect(this.navigate_stub).toHaveBeenCalledWith("dataset/12/search/test/10/2");
        });

        it("should render the 404 view but not change the url hash", function() {
            var old_location = window.location;

            Redd.goto_not_found();

            expect(this.get_or_create_view_stub).toHaveBeenCalledWith("NotFound");
            expect(this.fake_view.reset).toHaveBeenCalledOnce();
            expect(this.navigate_stub).not.toHaveBeenCalled();
            expect(window.location).toEqual(old_location);
        });

        it("should render the 500 view but not change the url hash", function() {
            var old_location = window.location;

            Redd.goto_server_error();

            expect(this.get_or_create_view_stub).toHaveBeenCalledWith("ServerError");
            expect(this.fake_view.reset).toHaveBeenCalledOnce();
            expect(this.navigate_stub).not.toHaveBeenCalled();
            expect(window.location).toEqual(old_location);
        });
    });
});


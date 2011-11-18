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
        this.topbar_stub = sinon.stub(Redd, "configure_topbar");
        this.refresh_notifications_stub = sinon.stub(Redd, "refresh_notifications");

        // Initialize with auth stubbed out
        Redd.initialize();

        this.auth_stub.restore();
        this.refresh_notifications_stub.restore();
        this.topbar_stub.restore();
        
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

            set_current_user_stub.restore();
            goto_login_stub.restore();
        });
    });

    describe("Ajax", function() {
        it("should check authentication on ajax requests", function() {
            var auth_stub = sinon.stub(Redd, "authenticate").returns(true);

            Redd.ajax({})

            expect(auth_stub).toHaveBeenCalledOnce();
        });

        it("should route to login if ajax returns 401", function () {
        });

        it("should call the original failure callback", function() {
        });

        it("should call the original success callback", function() {
        });

        it("should return a deferred", function() {
        });
    });
});


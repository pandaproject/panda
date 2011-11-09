describe("Index Router", function() {
    beforeEach(function() {
        // Fake out the Root view so its initialize won't fire
        FakeController = function() {}; 
        FakeController.prototype = PANDA.views.Root.prototype;
        this.fake_controller = new FakeController();

        this.controller_mock = sinon.mock(this.fake_controller); 
        this.router = new PANDA.routers.Index({ controller: this.fake_controller });

        try {
            Backbone.history.start({ silent:true });
        } catch(e) {}

        this.router.navigate("away");
    });

    it("should route to the login page", function() {
        this.controller_mock.expects("login").once();

        this.router.navigate("login", true);

        this.controller_mock.verify();
    });

    it("should route to the logout page", function() {
        this.controller_mock.expects("logout").once();

        this.router.navigate("logout", true);

        this.controller_mock.verify();
    });

    it("should route to the registration page", function() {
        this.controller_mock.expects("register").once();

        this.router.navigate("register", true);

        this.controller_mock.verify();
    });

    it("should route to search", function() {
        this.controller_mock.expects("search").withExactArgs(undefined, undefined, undefined).once();

        this.router.navigate("", true);

        this.controller_mock.verify();
    });

    it("should support search query", function() {
        this.controller_mock.expects("search").withExactArgs("query", undefined, undefined).once();

        this.router.navigate("search/query", true);

        this.controller_mock.verify();
    });

    it("should support search limit", function() {
        this.controller_mock.expects("search").withExactArgs("query", "10", undefined).once();

        this.router.navigate("search/query/10", true);

        this.controller_mock.verify();
    });

    it("should support search paging", function() {
        this.controller_mock.expects("search").withExactArgs("query", "10", "2").once();

        this.router.navigate("search/query/10/2", true);

        this.controller_mock.verify();
    });

    it("should route to the upload page", function() {
        this.controller_mock.expects("upload").once();

        this.router.navigate("upload", true);

        this.controller_mock.verify();
    });

    it("should route to dataset browsing", function() {
        this.controller_mock.expects("list_datasets").withExactArgs(undefined, undefined).once();

        this.router.navigate("datasets", true);

        this.controller_mock.verify();
    });

    it("should support dataset browsing limit", function() {
        this.controller_mock.expects("list_datasets").withExactArgs("10", undefined).once();

        this.router.navigate("datasets/10", true);

        this.controller_mock.verify();
    });

    it("should support dataset browser paging", function() {
        this.controller_mock.expects("list_datasets").withExactArgs("10", "2").once();

        this.router.navigate("datasets/10/2", true);

        this.controller_mock.verify();
    });

    it("should route to edit dataset", function() {
        this.controller_mock.expects("edit_dataset").withExactArgs("17").once();

        this.router.navigate("dataset/17", true);

        this.controller_mock.verify();
    });

    it("should route to per-dataset search", function() {
        this.controller_mock.expects("search_dataset").withExactArgs("17", "query", undefined, undefined).once();

        this.router.navigate("dataset/17/search/query", true);

        this.controller_mock.verify();
    });

    it("should support per-dataset search limit", function() {
        this.controller_mock.expects("search_dataset").withExactArgs("17", "query", "10", undefined).once();

        this.router.navigate("dataset/17/search/query/10", true);

        this.controller_mock.verify();
    });

    it("should support per-dataset search paging", function() {
        this.controller_mock.expects("search_dataset").withExactArgs("17", "query", "10", "2").once();

        this.router.navigate("dataset/17/search/query/10/2", true);

        this.controller_mock.verify();
    });

    it("should 404 on bad routes", function() {
        this.controller_mock.expects("not_found").withExactArgs("wtf/1/2/3").once();

        this.router.navigate("wtf/1/2/3", true);

        this.controller_mock.verify();
    });
});

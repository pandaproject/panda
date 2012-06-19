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
        this.controller_mock.expects("goto_login").once();

        this.router.navigate("login", true);

        this.controller_mock.verify();
    });

    it("should route to the logout page", function() {
        this.controller_mock.expects("goto_logout").once();

        this.router.navigate("logout", true);

        this.controller_mock.verify();
    });

    it("should route to search", function() {
        this.controller_mock.expects("goto_search").withExactArgs(undefined, undefined, undefined, undefined, undefined).once();

        this.router.navigate("", true);

        this.controller_mock.verify();
    });

    it("should support search query", function() {
        this.controller_mock.expects("goto_search").withExactArgs("all", "query", undefined, undefined, undefined).once();

        this.router.navigate("search/all/query", true);

        this.controller_mock.verify();
    });

    it("should support search limit", function() {
        this.controller_mock.expects("goto_search").withExactArgs("all", "query", "all", "10", undefined).once();

        this.router.navigate("search/all/query/all/10", true);

        this.controller_mock.verify();
    });

    it("should support search paging", function() {
        this.controller_mock.expects("goto_search").withExactArgs("all", "query", "all", "10", "2").once();

        this.router.navigate("search/all/query/all/10/2", true);

        this.controller_mock.verify();
    });

    it("should route to the data upload page", function() {
        this.controller_mock.expects("goto_data_upload").once();

        this.router.navigate("upload", true);

        this.controller_mock.verify();
    });

    it("should route to the per-dataset data upload page", function() {
        this.controller_mock.expects("goto_data_upload").withExactArgs("foo");

        this.router.navigate("dataset/foo/upload", true);

        this.controller_mock.verify();
    });

    it("should route to dataset search", function() {
        this.controller_mock.expects("goto_datasets_search").withExactArgs("all", undefined, undefined, undefined).once();

        this.router.navigate("datasets/all", true);

        this.controller_mock.verify();
    });

    it("should support dataset search query", function() {
        this.controller_mock.expects("goto_datasets_search").withExactArgs("all", "test", undefined, undefined).once();

        this.router.navigate("datasets/all/test", true);

        this.controller_mock.verify();
    });

    it("should support dataset search limit", function() {
        this.controller_mock.expects("goto_datasets_search").withExactArgs("all", "test", "10", undefined).once();

        this.router.navigate("datasets/all/test/10", true);

        this.controller_mock.verify();
    });

    it("should support dataset search paging", function() {
        this.controller_mock.expects("goto_datasets_search").withExactArgs("all", "test", "10", "2").once();

        this.router.navigate("datasets/all/test/10/2", true);

        this.controller_mock.verify();
    });

    it("should route to per-dataset search", function() {
        this.controller_mock.expects("goto_dataset_search").withExactArgs("17", "query", undefined, undefined, undefined).once();

        this.router.navigate("dataset/17/search/query", true);

        this.controller_mock.verify();
    });

    it("should support per-dataset search limit", function() {
        this.controller_mock.expects("goto_dataset_search").withExactArgs("17", "query", "all", "10", undefined).once();

        this.router.navigate("dataset/17/search/query/all/10", true);

        this.controller_mock.verify();
    });

    it("should support per-dataset search paging", function() {
        this.controller_mock.expects("goto_dataset_search").withExactArgs("17", "query", "all", "10", "2").once();
        this.router.navigate("dataset/17/search/query/all/10/2", true);

        this.controller_mock.verify();
    });

    it("should 404 on bad routes", function() {
        this.controller_mock.expects("goto_not_found").once();

        this.router.navigate("wtf/1/2/3", true);

        this.controller_mock.verify();
    });
});

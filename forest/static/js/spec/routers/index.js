describe("Index Router", function() {
    beforeEach(function() {
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

    it("should default to search", function() {
        var route_spy = sinon.spy();
        this.router.bind("route:search", route_spy);

        this.controller_mock.expects("search").withExactArgs(undefined, undefined, undefined).once();

        this.router.navigate("", true);

        expect(route_spy).toHaveBeenCalledOnce();
        expect(route_spy).toHaveBeenCalledWith();

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

    it("should support upload", function() {
        this.controller_mock.expects("upload").once();

        this.router.navigate("upload", true);

        this.controller_mock.verify();
    });

    it("should support dataset browsing", function() {
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

    it("should show a single dataset", function() {
        this.controller_mock.expects("edit_dataset").withExactArgs("17").once();

        this.router.navigate("dataset/17", true);

        this.controller_mock.verify();
    });

    it("should support per-dataset search", function() {
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

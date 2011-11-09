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

        this.controller_mock.expects("search").withArgs().once();

        this.router.navigate("", true);

        expect(route_spy).toHaveBeenCalledOnce();
        expect(route_spy).toHaveBeenCalledWith();

        this.controller_mock.verify();
    });

    it("should support search query", function() {
        this.controller_mock.expects("search").withArgs("query").once();

        this.router.navigate("search/query", true);

        this.controller_mock.verify();
    });

    it("should support search limit", function() {
        this.controller_mock.expects("search").withArgs("query", "10").once();

        this.router.navigate("search/query/10", true);

        this.controller_mock.verify();
    });

    it("should support search paging", function() {
        this.controller_mock.expects("search").withArgs("query", "10", "2").once();

        this.router.navigate("search/query/10/2", true);

        this.controller_mock.verify();
    });
});

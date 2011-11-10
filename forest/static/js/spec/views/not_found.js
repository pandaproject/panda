describe("Index Router", function() {
    beforeEach(function() {
        this.view = new PANDA.views.NotFound();

        sandbox({ id: "content" });
    });

    it("should render its template", function() {
        render_spy = sinon.spy(this.view, "render");

        this.view.reset();

        expect(render_spy).toHaveBeenCalledOnce();
        expect($("#content")).not.toBeEmpty();
    });
});


describe("Task model", function() {
    beforeEach(function() {
        // Intercept ajax requests
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
    });

    afterEach(function () {
        this.auth_stub.restore();
        this.xhr.restore();
    });

    it("should fetch the task", function() {
        var task = new PANDA.models.Task({ id : 1 });
        task.fetch();
        
        expect(this.requests.length).toEqual(1);

        this.requests[0].respond(200, { "Content-Type": "application/json" }, MOCK_XHR_RESPONSES.task);

        expect(task.get("task_name")).toEqual("redd.tasks.import.csv");
    });
});

describe("Task collection", function() {
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
    });

    afterEach(function () {
        this.auth_stub.restore();
        this.xhr.restore();
    });

    it("should fetch the tasks", function() {
        var tasks = new PANDA.collections.Tasks();
        tasks.fetch();
        
        expect(this.requests.length).toEqual(1);

        this.requests[0].respond(200, { "Content-Type": "application/json" }, MOCK_XHR_RESPONSES.tasks);

        expect(tasks.models.length).toEqual(1);
    });
});

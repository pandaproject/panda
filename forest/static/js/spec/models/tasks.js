describe("Task model", function() {
    beforeEach(function() {
        this.xhr = sinon.useFakeXMLHttpRequest();
        var requests = this.requests = [];

        this.xhr.onCreate = function(xhr) {
            requests.push(xhr);
        };
    });

    afterEach(function () {
        this.xhr.restore();
    });

    it("should fetch the task", function() {
        var task = new PANDA.models.Task({ id : 1 });
        task.fetch();
        
        expect(this.requests.length).toEqual(1);

        this.requests[0].respond(200, { "Content-Type": "application/json" }, MOCK_XHR_RESPONSES.task);

        expect(task.get("task_name")).toEqual("redd.tasks.DatasetImportTask");
    });
});

describe("Task collection", function() {
    beforeEach(function() {
        this.xhr = sinon.useFakeXMLHttpRequest();
        var requests = this.requests = [];

        this.xhr.onCreate = function(xhr) {
            requests.push(xhr);
        };
    });

    afterEach(function () {
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

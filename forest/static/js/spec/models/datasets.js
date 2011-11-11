describe("Dataset model", function() {
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

    it("should fetch the dataset", function() {
        var dataset = new PANDA.models.Dataset({ id : 1 });
        dataset.fetch();

        expect(this.requests.length).toEqual(1);

        this.requests[0].respond(200, { "Content-Type": "application/json" }, MOCK_XHR_RESPONSES.dataset);

        expect(dataset.get("name")).toEqual("Test");
    });

    it("should parse the related models", function() {
        var dataset = new PANDA.models.Dataset();

        response = $.parseJSON(MOCK_XHR_RESPONSES.dataset);
        response = dataset.parse(response);

        expect(dataset.creator).not.toBeNull();
        expect(dataset.creator.get("username")).toEqual("panda");
        expect(response.creator).toBeUndefined();

        expect(dataset.data_upload).not.toBeNull();
        expect(dataset.data_upload.get("original_filename")).toEqual("contributors.csv");
        expect(response.data_upload).toBeUndefined();

        expect(dataset.current_task).not.toBeNull();
        expect(dataset.current_task.get("task_name")).toEqual("redd.tasks.DatasetImportTask");
        expect(response.current_task).toBeUndefined();
    });

    it("should serialize related models as URIs by default", function() {
        var dataset = new PANDA.models.Dataset($.parseJSON(MOCK_XHR_RESPONSES.dataset));

        json = dataset.toJSON();

        expect(json.creator).toEqual("/api/1.0/user/1/");
        expect(json.data_upload).toEqual("/api/1.0/upload/1/");
        expect(json.current_task).toEqual("/api/1.0/task/1/");
    });

    it("should serialize related models in full when specified", function() {
        var dataset = new PANDA.models.Dataset($.parseJSON(MOCK_XHR_RESPONSES.dataset));

        json = dataset.toJSON(true);

        expect(json.creator).not.toBeNull();
        expect(json.creator.username).toEqual("panda");

        expect(json.data_upload).not.toBeNull();
        expect(json.data_upload.original_filename).toEqual("contributors.csv");

        expect(json.current_task).not.toBeNull();
        expect(json.current_task.task_name).toEqual("redd.tasks.DatasetImportTask");
    });

    xit("should tell the server to import data", function() {
        // TODO
    });

    xit("should serialize embedded search data", function() {
        // TODO
    });

    xit("should execute a search on just this dataset", function() {
        // TODO
    });

    xit("should parse search results", function() {
        // TODO
    });
});

xdescribe("Dataset collection", function() {
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

    xit("should fetch the datasets", function() {
        // TODO
    });

    xit("should parse paging metadata", function() {
        // TODO
    });

    xit("should search all datasets", function() {
        // TODO
    });

    xit("should serialize search results from all datasets", function() {
        // TODO
    });
});

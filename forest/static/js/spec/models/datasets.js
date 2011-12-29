describe("Dataset model", function() {
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
        expect(dataset.creator.get("email")).toEqual("panda@pandaproject.net");
        expect(response.creator).toBeUndefined();

        expect(dataset.uploads).not.toBeNull();
        expect(dataset.initial_upload).not.toBeNull();

        expect(dataset.current_task).not.toBeNull();
        expect(dataset.current_task.get("task_name")).toEqual("redd.tasks.import.csv");
        expect(response.current_task).toBeUndefined();

        expect(dataset.categories).not.toBeNull();
        expect(dataset.categories.length).toEqual(0);
    });

    it("should serialize related models as URIs by default", function() {
        var dataset = new PANDA.models.Dataset($.parseJSON(MOCK_XHR_RESPONSES.dataset));

        json = dataset.toJSON();

        expect(json.creator).toEqual("/api/1.0/user/1/");
        expect(json.uploads).toEqual(["/api/1.0/upload/1/"]);
        expect(json.initial_upload).toEqual("/api/1.0/upload/1/");
        expect(json.current_task).toEqual("/api/1.0/task/1/");
        expect(json.categories).toEqual([]);
    });

    it("should serialize related models in full when specified", function() {
        var dataset = new PANDA.models.Dataset($.parseJSON(MOCK_XHR_RESPONSES.dataset));

        json = dataset.toJSON(true);

        expect(json.creator).not.toBeNull();
        expect(json.creator.email).toEqual("panda@pandaproject.net");

        expect(json.uploads.length).toEqual(1);
        expect(json.initial_upload).not.toBeNull();

        expect(json.current_task).not.toBeNull();
        expect(json.current_task.task_name).toEqual("redd.tasks.import.csv");
        
        expect(json.categories).not.toBeNull();
        expect(json.categories).toEqual([]);
    });

    it("should tell the server to import data", function() {
        var dataset = new PANDA.models.Dataset($.parseJSON(MOCK_XHR_RESPONSES.dataset));

        success_spy = sinon.spy();

        dataset.import_data(1, success_spy);

        expect(this.requests.length).toEqual(1);
        expect(this.requests[0].url).toEqual("/api/1.0/dataset/test/import/1/");

        this.requests[0].respond(200, { "Content-Type": "application/json" }, MOCK_XHR_RESPONSES.dataset);

        expect(success_spy).toHaveBeenCalledWith(dataset);
    });

    it("should execute a search on just this dataset", function() {
        var dataset = new PANDA.models.Dataset($.parseJSON(MOCK_XHR_RESPONSES.dataset));
        
        dataset.search("Tribune", 10, 1);

        expect(this.requests.length).toEqual(1);
        
        this.requests[0].respond(200, { "Content-Type": "application/json" }, MOCK_XHR_RESPONSES.dataset_search);

        expect(dataset.data.models.length).toEqual(2)
        expect(dataset.data.models[0].attributes.data[1]).toEqual("Brian");
        expect(dataset.data.models[1].attributes.data[1]).toEqual("Joseph");
    });

    it("should serialize embedded search data", function() {
        var dataset = new PANDA.models.Dataset($.parseJSON(MOCK_XHR_RESPONSES.dataset));
        
        dataset.data.meta.limit = PANDA.settings.PANDA_DEFAULT_SEARCH_ROWS;
        dataset.data.meta.offset = 0;
        dataset.process_search_results($.parseJSON(MOCK_XHR_RESPONSES.dataset_search));

        results = dataset.results();

        expect(results.name).toEqual("Test");
        expect(results.data.length).toEqual(2);
    });

    it("should parse search results", function() {
        var dataset = new PANDA.models.Dataset($.parseJSON(MOCK_XHR_RESPONSES.dataset));
        
        dataset.process_search_results($.parseJSON(MOCK_XHR_RESPONSES.dataset_search));

        expect(dataset.data.length).toEqual(2);
    });
});

describe("Dataset collection", function() {
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

    it("should fetch the datasets", function() {
        var datasets = new PANDA.collections.Datasets();
        datasets.fetch();
        
        expect(this.requests.length).toEqual(1);

        this.requests[0].respond(200, { "Content-Type": "application/json" }, MOCK_XHR_RESPONSES.datasets);

        expect(datasets.models.length).toEqual(1);
        expect(datasets.models[0].get("name")).toEqual("Test");
    });

    it("should parse paging metadata", function() {
        var datasets = new PANDA.collections.Datasets();

        response = $.parseJSON(MOCK_XHR_RESPONSES.datasets);
        response = datasets.parse(response);

        expect(datasets.meta).not.toBeNull();
        expect(datasets.meta.offset).toEqual(0);
        expect(datasets.meta.page).toEqual(1);
    });

    it("should search all datasets", function() {
        var datasets = new PANDA.collections.Datasets();
        datasets.search("Tribune");

        expect(this.requests.length).toEqual(1);

        this.requests[0].respond(200, { "Content-Type": "application/json" }, MOCK_XHR_RESPONSES.search);

        expect(datasets.models.length).toEqual(1);
        expect(datasets.models[0].data.models.length).toEqual(2);
        expect(datasets.models[0].data.models[0].attributes.data[1]).toEqual("Brian");
        expect(datasets.models[0].data.models[1].attributes.data[1]).toEqual("Joseph");
    });

    it("should serialize search results from all datasets", function() {
        var datasets = new PANDA.collections.Datasets();
        datasets.search("Tribune");

        expect(this.requests.length).toEqual(1);

        this.requests[0].respond(200, { "Content-Type": "application/json" }, MOCK_XHR_RESPONSES.search);

        results = datasets.results();
        
        expect(results.meta).toEqual(datasets.meta);
        expect(results.datasets.length).toEqual(1);
        expect(results.datasets[0].name).toEqual("Test");
        expect(results.datasets[0].data.length).toEqual(2);
    });
});

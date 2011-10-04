(function() {
    window.Redd = {};
    Redd.controllers = {};
    Redd.model = {};
    Redd.app = {};
    Redd.ui = {};

    Redd.model.Dataset = Backbone.Model.extend({
        urlRoot: "/api/1.0/dataset"
    });

    Redd.model.DatasetSet = Backbone.Collection.extend({
        model: Redd.model.Dataset,
        url: "/api/1.0/dataset"
    });

    Redd.model.Datum = Backbone.Model.extend({
        urlRoot: "/api/1.0/data"
    });

    Redd.model.DatumSet = Backbone.Collection.extend({
        model: Redd.model.Datum,
        url: "/api/1.0/data",

        search: function(query) {
            $.getJSON(
                this.url() + '/search',
                { q: query },
                _.bind(function(response) {
                    _.each(response.objects, function(obj) {
                        this.add(obj);
                    });
                }, this));
        }
    });

    window.Datasets = new Redd.model.DatasetSet();
    window.Data = new Redd.model.DatumSet();
})();

/*(function() {
    window.Redd = {};
    
    Redd.API = "/api/1.0";

    Redd.create_dataset = function(name, data_upload_id, success_callback) {
        data = {
            name: name,
            data_upload: { id: data_upload_id }
        }

        $.ajax(Redd.API + "/dataset/", {
            type: "POST",
            data: JSON.stringify(data),
            dataType: "json",
            contentType: "application/json", 
            success: function(data, textStatus, jqXHR) {
                success_callback();
            }
        });    
    }

    Redd.search_data = function(query, limit, offset, success_callback) {
        data = {
            q: query,
            limit: limit,
            offset: offset
        }

        $.ajax(Redd.API + "/data/search/", {
            type: "GET",
            data: data,
            dataType: "json",
            success: function(data, textStatus, jqXHR) {
                success_callback(data);
            }
        }); 
    }
})();*/

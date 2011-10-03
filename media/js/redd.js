(function() {
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
})();

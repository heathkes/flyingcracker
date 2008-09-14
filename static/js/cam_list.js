var cam_list = {
    
    init: function() {
        YAHOO.util.Event.addListener(document.getElementById('id-category'), 'change', cam_list.request_list_func);
        YAHOO.util.Event.addListener(document.getElementById('id-image'), 'change', cam_list.request_image_func);
    },
    
    request_list_func: function(e) {
        // determine the id of the selected category
        var select = document.getElementById('id-category');
        
        // POST a request for new data
        post_url = '/cam/list/?xhr';
        var post_data = 'cat=' + select.value;
        var cObj = YAHOO.util.Connect.asyncRequest('POST', post_url, cam_list.request_list_callback, post_data);
    },
    
    request_list_callback: {
        success: function(o) {
            // This turns the JSON string into a JavaScript object.
            var response_obj = eval('(' + o.responseText + ')');
            
			var image_select = document.getElementById('id-image');
            // remove existing options
            image_select.options.length = 0;
            // Add the image ids
            cam_list.add_option(image_select.options, 0, '--Select webcam--')
            objs = response_obj.images;
            for (var i=0; i<objs.length; i++) {
                cam_list.add_option(image_select.options, objs[i].id, objs[i].title)
            }
            Set_Cookie("cam_category", objs.category, 7, '/', '', '')
        },
    
        failure: function(o) {
            var a = 1; // alert('An error has occurred');
        }
    
    },

    request_image_func: function(e) {
        // determine the id of the selected image
        var select = document.getElementById('id-image');
        
        // POST a request for new data
        post_url = '/cam/image/?xhr';
        var post_data = 'id=' + select.value;
        var cObj = YAHOO.util.Connect.asyncRequest('POST', post_url, cam_list.request_image_callback, post_data);
    },
    
    request_image_callback: {
        success: function(o) {
            // This turns the JSON string into a JavaScript object.
            try {
                var response_obj = YAHOO.lang.JSON.parse(o.responseText);
                var image = response_obj.image;
            }
            catch (e) {
                alert("Invalid server response in cam_list.js ["+o.responseText+"], please inform CracklyFinger")
            }
            if (image) {
                var el = document.getElementById('cam-image');
                el.alt = image.title;
                el.src = image.url;
            }
        },
    
        failure: function(o) {
            var a = 1; // alert('An error has occurred');
        }
    
    },
    
    add_option: function(sel,id,title) {
        var newElem = document.createElement("option");
        newElem.text = title;
        newElem.value = id;
        sel.add(newElem)
    }
};

// YAHOO.util.Event.addListener(window, 'load', cam_list.init);
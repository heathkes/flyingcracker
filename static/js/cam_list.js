var cam_list = {
    
    init: function() {
        YAHOO.util.Event.addListener(document.getElementById('id_category'), 'change', cam_list.request_func);
    },
    
    request_func: function(e) {
        // determine the id of the selected category
        var category_select = document.getElementById('id_category');
        
        // POST a request for new data
        post_url = '/cam/cam_list/?xhr';
        var post_data = 'cat=' + category_select.value;
        var cObj = YAHOO.util.Connect.asyncRequest('POST', post_url, cam_list.ajax_callback, post_data);
    },
    
    ajax_callback: {
        success: function(o) {
            // This turns the JSON string into a JavaScript object.
            var response_obj = eval('(' + o.responseText + ')');
            
			var image_select = document.getElementById('id_image');
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
    
    add_option: function(sel,id,title) {
        var newElem = document.createElement("option");
        newElem.text = title;
        newElem.value = id;
        sel.add(newElem)
    }
};

YAHOO.util.Event.addListener(window, 'load', cam_list.init);
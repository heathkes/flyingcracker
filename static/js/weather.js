function toggleUnits(element) {
    var elements = YAHOO.util.Dom.getElementsByClassName('curr_units', 'span');
    
    if (elements) {
        var state = elements[0].style.display;
        if (state == 'none')
            state = '';
        else
            state = 'none';
            
        for (i=0; i<elements.length; i++) {
            elements[i].style.display = state;
        }
        Set_Cookie("curr_weather_show_units", state, 7, '/', '', '');
    }
    element.setAttribute("toggled", element.getAttribute("toggled") != "true");
}

function toggleLabels(element) {
    var elements = YAHOO.util.Dom.getElementsByClassName('curr_title', 'span');
    if (elements) {
        var state = elements[0].style.visibility;
        if (state == 'hidden')
            state = 'visible';
        else
            state = 'hidden';
            
        for (i=0; i<elements.length; i++) {
            elements[i].style.visibility = state;
        }
        Set_Cookie("curr_weather_show_titles", state, 7, '/', '', '');
    }
    element.setAttribute("toggled", element.getAttribute("toggled") != "true");
}

var weather_units = {
    
    init: function() {
        // find all temp_value elements, assign a click handler
        weather_units.assign_listener('temp_value', 'curr_weather', weather_units.temp_change_units);
        weather_units.assign_listener('baro_value', 'curr_weather', weather_units.baro_change_units);
        weather_units.assign_listener('speed_value', 'curr_weather', weather_units.speed_change_units);
    },

    assign_listener: function(cl, root, func) {
        // find all temp_value elements, assign a click handler
        var elements = YAHOO.util.Dom.getElementsByClassName(cl, '', root);
        for (i=0; i<elements.length; i++) {
            YAHOO.util.Event.addListener(elements[i], 'click', func, elements[i]);
        }
    },
    
    temp_change_units: function(e, el) {
        weather_units.request_unit_change('T', el);
    },
    
    baro_change_units: function(e, el) {
        weather_units.request_unit_change('B', el);
    },
    
    speed_change_units: function(e, el) {
        weather_units.request_unit_change('S', el);
    },
    
    request_unit_change: function(unit_type, el) {
        var value = el.textContent;
        var parent = el.parentNode;
        var unit_els = YAHOO.util.Dom.getElementsByClassName('curr_units', 'span', parent);
        var curr_unit = unit_els[0].textContent;
        // make async request for a new unit for this type
        post_url = '/weather/unitchange/';
        var post_data = 'unit_type=' + unit_type;
        post_data += '&curr_unit=' + curr_unit;
        post_data += '&value=' + value;
        var callback = {
            success: weather_units.unit_change_callback_success,
            failure: weather_units.unit_change_callback_failure,
            scope: weather_units,
            argument: [el]
        }
        var cObj = YAHOO.util.Connect.asyncRequest('POST', post_url, callback, post_data);
    },
    
    unit_change_callback_success: function(o) {
        // This turns the JSON string into a JavaScript object.
        try {
            var response_obj = YAHOO.lang.JSON.parse(o.responseText);
        }
        catch (e) {
            alert("Invalid server response in unit_change_callback_success "+o.responseText+", please contact flyingcracker.com")
        }
        if (response_obj)
            this.unit_update(o.argument[0], response_obj.new_value, response_obj.new_unit);
    },
    
    unit_change_callback_failure: function(o) {
        alert('An error occurred when retrieving response from request_unit_change');
    },
    
    unit_update: function(el, new_value, new_unit) {
        // alert('changing element "'+el+'": value='+new_value+' unit:'+new_unit);
        el.textContent = new_value;
        var parent = el.parentNode;
        var unit_els = YAHOO.util.Dom.getElementsByClassName('curr_units', 'span', parent);
        unit_els[0].textContent = new_unit;
    }
    
};
YAHOO.util.Event.addListener(window, 'load', weather_units.init);


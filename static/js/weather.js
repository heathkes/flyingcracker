var current_weather = {
    
    title_toggle: function(e) {
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
        }
    },
    
    unit_toggle: function(e) {
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
        }
    },
    
    init: function() {
        var titleButton = new YAHOO.widget.Button(
            "title_toggle",  // Source element id
            { 
                type: "checkbox",
                label: "Labels"
            }
        );
        titleButton.addListener("click", current_weather.title_toggle);
        
        var unitButton = new YAHOO.widget.Button(
            "unit_toggle",  // Source element id
            { 
                type: "checkbox",
                label: "Units"
            }
        );
        unitButton.addListener("click", current_weather.unit_toggle);
    }
};
YAHOO.util.Event.addListener(window, 'load', current_weather.init);


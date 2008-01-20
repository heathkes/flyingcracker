var current_weather = {
    init: function() {
        var oButton = new YAHOO.widget.Button(
            "title_toggle",  // Source element id
            { 
                type: "checkbox",
                label: "Labels"
            }
        );
        oButton.addListener("click", current_weather.title_toggle);
    },
    
    title_toggle: function(e) {
        var elements = YAHOO.util.Dom.getElementsByClassName('curr_title', 'span');
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
    }
};
YAHOO.util.Event.addListener(window, 'load', current_weather.init);


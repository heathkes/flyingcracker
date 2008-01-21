var current_weather = {
    
    init: function() {
        current_weather.weather_div = document.getElementById("curr_weather");
        
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
    },
    
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
        // Set up the animation on the results div.
        var weather_fade_out = new YAHOO.util.Anim(current_weather.weather_div,
            { opacity: { to: 0 } }, 0.5, YAHOO.util.Easing.easeOut);
        
        var weather_fade_in = new YAHOO.util.Anim(current_weather.weather_div,
            { opacity: { to: 1 } }, 0.5, YAHOO.util.Easing.easeIn);
        
        var elements = YAHOO.util.Dom.getElementsByClassName('curr_units', 'span');
        
        if (elements) {
            var state = elements[0].style.display;
            if (state == 'none')
                state = '';
            else
                state = 'none';
                
            weather_fade_out.onComplete.subscribe(function() {
                for (i=0; i<elements.length; i++) {
                    elements[i].style.display = state;
                }
                weather_fade_in.animate();
            });
            
            weather_fade_out.animate();
        }
    }
};
YAHOO.util.Event.addListener(window, 'load', current_weather.init);


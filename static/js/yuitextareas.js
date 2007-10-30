var myEditor = new YAHOO.widget.Editor('id_body', { 
	    height: '600px', 
	    width: '100%', 
	    dompath: true, //Turns on the bar at the bottom 
	    animate: true //Animates the opening, closing and moving of Editor windows 
	}); 
myEditor.render();

YAHOO.util.Event.on('post_form', 'submit', function(ev) {
        YAHOO.util.Event.stopEvent(ev);
        myEditor.saveHTML();
        YAHOO.util.Dom.get('post_form').submit();
});
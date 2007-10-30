var myEditor = new YAHOO.widget.Editor('id_body', { 
	    height: '600px', 
	    width: '100%',
        handleSubmit: true, // Automatically saves the HTML in the textarea on submit
	    dompath: true, //Turns on the bar at the bottom 
	    animate: true //Animates the opening, closing and moving of Editor windows 
	}); 
myEditor.render();
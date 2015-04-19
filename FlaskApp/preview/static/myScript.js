$(document).ready( function() {
	
	$.getJSON("/getDevicesJSON", function(data) {
		
		$("table").append("<thead><th>ID</th><th>Mountpoint</th><th>Source</th><th>Info</th><th>Exported</th><th>Target</th></thead><tbody>");
		
		$.each (data.result, function() {
			
			$("table").append("<tr><th scope=\"row\">" + this["id"] + "</th><td>" + this["mountpoint"] + "</td><td>" + this["source"] + "</td><td>" + this["info"] + "</td><td>" + this["exported"] + "</td><td>" + this["target"] + "</td></tr>");
			
		});
		$("table").append("</tbody>");
		
	});
	
});
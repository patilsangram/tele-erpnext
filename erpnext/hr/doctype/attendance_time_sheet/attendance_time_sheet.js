
cur_frm.cscript.in_time = function(doc,cdt,cdn){
	record = locals[cdt][cdn];
	validate_time_entries();
}

cur_frm.cscript.out_time = function(doc,cdt,cdn){
	record = locals[cdt][cdn];
	validate_time_entries(record);
}

validate_time_entries = function(record){
	console.log(record)
}
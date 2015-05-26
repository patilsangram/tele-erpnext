// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

cur_frm.add_fetch('employee', 'company', 'company');
cur_frm.add_fetch('employee', 'employee_name', 'employee_name');

cur_frm.cscript.onload = function(doc, cdt, cdn) {
	if(doc.__islocal) cur_frm.set_value("att_date", get_today());
}

cur_frm.fields_dict.employee.get_query = function(doc,cdt,cdn) {
	return{
		query: "erpnext.controllers.queries.employee_query"
	}	
}

cur_frm.cscript.in_time = function(doc,cdt,cdn){
	validate_in_out_time_entries(cdt,cdn);
	cur_frm.refresh_field("task_details")
}

cur_frm.cscript.out_time = function(doc,cdt,cdn){
	validate_in_out_time_entries(record);
	cur_frm.refresh_field("task_details")
}

validate_in_out_time_entries = function(cdt,cdn){
	/*
		get the in_time and out time and validate the entries
		check whether in_time is greater then out_time
	*/
	var record = frappe.get_doc(cdt, cdn);

	_in = to_date(record.in_time);
	_out = to_date(record.out_time);

	if (_in > _out){
		frappe.msgprint("In Time can not be greater than Out time");
		record.in_time = ""
		cur_frm.refresh_field("task_details")
	}
}

to_date = function(time){
	hr_min_sec = time.split(":");
	return new Date(2015, 05, 26, parseInt(hr_min_sec[0]), parseInt(hr_min_sec[1]), parseInt(hr_min_sec[2]), 0)
}

cur_frm.cscript.validate = function(doc, cdt, cdn){
	return validate_time_entries(doc, cdt, cdn);
}

validate_time_entries = function(doc, cdt, cdn){
	/*
		validate the in_time of first record and out time of second record
	*/

	var records = doc.task_details

	for(var i = 0; i < records.length; i++){
		if( i+1 < records.length){
			_out = to_date(records[i].out_time);
			_in = to_date(records[i+1].in_time);

			if(_in < _out){
				frappe.msgprint("In Time of record : "+ records[i+1].idx +" must be greater than Out Time of record : "+records[i].idx);
				records[i+1].in_time = "";
				cur_frm.refresh_field("task_details");
				cur_frm.refresh();
			}
		}
	}

	return true;
}
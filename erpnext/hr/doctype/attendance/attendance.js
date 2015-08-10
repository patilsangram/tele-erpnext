// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

cur_frm.add_fetch('employee', 'company', 'company');
cur_frm.add_fetch('employee', 'employee_name', 'employee_name');

cur_frm.cscript.onload = function(doc, cdt, cdn) {
	if(doc.__islocal) cur_frm.set_value("att_date", get_today());
	hide_sections(doc.status)
}

cur_frm.fields_dict.employee.get_query = function(doc,cdt,cdn) {
	return{
		query: "erpnext.controllers.queries.employee_query"
	}
}

cur_frm.cscript.status = function(doc){
	hide_sections(doc.status)
}

hide_sections = function(status){
	var is_absent = (status == "Absent")? 1: 0
	cur_frm.set_df_property("time_sheet", "hidden", is_absent);
	cur_frm.set_df_property("total_hours", "hidden", is_absent)
}

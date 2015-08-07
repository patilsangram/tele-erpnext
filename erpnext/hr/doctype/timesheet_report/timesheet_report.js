cur_frm.cscript.onload = function(doc){
    doc.employee = "";
    doc.html_code = "";
    // autofill from date and to date
	frappe.call({
		method:"erpnext.hr.doctype.timesheet_report.timesheet_report.get_from_to_dates",
		callback: function(r){
			if(r.message){
				cur_frm.doc.from_date = r.message.from_date;
				cur_frm.doc.to_date = r.message.to_date;
                cur_frm.refresh_fields(["from_date","to_date"])
			}
		}
	})
}

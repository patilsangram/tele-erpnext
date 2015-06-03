frappe.ui.form.on("Issue", {
	"refresh": function(frm) {
		if(frm.doc.status==="Open") {
			frm.add_custom_button("Close", function() {
				frm.set_value("status", "Closed");
				frm.save();
			});
		} else {
			frm.add_custom_button("Reopen", function() {
				frm.set_value("status", "Open");
				frm.save();
			});
		}
	}
});

cur_frm.add_fetch('customer','customer_name','customer_name');
cur_frm.add_fetch('location_id','customer','customer');
cur_frm.add_fetch('contact','customer','customer');
cur_frm.add_fetch('contact','location_id','location_id');
cur_frm.add_fetch('contact','mobile_no','phone');
cur_frm.add_fetch('contact','email_id','raised_by');

cur_frm.cscript.refresh = function(doc, cdt, cdn){
	set_notification_mode(doc)
}

cur_frm.cscript.onload = function(doc, cdt, cdn){
	set_notification_mode(doc)
}

cur_frm.cscript.customer = function(doc, cdt, cdn){
	/*
		clear fields
		set the customer name
	*/

	doc.contact = "";
	doc.location_id = "";
	doc.raised_by = "";
	doc.phone = "";
	doc.contact_name = "";

	cur_frm.refresh_fields();
}

cur_frm.cscript.contact = function(doc, cdt, cdn){
	// get notification mode and set the checkbox
	
	set_notification_mode(doc);
}

set_notification_mode = function(doc){
	/*
		check the notification mode from Contact and checked the respective checkbox
	*/
	var mode = "";
	if(doc.contact){
		// Get Contact doc 
		frappe.model.with_doc('Contact', doc.contact, function() {
	  		d = frappe.model.get_doc('Contact', doc.contact);
	  		mode = d.notification_mode;
	  		// Set the checkbox to checked state
	  		$('.is-email').prop('checked', mode == 'Via Email'? true: false);
			$('.is-sms').prop('checked', mode == 'Via SMS'? true: false);
			$('.is-both').prop('checked', mode == 'Both'? true: false);
			$('.is-comment').prop('checked',mode != 'Via Email' && mode != 'Via SMS' && mode != 'Both'?true:false);
		})

		cur_frm.refresh_fields();
	}
}

cur_frm.fields_dict['location_id'].get_query = function(doc, cdt, cdn) {
	return {
		filters:{ 'customer': doc.customer }
	}
}

cur_frm.fields_dict['contact'].get_query = function(doc, cdt, cdn) {
	return {
		filters:{
			'location_id': doc.location_id,
			'customer': doc.customer 
		}
	}
}
set_notification_mode = function(contact){
	/*
		check the notification mode from Contact and checked the respective checkbox
	*/
	var mode = "";
	if(contact){
		// Get Contact doc 
		frappe.model.with_doc('Contact', contact, function() {
	  		d = frappe.model.get_doc('Contact', contact);
	  		mode = d.notification_mode;
	  		// Set the checkbox to checked state
	  		$('.is-email').prop('checked', mode == 'Via Email'? true: false);
			$('.is-sms').prop('checked', mode == 'Via SMS'? true: false);
			$('.is-both').prop('checked', mode == 'Both'? true: false);
			$('.is-comment').prop('checked',mode != 'Via Email' && mode != 'Via SMS' && mode != 'Both'?true:false);
		})

		cur_frm.refresh_fields();
	}
	else
		$('.is-comment').prop('checked',true);
}
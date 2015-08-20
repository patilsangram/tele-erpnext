// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

{% include 'controllers/js/contact_address_common.js' %};

frappe.ui.form.on("Address", "validate", function(frm) {
	// clear linked customer / supplier / sales partner on saving...
	$.each(["Customer", "Supplier", "Sales Partner", "Lead"], function(i, doctype) {
		var name = frm.doc[doctype.toLowerCase().replace(/ /g, "_")];
		if(name && locals[doctype] && locals[doctype][name])
			frappe.model.remove_from_locals(doctype, name);
	});
});

frappe.ui.form.on("Address", "refresh", function(cur_frm) {
	is_customer(cur_frm.doc)
});

cur_frm.cscript.customer = function(doc){
	is_customer(doc);
}

cur_frm.cscript.validate = function(doc){
	is_customer(doc);
}

is_customer = function(doc){
	// If customer the hide fields
	if(doc.customer){
		doc.address_title = "";
		cur_frm.set_df_property("location_name", "reqd", 1);
		cur_frm.set_df_property("address_title", "read_only", 1);
	}
	else{
		// unhide fields and set customer and customer name to null
		doc.customer = "";
		doc.customer_name = "";
		doc.location_id = "";
		cur_frm.set_df_property("location_name", "reqd", 0);
	}
	cur_frm.refresh_fields();
}

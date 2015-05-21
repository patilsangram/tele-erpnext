// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

{% include 'controllers/js/contact_address_common.js' %};

cur_frm.email_field = "email_id";
frappe.ui.form.on("Contact", "validate", function(frm) {
	// clear linked customer / supplier / sales partner on saving...
	$.each(["Customer", "Supplier", "Sales Partner"], function(i, doctype) {
		var name = frm.doc[doctype.toLowerCase().replace(/ /g, "_")];
		if(name && locals[doctype] && locals[doctype][name])
			frappe.model.remove_from_locals(doctype, name);
	});
});

cur_frm.fields_dict['location_id'].get_query = function(doc,cdt,cdn) {
	return {
		query: "erpnext.utilities.doctype.address.address.get_customer_addresses",
		filters:{
			'customer': doc.customer
		}
	}
}
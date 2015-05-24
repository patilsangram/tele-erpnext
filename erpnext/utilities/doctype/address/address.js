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

/*frappe.ui.form.on("Address", "onload", function(cur_frm) {
	is_customer(cur_frm.doc)
});*/

cur_frm.cscript.customer = function(doc){
	is_customer(doc);
}

is_customer = function(doc){
	// If customer the hide fields
	flds = ["supplier","supplier_name","lead","lead_name","sales_partner","address_title"];
	if(doc.customer){
		// address title fields to readonly
		// hide and set other fields to null

		/*var refdoc = frappe.get_doc("Customer", doc.customer);
		cur_frm.set_value('customer_name', refdoc.customer_name);*/

		/*doc.supplier = null;
		doc.supplier_name = null;
		doc.lead = null;
		doc.lead_name = null;
		doc.sales_partner = null;*/
		
		// hide_field(flds);
		// unhide_field(["location_id","customer_name"]);

		make_fields_readonly(true);
		cur_frm.refresh_fields();
	}
	else{
		// unhide fields and set customer and customer name to null
		doc.customer = "";
		doc.customer_name = "";
		doc.location_id = "";

		// hide_field(["location_id"]);
		// unhide_field(flds);

		make_fields_readonly(false);
		cur_frm.refresh_fields();
	}
}

make_fields_readonly = function(is_readonly){
	read_only = 0
	
	is_readonly? read_only=1 : read_only=0

	cur_frm.set_df_property("supplier", "read_only", read_only);
	cur_frm.set_df_property("lead", "read_only", read_only);
	cur_frm.set_df_property("sales_partner", "read_only", read_only);
}
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cstr, add_days, date_diff
from frappe import _
from frappe.utils.csvutils import UnicodeWriter
from frappe.model.document import Document
import datetime as dt

class UploadAttendance(Document):
	pass

@frappe.whitelist()
def get_template():
	if not frappe.has_permission("Attendance", "create"):
		raise frappe.PermissionError

	args = frappe.local.form_dict

	w = UnicodeWriter()
	w = add_header(w)

	w = add_data(w, args)

	# write out response as a type csv
	frappe.response['result'] = cstr(w.getvalue())
	frappe.response['type'] = 'csv'
	frappe.response['doctype'] = "Attendance"

def add_header(w):
	status = ", ".join((frappe.get_meta("Attendance").get_field("status").options or "").strip().split("\n"))
	w.writerow(["Notes:"])
	w.writerow(["Please do not change the template headings"])
	w.writerow(["Status should be one of these values: " + status])
	w.writerow(["If you are overwriting existing attendance records, 'ID' column mandatory"])
	w.writerow(["ID", "Employee", "Employee Name", "Date", "Status",
		"Fiscal Year", "Company", "Naming Series","Task Record ID","Task","In Time","Out Time","Description"])
	return w

def add_data(w, args):
	from erpnext.accounts.utils import get_fiscal_year

	dates = get_dates(args)
	employees = get_active_employees()
	existing_attendance_records = get_existing_attendance_records(args)
	
	for date in dates:
		for employee in employees:
			existing_attendance = {}
			if existing_attendance_records \
				and tuple([date, employee.name]) in existing_attendance_records:
					existing_attendance = existing_attendance_records[tuple([date, employee.name])]

			if existing_attendance and existing_attendance.get("task_details"):
				for i in range(len(existing_attendance.get("task_details"))):
					row = get_row(i, existing_attendance, employee, date);
					w.writerow(row)
			else:
				row = get_row(0, None, employee, date)				
				w.writerow(row)
	return w

def get_row(i, record, employee, date):
	from erpnext.accounts.utils import get_fiscal_year
	return [
		i == 0 and record and record.name or "",
		i == 0 and employee.name or "",
		i == 0 and employee.employee_name or "", 
		i == 0 and date or "",
		i == 0 and record and record.status or "",
		i == 0 and get_fiscal_year(date)[0] or "", 
		i == 0 and employee.company or "",
		i == 0 and record and record.naming_series or get_naming_series(),
		record and record["task_details"][i]["task_record_id"] or "",
		record and record["task_details"][i]["task"] or "",
		record and record["task_details"][i]["in_time"] or "",
		record and record["task_details"][i]["out_time"] or "",
		record and record["task_details"][i]["description"] or "",
	]

def get_dates(args):
	"""get list of dates in between from date and to date"""
	no_of_days = date_diff(add_days(args["to_date"], 1), args["from_date"])
	dates = [add_days(args["from_date"], i) for i in range(0, no_of_days)]
	return dates

def get_active_employees():
	employees = frappe.db.sql("""select name, employee_name, company
		from tabEmployee where docstatus < 2 and status = 'Active'""", as_dict=1)
	return employees

def get_existing_attendance_records(args):
	attendance = frappe.db.sql("""SELECT 
									att.name, 
									att.att_date, 
									att.employee, 
									att.status, 
									att.naming_series,
									ats.name AS task_record_id, 
									ats.task, 
									ats.in_time, 
									ats.out_time, 
									ats.description 
								FROM 
									`tabAttendance` att, 
									`tabAttendance Time Sheet` ats 
								WHERE 
									ats.parent = att.name 
									AND 
									att.att_date between %s and %s 
									AND att.docstatus < 2 ORDER BY att.att_date ASC""",(args["from_date"], args["to_date"]), as_dict=1)

	existing_attendance = {}
	att_id = []
	
	for att in attendance:
		task_details = []
		if att.name not in att_id:
			for a in [dictio for dictio in attendance if dictio['name'] == att.name]:
				task_details.append({
					"task_record_id":a.task_record_id,
					"task":a.task,
					"in_time":a.in_time,
					"out_time":a.out_time,
					"description":a.description
					})
			att_id.append(att.name)

			att.update({"task_details":task_details})

			existing_attendance[tuple([str(att.att_date), att.employee])] = att

	return existing_attendance

def get_naming_series():
	series = frappe.get_meta("Attendance").get_field("naming_series").options.strip().split("\n")
	if not series:
		frappe.throw(_("Please setup numbering series for Attendance via Setup > Numbering Series"))
	return series[0]


@frappe.whitelist()
def upload():
	if not frappe.has_permission("Attendance", "create"):
		raise frappe.PermissionError

	from frappe.utils.csvutils import read_csv_content_from_uploaded_file
	from frappe.modules import scrub

	rows = read_csv_content_from_uploaded_file()
	rows = filter(lambda x: x and any(x), rows)
	if not rows:
		msg = [_("Please select a csv file")]
		return {"messages": msg, "error": msg}
	columns = [scrub(f) for f in rows[4]]
	columns[0] = "name"
	columns[3] = "att_date"
	ret = []
	error = False
	child_entries = {}

	from frappe.utils.csvutils import check_record

	for i, row in enumerate(rows[5:]):
		if not row: continue
		row_idx = i + 5
		d = frappe._dict(zip(columns, row))
		
		d["doctype"] = "Attendance"
		if d.name:
			d["docstatus"] = frappe.db.get_value("Attendance", d.name, "docstatus")

		try:
			if row[1] and row[3]:
				check_record(d)

				att_id = import_doc(d, "Attendance", 1, row_idx, submit=True)
				ret.append(att_id)

				task_details = []
				task_details.append(get_child_entries(att_id,row))
				
				child_entries.update({
					att_id:task_details
					})
			else:
				att_id = ret[-1]
				child_entries[att_id].append(get_child_entries(att_id, row))

		except Exception, e:
			error = True
			ret.append('Error for row (#%d) %s : %s' % (row_idx,
				len(row)>1 and row[1] or "", cstr(e)))

	save_child_entries(child_entries)

	if error:
		frappe.db.rollback()
	else:
		# frappe.db.commit()
		pass
	return {"messages": ret, "error": error}

def get_child_entries(att_id, row):
	return {
		"name": row[8],
		"parent": att_id,
		"task": row[9],
		"in_time": dt.datetime.strptime(row[10], '%H:%M:%S'),
		"out_time": dt.datetime.strptime(row[11], '%H:%M:%S'),
		"description":row[12]
	}

def make_child_entry(att_id,record):
	att=frappe.new_doc("Attendance Time Sheet")
	att.task = record["task"]
	att.description = record["description"]
	att.in_time = record["in_time"]
	att.out_time = record["out_time"]
	att.parent = att_id
	att.parentfield='task_details'
	att.parenttype='Attendance'
	att.docstatus=1
	att.save(ignore_permissions=True)
	# worked_hours=cint(worked_hours) + cint(diff.seconds/60)
	# prt = frappe.get_doc('Attendance', att_id)
	# total_hours=((flt(prt.total_hours)*60)+flt(worked_hours))/60
	# frappe.db.sql("""update `tabAttendance` set total_hours='%s' where name='%s'"""%(total_hours,att_id))
	frappe.db.commit()

def save_child_entries(child_entries):
	for key, value in child_entries.iteritems():
		for record in value:
			make_child_entry(key, record)	

def import_doc(d, doctype, overwrite, row_idx, submit=False, ignore_links=False):
	#frappe.errprint("in import doc")
	"""import main (non child) document"""
	if d.get("name") and frappe.db.exists(doctype, d['name']):
		if overwrite:
			doc = frappe.get_doc(doctype, d['name'])
			doc.ignore_links = ignore_links
			doc.update(d)
			if d.get("docstatus") == 1:
				doc.update_after_submit()
			else:
				doc.save()
			# return 'Updated row (#%d) %s' % (row_idx + 1, getlink(doctype, d['name']))
			return d["name"]
		else:
			return 'Ignored row (#%d) %s (exists)' % (row_idx + 1,
				getlink(doctype, d['name']))
	else:
		doc = frappe.get_doc(d)
		doc.ignore_links = ignore_links
		doc.insert()

		if submit:
			doc.submit()

		return doc.get('name')

def getlink(doctype, name):
	return '<a href="#Form/%(doctype)s/%(name)s">%(name)s</a>' % locals()
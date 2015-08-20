from __future__ import unicode_literals
import frappe
from datetime import timedelta

def execute():
	update_attendance_timesheet_records()

def update_attendance_timesheet_records():
	for attr in frappe.db.sql("""select in_time, out_time, task, name from `tabAttendance Time Sheet`
		where docstatus = 1""", as_dict=1):

		# rec = unicode_to_timedelta(attr['in_time'], attr['out_time'])
		rec = timedelta_to_unicode(attr['in_time'], attr['out_time'])

		frappe.db.sql("""update `tabAttendance Time Sheet`
						set out_time = '%s', in_time = '%s' where name = '%s'"""%(rec["out_time"],
						rec["in_time"], attr['name']))

		frappe.db.commit()
	print "Attendance Time sheet `In Time`,`Out Time` updated ...."

def timedelta_to_unicode(in_time, out_time):
	"""removing microseconds from in time and out time"""
	return {
		"in_time":str(in_time).split(".")[0],
		"out_time":str(out_time).split(".")[0]
	}

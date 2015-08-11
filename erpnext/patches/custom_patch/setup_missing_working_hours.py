from __future__ import unicode_literals
import frappe
import datetime as dt

def execute():
	update_attendance_timesheet_records()

def update_attendance_timesheet_records():
	for attr in frappe.db.sql("""select in_time, out_time, task, name from `tabAttendance Time Sheet` 
		where docstatus = 1""", as_dict=1):
		
		rec = unicode_to_timedelta(attr['in_time'], attr['out_time'])
		
		frappe.db.sql("""update `tabAttendance Time Sheet` 
				set working_hours = '%s' 
				where name = '%s' """%((rec["out_time"] - rec["in_time"]), attr['name']))
		
		frappe.db.commit()

def unicode_to_timedelta(in_time, out_time):
	if isinstance(in_time, unicode) and isinstance(out_time, unicode):
		_in = in_time.split(":")
		_out = out_time.split(":")
		
		return {
			"in_time":dt.timedelta(hours = int(_in[0]), minutes = int(_in[1]), seconds = int(_in[2])),
			"out_time":dt.timedelta(hours = int(_out[0]), minutes = int(_out[1]), seconds = int(_out[2]))
		}

	else:
		return {
			"in_time":in_time,
			"out_time":out_time
		}
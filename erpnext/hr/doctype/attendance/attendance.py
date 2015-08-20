# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe

from frappe.utils import getdate, nowdate
from frappe import _
from frappe.model.document import Document
from erpnext.hr.utils import set_employee_name
import datetime as dt

class Attendance(Document):
	def validate_duplicate_record(self):
		res = frappe.db.sql("""select name from `tabAttendance` where employee = %s and att_date = %s
			and name != %s and docstatus = 1""",
			(self.employee, self.att_date, self.name))
		if res:
			frappe.throw(_("Attendance for employee {0} is already marked").format(self.employee))

		set_employee_name(self)

	def check_leave_record(self):
		if self.status == 'Present':
			leave = frappe.db.sql("""select name from `tabLeave Application`
				where employee = %s and %s between from_date and to_date and status = 'Approved'
				and docstatus = 1""", (self.employee, self.att_date))

			if leave:
				frappe.throw(_("Employee {0} was on leave on {1}. Cannot mark attendance.").format(self.employee,
					self.att_date))

	def validate_att_date(self):
		if getdate(self.att_date) > getdate(nowdate()):
			frappe.throw(_("Attendance can not be marked for future dates"))

	def validate_employee(self):
		emp = frappe.db.sql("select name from `tabEmployee` where name = %s and status = 'Active'",
		 	self.employee)
		if not emp:
			frappe.throw(_("Employee {0} is not active or does not exist").format(self.employee))

	def validate(self):
		from erpnext.controllers.status_updater import validate_status
		from erpnext.accounts.utils import validate_fiscal_year
		validate_status(self.status, ["Present", "Absent", "Half Day"])
		validate_fiscal_year(self.att_date, self.fiscal_year, _("Attendance Date"), self)
		self.validate_att_date()
		self.validate_duplicate_record()
		self.check_leave_record()
		self.validate_task_details()

		self.working_hours = self.calculate_total_work_hours()
		self.break_time = self.calculate_total_break_hours()

	def on_update(self):
		# this is done because sometimes user entered wrong employee name
		# while uploading employee attendance
		employee_name = frappe.db.get_value("Employee", self.employee, "employee_name")
		frappe.db.set(self, 'employee_name', employee_name)

	def calculate_total_work_hours(self):
		"""
			calculate the total working time in Hours
		"""
		time_sheet_records = self.task_details

		hours = dt.timedelta(hours = 0, minutes = 0, seconds = 0)

		for record in time_sheet_records:
			rec = self.unicode_to_timedelta(record.in_time, record.out_time)
			record.working_hours = ( rec["out_time"] - rec["in_time"] )
			hours += ( rec["out_time"] - rec["in_time"] )

		return hours

	def calculate_total_break_hours(self):
		"""
			calculate the total break time in Hours
		"""
		time_sheet_records = self.task_details

		break_time = dt.timedelta(hours = 0, minutes = 0, seconds = 0)

		for i in range(0,len(time_sheet_records)):
			if i+1 < len(time_sheet_records):
				rec_1 = self.unicode_to_timedelta(time_sheet_records[i].in_time, time_sheet_records[i].out_time)
				rec_2 = self.unicode_to_timedelta(time_sheet_records[i+1].in_time, time_sheet_records[i+1].out_time)

				break_time += ( rec_2["in_time"] - rec_1["out_time"] )

		return break_time

	def unicode_to_timedelta(self,in_time, out_time):
		# time = frappe._dict({
		# 	"in_time": dt.timedelta(hours = 0, minutes = 0, seconds = 0)
		# 	"out_time": dt.timedelta(hours = 0, minutes = 0, seconds = 0)
		# 	})

		if isinstance(in_time, unicode) and isinstance(out_time, unicode):
			# validate_date_format([in_time,out_time])
			validate_date_format({"In Time":in_time,"Out Time":out_time})
			_in = in_time.split(":")
			_out = out_time.split(":")
			return {
				"in_time":dt.timedelta(hours = int(_in[0]), minutes = int(_in[1]), seconds = int(_in[2]) if len(_in) == 3 else 0),
				"out_time":dt.timedelta(hours = int(_out[0]), minutes = int(_out[1]), seconds = int(_out[2]) if len(_out) == 3 else 0)
			}
		else:
			return {
				"in_time":in_time,
				"out_time":out_time
			}

	def validate_task_details(self):
		"""
			validate the in time and out time
			0. Check Attendance status
			1. In time can not be greater than out time_sheet_records
			2. In time of next record must be greater than out time of previous record
		"""
		if self.status == "Absent":
			self.task_details = {}
		else:
			records = self.task_details

			for i in range(0,len(records)):
				rec_1 = self.unicode_to_timedelta(records[i].in_time, records[i].out_time)

				if rec_1["in_time"] == rec_1["out_time"]:
					frappe.throw("In Time & Out Time can not be same")
				elif rec_1["in_time"] > rec_1["out_time"]:
					frappe.throw("In Time should be less than Out Time for record : {0}".format(records[i].idx))

				if i+1 < len(records):
					rec_2 = self.unicode_to_timedelta(records[i+1].in_time, records[i+1].out_time)

					if rec_2["in_time"] < rec_1["out_time"]:
						frappe.throw("In Time of record {0} should be greater than Out Time of record {1}".format(records[i+1].idx, records[i].idx,))

def validate_date_format(_time=None):
	for field, time in _time.iteritems():
		tm_list = time.split(":")
		hours = 0
		minutes = 0
		seconds = 0

		if (len(tm_list) == 3) or (len(tm_list) == 2):
			hours, minutes = int(tm_list[0]), int(tm_list[1])
			seconds = 0 if len(tm_list) == 2 else int(tm_list[2])
			if not (hours >=0 and hours <=23):
				frappe.throw("Invalid hours value in '%s' field"%(field))
			elif not (minutes >= 0 and minutes <= 59):
				frappe.throw("Invalid minutes value in '%s' field"%(field))
			elif not (seconds >= 0 and seconds <= 59):
				frappe.throw("Invalid seconds value  in '%s' field"%(field))
		else:
			frappe.throw("Invalid time format please input time in HH:MM:SS or HH:MM format")

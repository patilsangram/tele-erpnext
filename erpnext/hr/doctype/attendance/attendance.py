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
		self.check_validate_hours()

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
		in_time = dt.timedelta(hours = 0, minutes = 0, seconds = 0)
		out_time = dt.timedelta(hours = 0, minutes = 0, seconds = 0)

		for record in time_sheet_records:
			if isinstance(record.in_time, unicode) and isinstance(record.out_time, unicode):
				in_time = self.unicode_to_timedelta(record.in_time)
				out_time = self.unicode_to_timedelta(record.out_time)
			else:
				in_time = record.in_time
				out_time = record.out_time

			hours += ( out_time - in_time )

		return hours

	def calculate_total_break_hours(self):
		"""
			calculate the total break time in Hours
		"""
		time_sheet_records = self.task_details
		
		break_time = dt.timedelta(hours = 0, minutes = 0, seconds = 0)
		start_dt = dt.timedelta(hours = 0, minutes = 0, seconds = 0)
		end_dt = dt.timedelta(hours = 0, minutes = 0, seconds = 0)
		
		for i in range(0,len(time_sheet_records)):
			if i+1 < len(time_sheet_records):
				if isinstance(time_sheet_records[i+1].in_time, unicode) and isinstance(time_sheet_records[i].out_time, unicode):
					start_dt = self.unicode_to_timedelta(time_sheet_records[i].out_time)
					end_dt = self.unicode_to_timedelta(time_sheet_records[i+1].in_time)
				else:
					start_dt = time_sheet_records[i].out_time
					end_dt = time_sheet_records[i+1].in_time

				break_time += ( end_dt - start_dt )
				
		return break_time

	def unicode_to_timedelta(self,uni_time):
		time = uni_time.split(":")
		return dt.timedelta(hours = int(time[0]), minutes = int(time[1]), seconds = int(time[2]))

	def check_validate_hours(self):
		# attendance = frappe.get_doc("Attendance", self.name)
		time_sheet_records = self.task_details

		for record in time_sheet_records:
			if record.in_time > record.out_time:
				frappe.throw("In time can not be greater than out time\nPlease check the record numer : {0}".format(record.idx))
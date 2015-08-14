# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from datetime import datetime as dt,timedelta

class TimesheetReport(Document):
	def validate(self):
		self.get_timesheet_report()

	def get_timesheet_report(self):
		# validate from date to date
		# If send notification to manager if marked hours are more than 8 hrs
		# fetch the records and save the data in HTML table as string
		# save record in html_code fields
		# return the html_code string to render the table on html field

		timesheet_report = ""

		if self.is_valid_from_to_dates():
			# get the attendance records between given date range
			query = """SELECT DISTINCT
					    ats.task,
					    att.att_date,
					    att.status,
					    att.working_hours as day_working_hours,
					    SEC_TO_TIME(SUM(TIME_TO_SEC(ats.working_hours))) as task_working_hours,
					    MIN(ats.in_time)  AS in_time,
					    MAX(ats.out_time) AS out_time
					FROM
					    `tabAttendance` AS att,
					    `tabAttendance Time Sheet` ats
					WHERE
					    att.docstatus=1
					AND att.employee='{emp}'
					AND (
					        att.att_date BETWEEN '{from_date}' AND '{to_date}')
					AND ats.parent=att.name
					GROUP BY
					    ats.task,
					    att.att_date
					ORDER BY
					    att.att_date DESC, ats.idx ASC""".format(emp=self.employee, from_date=self.from_date, to_date=self.to_date)

			records = frappe.db.sql(query,as_dict=True)
			records = self.get_formatted_records(records)
			timesheet_html_report = self.get_html_code(records.get("timesheet_record"), records.get("timing_totals"))

	def is_valid_from_to_dates(self):
		if self.from_date and self.to_date:
			from_date = dt.strptime(self.from_date,"%Y-%m-%d")
			to_date = dt.strptime(self.to_date,"%Y-%m-%d")
			date_diff = to_date - from_date

			if (from_date.strftime("%a") == "Fri") and (to_date.strftime("%a") == "Thu") and (date_diff.days == 6):
				return True
			else:
				frappe.throw("Invalid From Date and To Date")
		else:
			frappe.throw("From Date and To Date fields are mandatory")

	def get_formatted_records(self,records):
		day_to_index={'Fri':1,'Sat':2,'Sun':3,'Mon':4,'Tue':5,'Wed':6,'Thu':7}

		days = ['Day','Fri','Sat','Sun','Mon','Tue','Wed','Thu']
		dates = ["Date",'','','','','','','']
		# setting up dates
		from_date = dt.strptime(self.from_date,"%Y-%m-%d")
		for i in range(1,8):
			date = from_date + timedelta(i-1)
			dates[i] = date.strftime("%d-%m-%y")

		status = ['Status','Absent','Absent','Absent','Absent','Absent','Absent','Absent']
		in_time = ['In Time','','','','','','','']
		out_time = ['Out Time','','','','','','','']
		day_totals = ['Total','','','','','','','','','']
		att_timings = {}
		tasks = {}

		ordered_tasks = []

		for att_record in records:
			index = day_to_index.get(att_record.get("att_date").strftime("%a"))
			dates[index] = att_record.get("att_date").strftime("%d-%m-%y")
			status[index] = att_record.get("status")
			day_totals[index + 1] = att_record.get("day_working_hours")

			if in_time[index] or (in_time[index] == timedelta(0)):
				# compare times and choose min time as in_time
				if in_time[index] > att_record.get("in_time"):
					in_time[index] = att_record.get("in_time")
			else:
				in_time[index] = att_record.get("in_time")

			if out_time[index] or (out_time[index] == timedelta(0)):
				# compare times and choose max time as in_time
				if out_time[index] < att_record.get("out_time"):
					out_time[index] = att_record.get("out_time")
			else:
				out_time[index] = att_record.get("out_time")

			task = att_record.get("task")
			task_template = []
			if not tasks.get(task):
				# task_template = [task,'','','','','','','','','']
				task_template = [task,'','','','','','','','','']
				task_template[9] = att_record.get("task_working_hours")
			else:
				task_template = tasks.get(task)
				task_template[9] += att_record.get("task_working_hours")
			task_template[index+1] = att_record.get("task_working_hours")
			tasks.update({
				task:task_template
			})
			if task not in ordered_tasks: ordered_tasks.append(task)

		timesheet_record = [dates,status,in_time,out_time]
		[timesheet_record.append(tasks.get(key)) for key in ordered_tasks]

		day_totals[9] = self.get_timing_totals(day_totals)
		timesheet_record.append(day_totals)

		return {
			"timesheet_record":timesheet_record,
			"timing_totals":day_totals
		}

	def get_timing_totals(self,totals):
		total = timedelta(0,0)
		# check calculate the total timing
		for time in totals:
			
			if isinstance(time,timedelta):
				total += time
		
		return str(total.days*24 + total.seconds//3600) + " : " + str((total.seconds//60)%60)

	def get_html_code(self,records,totals):
		from datetime import timedelta

		html_code = "<table class='table table-bordered' widtd=100%><tr align='center'><td rowspan='6' style='vertical-align:bottom !important'><b>Job Name</b></td>\
		            <td><b>Day</b></td><td><b>Fri</b></td><td><b>Sat</b></td><td><b>Sun</b></td><td><b>Mon</b></td><td><b>Tue</b></td>\
		            <td><b>Wed</b></td><td><b>Thu</b></td><td rowspan='6' style='vertical-align:bottom !important'><b>Total Job Hours</b></td></tr>"

		for rec in records:
			row = "<tr align='center'>"

			index = 0
			for r in rec:
				row += "<td><b>%s</b></td>"%(r) if r in ["Date","Status","In Time","Out Time","Total"] else "<td>%s</td>"%(self.get_formatted_time(r))
				index += 1

			row += "</tr><tr><td colspan='8'></td></tr>" if records.index(rec) == 3 else "</tr>"
			html_code += row

		html_code += "<tr><td colspan='10'><b><br>Employee Signature<br><br>Checked By</b></td></tr>"

		self.html_code = html_code
		return html_code

	def get_formatted_time(self,time):
		return ":".join(str(time).split(":")[:2])

@frappe.whitelist()
def get_from_to_dates():
	now = dt.now()
	from_date, to_date = now.date(), now.date()

	if now.strftime("%a") == "Fri":
		from_date = now.date()
		to_date = now.date() + timedelta(days = 6)
	elif now.strftime("%a") in ["Sun","Mon","Tue","Wed","Thu"]:
		weeks = 0 if now.strftime("%a") == "Sun" else -1
		last_friday = (now.date() - timedelta(days=now.weekday()) + timedelta(days=4, weeks=weeks))
		from_date = last_friday
		to_date = last_friday + timedelta(days = 6)

	return {
		"from_date":from_date,
		"to_date":to_date
	}

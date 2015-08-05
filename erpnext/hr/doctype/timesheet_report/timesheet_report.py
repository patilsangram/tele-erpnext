# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

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
					AND att.employee='EMP/0001'
					AND (
					        att.att_date BETWEEN '2015-08-05' AND '2015-08-05')
					AND ats.parent=att.name
					GROUP BY
					    ats.task,
					    att.att_date
					ORDER BY
					    att.att_date DESC"""

			records = frappe.db.sql(query,as_dict=True)
			records = self.get_formatted_records(records)
			timesheet_html_report = self.get_html_code(records)

		# return timesheet_html_report

	def is_valid_from_to_dates(self):
		if self.from_date and self.to_date:
			from datetime import datetime as dt

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
		status = ['Status','','','','','','','']
		in_time = ['In Time','','','','','','','']
		out_time = ['Out Time','','','','','','','']
		tasks = {}

		for att_record in records:
			index = day_to_index.get(att_record.get("att_date").strftime("%a"))
			dates[index] = att_record.get("att_date").strftime("%d-%m-%Y")
			status[index] = att_record.get("status")

			if in_time[index]:
				# compare times and choose min time as in_time
				if in_time[index] > att_record.get("in_time"):
					in_time[index] = att_record.get("in_time")
			else:
				in_time[index] = att_record.get("in_time")

			if out_time[index]:
				# compare times and choose max time as in_time
				if out_time[index] > att_record.get("out_time"):
					in_time[index] = att_record.get("out_time")
			else:
				out_time[index] = att_record.get("out_time")

			task = att_record.get("task")
			task_template = []
			if not tasks.get(task):
				task_template = [task,'','','','','','','','','']
				task_template[9] = att_record.get("task_working_hours")
			else:
				task_template = tasks.get(task)
				task_template[9] += att_record.get("task_working_hours")
			task_template[index+1] = att_record.get("task_working_hours")
			tasks.update({
				task:task_template
			})

		self.store_timings_for_total(tasks)

		timesheet_record = [dates,in_time,out_time]
		[timesheet_record.append(value) for key,value in tasks.iteritems()]

		return timesheet_record

	def store_timings_for_total(self,tasks):
		from datetime import timedelta

		timing_totals = {}
		index_to_day={1:'Fri',2:'Sat',3:'Sun',4:'Mon',5:'Tue',6:'Wed',7:'Thu'}

		for key,task in tasks.iteritems():
			frappe.errprint(len(task))
			for rec in task:
				i = task.index(rec)
				task_total_time = timedelta(0)
				if isinstance(rec,timedelta) and i != 9:
					day = index_to_day.get(i)
					# calculating total time spent on task
					task_total_time += rec
					# calculating total time spent on day
					day_total_time = ""
					if not timing_totals.get(day):
						day_total_time = task[i]
					else:
						day_total_time = timing_totals.get(day) + task[i]

					timing_totals.update({
						day:day_total_time,
						key:task_total_time
					})

		frappe.errprint(timing_totals)
		s

	def get_html_code(self,records):
		html_code = "<table class='table table-bordered' width=100%><tr><th rowspan='5' style='vertical-align: bottom;'>Job Name</th>\
					<th><b>Day</b></th><th><b>Fri</b></th><th><b>Sat</b></th><th><b>Sun</b></th><th><b>Mon</b></th><th><b>Tue</b></th>\
					<th><b>Wed</b></th><th><b>Thu</b></th><th rowspan='5' style='vertical-align: bottom;'>Total Job Hours</th></tr>"

		for rec in records:
			row = "<tr>"
			for r in rec:
				row += "<td><b>%s</b></td>"%(r) if r in ["Date","Status","In Time","Out Time"] else "<td>%s</td>"%(r)

			row += "</tr><tr><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>" if records.index(rec) == 2 else "</tr>"


			html_code += row

		self.html_code = html_code
		return html_code

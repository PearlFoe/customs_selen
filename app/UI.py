from tkinter import *
from tkinter.ttk import Frame

import os

class Vier():
	"""docstring for Vier"""
	def __init__(self):
		self.window = Tk()
		self.window.geometry('550x400')

	def run(self):
		header = Frame(self.window)
		Header(
			header, 
			'Current orders'
		).create()
		header.pack(side=TOP, anchor=NW)
		
		l_input_frame = LabelFrame(self.window)
		input_frame = Frame(l_input_frame)
		InputForm(input_frame).create()

		input_frame.pack(side=BOTTOM)
		l_input_frame.pack(side=BOTTOM)

		l_order_list_frame = LabelFrame(self.window)
		order_list_frame = Frame(l_order_list_frame)
		OrderList(order_list_frame).create()

		scrollbar = Scrollbar(order_list_frame, orient=VERTICAL)

		canvas = Canvas(order_list_frame, width=300, height=100,
                                yscrollcommand=scrollbar.set)
		scrollbar.config(canvas=canvas.yview)

		order_list_frame.pack(side=LEFT)
		scrollbar.pack(side=RIGHT, fill=Y)
		l_order_list_frame.pack(side=TOP)

		'''
		order_frame = Frame(self.window)
		Order(
			order_frame, 
			'Login',
			'01-01-2001',
			'00-01',
			'Started'
		).create()
		
		order_frame.pack(side=TOP)
		'''
		self.window.mainloop()

class Header():
	"""docstring for Header"""
	def __init__(self, window, text):
		self.window = window
		self.text = text

	def create(self):
		lbl = Label(self.window, text=self.text, font=("Arial Bold", 18))
		lbl.pack(side=LEFT) 
		
class OrderList():
	"""docstring for OrderList"""
	def __init__(self, window):
		self.window = window
		self.orders = []
		
	def create(self):
		'''
		for i in orders:
			order_frame = Frame(self.window)
			Order(order_frame).create()
			order_frame.pack(side=TOP)
		'''
		for _ in range(10):
			order_frame = Frame(self.window)
			Order(
				order_frame, 
				'Login',
				'01-01-2001',
				'00-01',
				'Started'
			).create()
			order_frame.pack(side=TOP)

	def add_order(self, order):
		pass

	def remove_order(self, order):
		pass

class Order():
	def __init__(self, window, login, date, time, status):
		self.window = window
		self.login = login
		self.date = date
		self.time = time
		self.status = status
		self.location = {
				'login': 0,
				'datetime': 1,
				'status': 2,
		}

	def create(self):
		self.add_login()
		self.add_datetime()
		self.add_status()

	def add_login(self):
		label = Label(self.window, text=self.login, font=("Arial Bold", 12))
		label.grid(column=self.location['login'], row=0, rowspan=1)

	def add_datetime(self):
		text = f'Date: {self.date}\nTime: {self.time}'
		label = Label(self.window, text=text, font=("Arial Bold", 12))
		label.grid(column=self.location['datetime'], row=0, rowspan=2, sticky=W)

	def add_status(self):
		label = Label(self.window, text=self.status, font=("Arial Bold", 12))
		label.grid(column=self.location['status'], row=0, rowspan=1)

class InputForm():
	"""docstring for InputForm"""
	def __init__(self, window):
		self.window = window
		self._date_input = None
		self._time_input = None
		self._confirm_btn = None

	def create(self):
		self.add_date_input()
		self.add_time_input()
		self.add_confirm_btn()
		
	def add_date_input(self):
		date = StringVar()
		date.set(None)
		_date_input = Entry(self.window, text=date, justify=LEFT)
		label = Label(self.window, text='Date', font=("Arial Bold", 12))

		label.grid(row=0, column=0, sticky=W)
		_date_input.grid(row=0, column=1, sticky=W)

	def add_time_input(self):
		time = StringVar()
		time.set(None)
		_time_input = Entry(self.window, text=time, justify=LEFT)
		label = Label(self.window, text='Time', font=("Arial Bold", 12))

		label.grid(row=1, column=0, sticky=W)
		_time_input.grid(row=1, column=1, sticky=W) 

	def add_confirm_btn(self):
		_confirm_btn = Button(self.window, text='Add')
		_confirm_btn.grid(row=0, column=2, sticky=E)
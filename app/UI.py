from tkinter import *
from tkinter.ttk import Frame, Combobox

from app import logger, config, accounts
from app.utils import get_order_data

import os
import threading

class Vier():
	"""docstring for Vier"""
	def __init__(self, runner):
		self.window = Tk()
		self.window.geometry('750x500')
		self.runner = runner

	def run(self):
		header = Frame(self.window)
		Header(
			header, 
			'Current orders'
		).create()
		header.pack(side=TOP, anchor=NW)

		##################################################
		l_order_list_frame = LabelFrame(self.window)
		container = Frame(l_order_list_frame)

		order_list_frame = ScrollableFrame(container)
		order_list = OrderList(order_list_frame.scrollable_frame)
		
		l_order_list_frame.pack(side=TOP, expand=True, fill='x')
		container.pack(side=TOP, expand=True, fill='x')
		order_list_frame.pack(side=LEFT, expand=True, fill='x')
		
		###################################################
		l_input_frame = LabelFrame(self.window)
		input_frame = Frame(l_input_frame)
		input_form = InputForm(window=input_frame, order_list=order_list, runner=self.runner)
		input_form.create()

		input_frame.pack(side=BOTTOM)
		l_input_frame.pack(side=BOTTOM)

		###################################################	

		btns_frame = Frame(self.window)
		input_form.add_check_box(window=btns_frame, row=0, column=0)
		input_form.add_delete_btn(window=btns_frame, row=0, column=1)
		input_form.add_start_btn(window=btns_frame, row=0, column=2)

		btns_frame.pack(side=TOP)

		threading.Thread(target=self.window.mainloop(), name='Thread_Vier_Main_Loop', daemon=True)

	def quit(self):
		self.window.quit() 

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
		
	def add_order(self, order):
		order_frame = Frame(self.window)
		order.window = order_frame
		order.create()
		order_frame.pack(side=TOP)
		self.orders.append(order)

	def remove_order(self):
		try:
			order = self.orders.pop()
			order.window.destroy()
		except Exception:
			pass

class Order():
	def __init__(self, login, status, start_date, end_date, start_time, end_time, auto_type, customs_type, 
					reg_number, car_brand, car_model, region, window=None):
		self.window = window
		self.login = StringVar(value=login)
		self.start_date = start_date
		self.end_date = end_date		
		self.start_time = start_time
		self.end_time = end_time
		self.ordered_datetime = StringVar()
		self.time_to_wait = StringVar(value=f"Time left:\n{config['TIME_OUT']}")
		self.status = StringVar(value=status)
		self.auto_type = auto_type
		self.customs_type = customs_type
		self.reg_number = reg_number
		self.car_brand = car_brand
		self.car_model = car_model
		self.region = region

		self.__location = {
				'login': 0,
				'datetime': 1,
				'time_to_wait': 2,
				'status': 3,
		}

	def create(self):
		self.add_login()
		self.add_datetime()
		self.add_time_to_wait()
		self.add_status()

	def add_login(self):
		label = Label(self.window, textvariable=self.login, font=("Arial Bold", 12))
		label.grid(column=self.__location['login'], row=0, rowspan=1)

	def add_datetime(self):
		text = f'Date: {self.start_date} - {self.end_date}\nTime: {self.start_time} - {self.end_time}'
		self.ordered_datetime.set(text)
		label = Label(self.window, textvariable=self.ordered_datetime, font=("Arial Bold", 12))
		label.grid(column=self.__location['datetime'], row=0, rowspan=2, sticky=W)

	def add_time_to_wait(self):
		label = Label(self.window, textvariable=self.time_to_wait, font=("Arial Bold", 12))
		label.grid(column=self.__location['time_to_wait'], row=0, rowspan=1)

	def add_status(self):
		label = Label(self.window, textvariable=self.status, font=("Arial Bold", 12))
		label.grid(column=self.__location['status'], row=0, rowspan=1)

	def update_login(self, new_login):
		self.login.set(new_login)

	def update_status(self, new_status):
		self.status.set(new_status)

	def update_time_to_wait(self, time_left):
		s = f"Time left:\n{time_left}"
		self.time_to_wait.set(s)

	def update_datetime(self, date, time):
		text = f'Date: {date}\nTime: {time}'
		self.ordered_datetime.set(text)

class InputForm():
	"""docstring for InputForm"""
	def __init__(self, order_list, runner, window=None):
		self.window = window
		self.runner = runner
		self.order_list = order_list
		self._start_date_input = None
		self._end_date_input = None
		self._start_time_input = None
		self._end_time_input = None
		self._auto_type_list = None
		self._customs_type_list = None
		self._reg_number_input = None
		self._car_brand_input = None
		self._car_model_input = None
		self._region_input = None
		self._get_info_from_file = None
		self._start_btn = None
		self._confirm_btn = None
		self._delete_btn = None

	def create(self):
		self.add_date_input()
		self.add_time_input()
		self.add_transport_type_list()
		self.add_customs_type_list()
		self.add_reg_number_input()
		self.add_car_brand_input()
		self.add_car_model_input()
		self.add_region_input()
		self.add_confirm_btn(row=4, column=3)

	def add_date_input(self):
		start_date = StringVar()
		start_date.set('01.01.2021')
		end_date = StringVar()
		end_date.set('02.01.2021')
		'''
		self._date_input = Entry(self.window, text=date, justify=LEFT)
		label = Label(self.window, text='Date', font=("Arial Bold", 12))

		label.grid(row=0, column=0, sticky=W)
		self._date_input.grid(row=0, column=1, sticky=W)
		'''

		label = Label(self.window, text='Date', font=("Arial Bold", 12))
		date_input_frame = Frame(self.window)

		self._start_date_input = Entry(date_input_frame, text=start_date, justify=LEFT)
		self._end_date_input = Entry(date_input_frame, text=end_date, justify=LEFT)

		self._start_date_input.grid(row=0, column=0)
		self._end_date_input.grid(row=0, column=1)

		label.grid(row=0, column=0, sticky=W)
		date_input_frame.grid(row=0, column=1, sticky=W)

	def add_time_input(self):
		start_time = StringVar()
		start_time.set('00-01')
		end_time = StringVar()
		end_time.set('01-02')
		'''
		self._time_input = Entry(self.window, text=time, justify=LEFT)
		label = Label(self.window, text='Time', font=("Arial Bold", 12))

		label.grid(row=0, column=2, sticky=W)
		self._time_input.grid(row=0, column=3, sticky=W)
		'''
		label = Label(self.window, text='Time', font=("Arial Bold", 12))
		time_input_frame = Frame(self.window)

		self._start_time_input = Entry(time_input_frame, text=start_time, justify=LEFT)
		self._end_time_input = Entry(time_input_frame, text=end_time, justify=LEFT)

		self._start_time_input.grid(row=0, column=0)
		self._end_time_input.grid(row=0, column=1)

		label.grid(row=0, column=2, sticky=W)
		time_input_frame.grid(row=0, column=3, sticky=W)


	def add_transport_type_list(self):
		items = [
			'Легковой автомобиль',
			'Грузовой автомобиль',
			'Автобус',
			'Легковой/пассажирский микроавтобус',
			'Мотоцикл'
		]

		label = Label(self.window, text="Transport type", font=("Arial Bold", 12))
		self._auto_type_list = Combobox(self.window, values=items)
		label.grid(row=1, column=0, sticky=W)
		self._auto_type_list.grid(row=1, column=1, sticky=NSEW)
		self._auto_type_list.current(0)

	def add_customs_type_list(self):
		items = [
			'Брест',
			'Урбаны',
			'Брузги',
			'Котловка',
			'Григоровщина'
		]

		label = Label(self.window, text="Customs type", font=("Arial Bold", 12))
		self._customs_type_list = Combobox(self.window, values=items)
		label.grid(row=1, column=2, sticky=W)
		self._customs_type_list.grid(row=1, column=3, sticky=NSEW)
		self._customs_type_list.current(0)

	def add_reg_number_input(self):
		label = Label(self.window, text="Reg. number", font=("Arial Bold", 12))
		self._reg_number_input = Entry(self.window, text=None, justify=LEFT)

		label.grid(row=2, column=0, sticky=W)
		self._reg_number_input.grid(row=2, column=1, sticky=NSEW)

	def add_car_brand_input(self):
		label = Label(self.window, text="Transport brand", font=("Arial Bold", 12))
		self._car_brand_input = Entry(self.window, text=None, justify=LEFT)

		label.grid(row=2, column=2, sticky=W)
		self._car_brand_input.grid(row=2, column=3, sticky=NSEW)

	def add_car_model_input(self):
		label = Label(self.window, text="Transport model", font=("Arial Bold", 12))
		self._car_model_input = Entry(self.window, text=None, justify=LEFT)

		label.grid(row=3, column=0, sticky=W)
		self._car_model_input.grid(row=3, column=1, sticky=NSEW)

	def add_region_input(self):
		label = Label(self.window, text="Region", font=("Arial Bold", 12))
		self._region_input = Entry(self.window, text='RU', justify=LEFT)

		label.grid(row=3, column=2, sticky=W)
		self._region_input.grid(row=3, column=3, sticky=NSEW)

	def add_check_box(self, row, column, window=None):
		window = self.window if not window else window
		self._get_info_from_file = BooleanVar()
		self._get_info_from_file.set(True)

		chk = Checkbutton(window, text="Get info from file", var=self._get_info_from_file)  
		chk.grid(row=row, column=column)

	def add_start_btn(self, row, column, window=None):
		window = self.window if not window else window
		self._start_btn = Button(window, text="Start", command=self.start_on_slick)
		self._start_btn.grid(row=row, column=column, sticky=W)

	def add_confirm_btn(self, row, column, window=None):
		window = self.window if not window else window
		self._confirm_btn = Button(window, text='Add', command=self.confirm_on_click)
		self._confirm_btn.grid(row=row, column=column, sticky=NSEW)

	def add_delete_btn(self, row, column, window=None):
		window = self.window if not window else window
		self._delete_btn = Button(window, text="Delete", command=self.delete_on_click)
		self._delete_btn.grid(row=row, column=column, sticky=W)

	def get_data_from_input(self):
		return {
			'start_date': self._start_date_input.get(),
			'end_date': self._end_date_input.get(),
			'start_time': self._start_time_input.get(),
			'end_time': self._end_time_input.get(),
			'auto_type': self._auto_type_list.get(),
			'customs_type': self._customs_type_list.get(),
			'reg_number': self._reg_number_input.get(),
			'car_brand': self._car_brand_input.get(),
			'car_model': self._car_model_input.get(),
			'region': self._region_input.get()
		}

	def start_on_slick(self):
		self.runner.orders = self.order_list.orders
		self.runner.start()

	def confirm_on_click(self):
		if self._get_info_from_file:
			input_data = self.get_data_from_input()
			file_data = get_order_data('order_data.json')
			order = Order(
				login='---', 
				status='Waiting',
				start_date=input_data['start_date'],
				end_date=input_data['end_date'],
				start_time=input_data['start_time'],
				end_time=input_data['end_time'],
				auto_type=input_data['auto_type'],
				customs_type=input_data['customs_type'],
				**file_data
			)
		else:	
			data = self.get_data_from_input()
			order = Order(
				login='---', 
				status='Waiting',
				**data
			)
		self.order_list.add_order(order)

	def delete_on_click(self):
		self.order_list.remove_order()

class ScrollableFrame(Frame):
	def __init__(self, container, *args, **kwargs):
		super().__init__(container, *args, **kwargs)
		canvas = Canvas(self)
		scrollbar = Scrollbar(self, orient="vertical", command=canvas.yview)
		self.scrollable_frame = Frame(canvas)

		self.scrollable_frame.bind(
			"<Configure>",
			lambda e: canvas.configure(
				scrollregion=canvas.bbox("all")
			)
		)

		canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

		canvas.configure(yscrollcommand=scrollbar.set)

		canvas.pack(side="left", fill="both", expand=True)
		scrollbar.pack(side="right", fill="y")
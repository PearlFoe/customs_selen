from tkinter import *
from tkinter.ttk import Frame, Combobox

from app import logger, config, accounts

import os

class Vier():
	"""docstring for Vier"""
	def __init__(self, runner):
		self.window = Tk()
		self.window.geometry('550x500')
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
		
		l_order_list_frame.pack(side=TOP)
		container.pack(side=TOP)
		order_list_frame.pack(side=LEFT)
		
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

		self.window.mainloop()

	def quit(self):
		self.window.destroy() 

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
	def __init__(self, login, status, date, time, auto_type, customs_type, 
					reg_number, car_brand, car_model, region, window=None):
		self.window = window
		self.login = StringVar(value=login)
		self.date = date
		self.time = time
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
				'status': 2,
		}

	def create(self):
		self.add_login()
		self.add_datetime()
		self.add_status()

	def add_login(self):
		label = Label(self.window, textvariable=self.login, font=("Arial Bold", 12))
		label.grid(column=self.__location['login'], row=0, rowspan=1)

	def add_datetime(self):
		text = f'Date: {self.date}\nTime: {self.time}'
		label = Label(self.window, text=text, font=("Arial Bold", 12))
		label.grid(column=self.__location['datetime'], row=0, rowspan=2, sticky=W)

	def add_status(self):
		label = Label(self.window, textvariable=self.status, font=("Arial Bold", 12))
		label.grid(column=self.__location['status'], row=0, rowspan=1)

	def update_login(self, new_login):
		self.login.set(new_login)

	def update_status(self, new_status):
		self.status.set(new_status)

class InputForm():
	"""docstring for InputForm"""
	def __init__(self, order_list, runner, window=None):
		self.window = window
		self.runner = runner
		self.order_list = order_list
		self._date_input = None
		self._time_input = None
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
		date = StringVar()
		date.set('01.01.2021')
		self._date_input = Entry(self.window, text=date, justify=LEFT)
		label = Label(self.window, text='Date', font=("Arial Bold", 12))

		label.grid(row=0, column=0, sticky=W)
		self._date_input.grid(row=0, column=1, sticky=W)

	def add_time_input(self):
		time = StringVar()
		time.set('00-01')
		self._time_input = Entry(self.window, text=time, justify=LEFT)
		label = Label(self.window, text='Time', font=("Arial Bold", 12))

		label.grid(row=0, column=2, sticky=W)
		self._time_input.grid(row=0, column=3, sticky=W)

	def add_transport_type_list(self):
		items = [
			'Легковой автомобиль',
			'Грузовой автомобиль',
			'Автобус',
			'Легковой/пассажирский микроавтобус',
			'Мотоцикл'
		]

		label = Label(self.window, text="Auto type", font=("Arial Bold", 12))
		self._auto_type_list = Combobox(self.window, values=items)
		label.grid(row=1, column=0, sticky=W)
		self._auto_type_list.grid(row=1, column=1, sticky=W)
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
		self._customs_type_list.grid(row=1, column=3, sticky=W)
		self._customs_type_list.current(0)

	def add_reg_number_input(self):
		label = Label(self.window, text="Reg. number", font=("Arial Bold", 12))
		self._reg_number_input = Entry(self.window, text=None, justify=LEFT)

		label.grid(row=2, column=0, sticky=W)
		self._reg_number_input.grid(row=2, column=1, sticky=W)

	def add_car_brand_input(self):
		label = Label(self.window, text="Car brand", font=("Arial Bold", 12))
		self._car_brand_input = Entry(self.window, text=None, justify=LEFT)

		label.grid(row=2, column=2, sticky=W)
		self._car_brand_input.grid(row=2, column=3, sticky=W)

	def add_car_model_input(self):
		label = Label(self.window, text="Car model", font=("Arial Bold", 12))
		self._car_model_input = Entry(self.window, text=None, justify=LEFT)

		label.grid(row=3, column=0, sticky=W)
		self._car_model_input.grid(row=3, column=1, sticky=W)

	def add_region_input(self):
		label = Label(self.window, text="Region", font=("Arial Bold", 12))
		self._region_input = Entry(self.window, text='RU', justify=LEFT)

		label.grid(row=3, column=2, sticky=W)
		self._region_input.grid(row=3, column=3, sticky=W)

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
			'date': self._date_input.get(), 
			'time': self._time_input.get(),
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
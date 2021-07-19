from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.slider import Slider
from kivy.uix.button import Button

import os
os.environ['KIVY_GL_BACKEND']='angle_sdl2'

class Vier(App):
	"""docstring for Vier"""
	def build(self):
		layout = BoxLayout(padding=10, orientation='vertical')

		header = Header('Current orders').create()
		order_list = OrdersList().create()

		layout.add_widget(header)
		layout.add_widget(order_list)
		layout.add_widget(Label())

		#layout.add_widget(start_btn)

		return layout

class Header():
	"""docstring for Header"""
	def __init__(self, lable_text):
		self.text = lable_text

	def create(self):
		layout = AnchorLayout(anchor_x='left', anchor_y='top')

		label = Label(
					text=self.text,
					size_hint=(.17, .3),
				)
 		
		layout.add_widget(label)

		return layout
		
class OrdersList():
	def create(self):
		layout = BoxLayout(padding=25, spacing=10)

		for i in range(5):
			order = Order(f'Login {i}', '23-12-2021', '00-01', 'Status').create()
			layout.add_widget(order)
		'''
		slider = Slider()
		layout.add_widget(slider)
		'''
		return layout

class Order():
	"""docstring for Order"""
	def __init__(self, login, date, time, status):
		self.login = login
		self.date = date
		self.time = time
		self.status = status
		self.height = 0.2
		self.width = 0.8

	def create_login_lable(self):
		lable = Label(
					text=self.login,
					size_hint=(self.width, self.height),
				)

		return lable

	def create_datetime_lable(self):
		text = f'Date: {self.date}\nTime: {self.time}'
		lable = Label(
					text=text,
					size_hint=(self.width, self.height),
				)

		return lable

	def create_status_lable(self):
		lable = Label(
					text=self.status,
					size_hint=(self.width, self.height),
				)

		return lable

	def create_order_delete_btn(self):
		button = Button(
					text='Delete',
					size_hint=(.2, self.height),
					background_color='red'
				)

		return button

	def create(self):
		layout = BoxLayout(padding=5, spacing=0)
		
		login_ = self.create_login_lable()
		datetime_ = self.create_datetime_lable()
		status_ = self.create_status_lable()
		delete_btn_ = self.create_order_delete_btn()

		layout.add_widget(login_)
		layout.add_widget(datetime_)
		layout.add_widget(status_)
		#layout.add_widget(delete_btn_)

		return layout
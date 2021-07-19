from kivy.app import App
from kivy.uix.label import Label

import os
os.environ['KIVY_GL_BACKEND']='angle_sdl2'

class Vier(App):
	"""docstring for Vier"""
	def build(self):
		label = Label(
					text='Hello from Kivy',
					size_hint=(.5, .5),
					pos_hint={'center_x': .5, 'center_y': .5})
 
		return label
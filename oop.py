import datetime
import math
import random
import sys


class Animal:
	def __init__(self, age=0, mass=0, birthday_date=datetime.datetime.now(), kind=None):
		self.age = age
		self.mass = mass
		self.birthday_date = birthday_date
		self.kind = kind
		self.cords = (0, 0)

	def go(self, velocity, time, direction):
		distanse = velocity * time
		x = self.cords[0] + (math.cos(direction) * distanse)
		y = self.cords[1] + (math.sin(direction) * distanse)
		self.cords = (x, y)

	def get_cords(self):
		return self.cords

	def tame(self, human):
		return bool(random.randint(0, 1))


class Bird(Animal):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.wing_size = kwargs.get("wing_size", None)
		self.is_can_flying = kwargs.get("is_can_flying", True)

	def fly(self, to):
		if self.is_can_flying:
			self.cords = tuple(to)
			return True
		return False

	def eat(self, food):
		print(f"Eating {food.lower()}...")


class Cock(Bird):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.tail_color = kwargs.get("tail_color", list())
		self.is_wild = kwargs.get("is_wild", False)

	def friendly(self, object):
		return bool(random.randint(0, 1))

	def speak(self):
		print("I'm a smart cock!")

	def die(self):
		print("Cock is died :(")
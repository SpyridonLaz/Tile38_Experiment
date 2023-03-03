import argparse
import datetime as dt
import json
import pathlib
import subprocess
import time
from typing import Union

import redis


def Argparser():
	try:

		parser = argparse.ArgumentParser(
				prog="Enviroment",
				description="Experimental project of given assignment excercise.", add_help=False)

		parser.add_argument(
				'-u', '--url',
				default="localhost",
				help='server uri: string')

		parser.add_argument(
				'-p', '--port',
				default=9851,
				help="server port : integer")

		parser.add_argument(
				'-d', '--defaults', action="store_false",
				default=False,
				help='Enable default settings and geojsons.')

		parser.print_help()
		args, _ = parser.parse_known_args()
		args = args.__dict__
		return args
	except Exception as e:
		print(e)
		exit()


## few rather generic  constants
ARGS = Argparser()
PATH = pathlib.Path().absolute()
DEFAULT_GEOFENCE = [f"{PATH}/athens_dactylios.geojson"]
DEFAULT_POINTS = [f"{PATH}/point_movement.geojson"]


class Generic_Mixin:
	"""Convenient class Mixin to
	properly set Unix timestamps

	class that manages prompts and Operating System dialogs
	"""

	def timestamp(self, interval: int or float = 0, ):
		"""
		:param interval: distance from timestamp in seconds
		:type interval:   integer or float
		:return: Unix timestamp
		:rtype: integer
		"""
		##   Unix timestamp in seconds
		stamp = datetime.now().timestamp()
		return int(stamp) + interval

	def _zenity_dialog(self, prompt_title="title", zenity_args=""):

		try:
			cmd_output = subprocess.Popen(
					["zenity", "--title",
					 prompt_title,
					 "--file-selection",
					 zenity_args,
					 ],
					stdout=subprocess.PIPE,
					stderr=subprocess.PIPE, )
			cmd_output, err = cmd_output.communicate()
			assert cmd_output, "You must to choose a file"
			return cmd_output.decode("utf-8")
		except (AssertionError, FileNotFoundError):
			# fallback to manual labor
			return self.fallback_prompt()
		except Exception:
			exit()

	def fallback_prompt(self):
		# fallback in case OS does not have kdialog/ zenity
		while True:
			try:
				cmd_output = pathlib.Path(input("Enter filepath manually"))
				if pathlib.Path(cmd_output).exists():
					break
				elif cmd_output not in ("X", "x"):
					print("retry or [X] for exit")
					break
				else:
					continue

			except KeyboardInterrupt:
				exit("You must provide a (valid) filepath to continue")
		return cmd_output.as_posix()

	def open_file(self, ):

		# figuring if there are enviromental variables
		# to use for easier file opening
		return self._zenity_dialog(prompt_title="Open File", ) if True else self.fallback_prompt()

	###//TODO

	def save_file(self, ):
		# not currently used###//TODO
		return self._zenity_dialog(
				prompt_title="Save_as..",
				zenity_args="--save")


class linux_promptDialog():
	# not used
	pass


class win32_promptDialog():
	# not used

	pass


class Enviroment(Generic_Mixin):
	"""
	main class that contains all essential components of a test.

	"""

	timestamp = Generic_Mixin.timestamp

	BASE_SCTRUCTURE = {
		'type': 'FeatureCollection',
		'features': []
	}

	def __init__(
			self,
			name: str = "unnamed_experiment",
			host=ARGS.get('url', "localhost"),
			port=ARGS.get('port', 9851),
	):

		# name of test case
		self.name = name
		#       we connect to db
		self.client = redis.Redis(host=host, port=port)

	def _file_list(self, list_of_paths: list):
		##  iterates filepaths ,asserts , reads files , eval  on them
		# and returns a list with the file json objects as dictionaries

		_object_list = []
		for path in list_of_paths:
			assert pathlib.Path(path)
			print("Loading..    ", pathlib.Path(path).name)
			with open(path, 'r') as f:
				data = eval(f.read())
				_object_list += [data]
		return _object_list

	def _filepath_list(self, paths: list = None):

		# user chooses file from dialog

		if not paths:
			#  raw dialog input
			path_decoded = self.open_file()

			# cleaning and separation of paths
			paths = list(filter(None, path_decoded.split("\n")))

		#  iterate through FeatureCollection for objects ,separate them and save as JSON

		obj_list = self._file_list(paths)
		return obj_list

	def _get_features(self, paths: list = None):
		_list = [
			feature for FeatureCollection in self._filepath_list(paths)
			for feature in FeatureCollection.get("features")

		]

		return _list if _list else exit("Error")

	def _build_collection(self, paths: list):
		new_FeatureCollection = self.BASE_SCTRUCTURE
		new_FeatureCollection['features'] = self._get_features(paths)

		return new_FeatureCollection

	def build_webhook(self, name: str, paths: list = None):
		return Webhook(self, self._build_collection(paths), name)

	def build_fleet(self, name: str, paths: list):

		##      Extracting coordinates. why not use FeatureCollection? because we need to add z  (timestamp)

		fleet_point_coords = [feature.get('geometry').get("coordinates") for feature in
		                      self._get_features(paths)]

		return Fleet_vessel(self, name, fleet=fleet_point_coords)


class Fleet_vessel(Generic_Mixin):

	def __init__(self, context: Enviroment, name: str, fleet: list):

		self.input_points = fleet
		self.context = context
		self.client: redis.client.Redis = context.client
		self.name = name
		print("OK")
		print(f"Scooter with name :{self.name} , deployed around Athens")
		self._steps = self._generate()

	def _generate(self, interval: int or float = 0):

		for lon, lat in self.input_points:
			print(f"Moning object {self.context.name} {self.name} to : {lat} , {lon}")
			result = self.client.execute_command(
					"SET",
					self.context.name,
					self.name,
					"POINT",
					lat,
					lon,
					self.timestamp(interval)
			)

			print(f"Ok") if result else print(f"{self.name} did not move")
			yield result

	def create_steps(self, interval: int = 0):
		# builds generator object
		self._steps = self._generate(interval)
		return True if self._steps else False

	def run_step(self, ):
		#       makes a single "step" movement
		# by using the generated object self._steps
		# to loaded geographic points
		if not self._steps:
			print("Create a sequence first! e.g object.step_sequence()")
			raise StopIteration
		next(self._steps)

	def run_sequence(self):
		# iterates all steps at once
		while True:
			try:
				if not self._steps:
					break
				self.run_step()
			# we catchStopIteration
			except StopIteration:
				self._steps = None
				break

		return

	def drop_fleet(self):
		# drop current item from server
		return self.context.client.execute_command("DROP", "{obj}".format(obj=self.name))


class Webhook(Generic_Mixin):
	ZONES = {"cross", "enter", "exit", "inside", "outside"}

	def __init__(
			self,
			context: Enviroment,
			data: dict,
			name: str = "unnamed",
			endpoint: str = "http://localhost:8001/endpoint", ):
		"""
		:param client: Redis client imported from Enviroment
		class
		:param endpoint: url that receives webhook events
		:type endpoint: str

		"""

		self.context = context
		self.data = data
		self.trigger: set = {"cross", "enter", "exit", "inside"}

		self.name: str = name
		self.endpoint: str = endpoint
		print("OK")

	def deploy_webhook(
			self,
			timeLow: Union[str, int] = 0,
			timeHi: Union[int, str] = 60,
	):
		"""
		:param timeLow:    distance from minimum accepted event, in seconds
		:type timeLow: integer  positive/negative
		:param timeHi:  distance from maximum accepted event, in seconds
		:type timeHi: integer  positive/negative
		:return:
		:rtype:
		"""

		timeLow = "{Low}".format(Low=timeLow if isinstance(timeLow, str) else self.timestamp(timeLow))
		timeHi = "{Hi}".format(Hi=timeHi if isinstance(timeHi, str) else self.timestamp(timeHi))

		assert (self.context.client.execute_command(

				"SETHOOK",
				self.name,
				self.endpoint,
				"INTERSECTS",
				self.context.name,
				"WHERE", "z",
				timeLow,
				timeHi,
				"FENCE",
				"DETECT",
				self.get_triggers(),

				"OBJECT",
				self.get_geofence_as_JSON(),
		))
		print(f"Webhook  with name: {self.name}, deployed at endpoint: {self.endpoint}")

	def get_geofence_as_JSON(self):
		# from dictionary FeatureCollection to JSON
		# so that server can understand it
		return json.dumps(self.data)

	def set_triggers(self, trigger):
		#       set which events will be emmited by webhook
		if trigger in self.ZONES:
			_zones = self.trigger
			return set(_zones).add(trigger)

	def get_triggers(self):
		# get the events allowed to be transmitted
		a = ",".join(self.trigger)
		print(a)
		return a

	def kill_webhook(self, ):
		# drops the webhook
		return self.context.client.execute_command("PDELHOOK", "{obj}".format(obj=self.name))


# @@@@@@@@@@@ TEST ZONE TEST ZONE TEST ZONE@@@@@@@@@@
##########################################################
main = Enviroment()

scooter = main.build_fleet(name="skouterakias", paths=DEFAULT_POINTS)
athens_dactylios = main.build_webhook(name="athens_dactylios", paths=DEFAULT_GEOFENCE).deploy_webhook()


def test_case(test_name, fleet_name, wh, int1, int2):
	if ARGS.get('defaults'):
		"""
		sets the default test parameters. (geofence /point files)
		Can be bypassed by setting  'default=False'
		when instantiating the class Enviroment
		"""
		##  example

		test_case = Enviroment(name=test_name)
		wh = test_case.build_webhook(name=wh, paths=DEFAULT_GEOFENCE)
		wh.deploy_webhook(int1, int2)

		scooter = test_case.build_fleet(name=fleet_name, paths=DEFAULT_POINTS)
		scooter.create_steps()
		scooter.run_sequence()
		time.sleep(1)

		scooter.drop_fleet()
		wh.kill_webhook()
		time.sleep(1)


test_case(
		test_name="test_1",
		wh="athens_dactylios1",
		int1=0,
		int2=60,
		fleet_name="case_1"
)

test_case(
		test_name="test_2",
		wh="athens_dactylios2",
		int1=0,
		int2=60,
		fleet_name="case_1"

)

test_case(
		test_name="test_2",
		wh="athens_dactylios3",
		int1=0,
		int2=60,
		fleet_name="case_2"

)
test_case(
		test_name="test_3",
		wh="athens_dactylios4",
		int1=0,
		int2=60,
		fleet_name="case_1"

)
test_case(
		test_name="test_3",
		wh="athens_dactylios5",
		int1="-inf",
		int2=-5,
		fleet_name="case_2"

)

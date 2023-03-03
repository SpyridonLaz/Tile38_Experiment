from  pathlib import Path
import time
from unittest import TestCase

from dispatch import Enviroment


class TestEnviroment(TestCase):

    def setUpClass(self):
        self.PATH = Path().absolute()
        print("Enviroment path: ", self.PATH)
        self.DEFAULT_GEOFENCE = [f"{self.PATH}/athens_dactylios.geojson"]
        self.DEFAULT_POINTS = [f"{self.PATH}/point_movement.geojson"]

        self.main = Enviroment()



class TestWebhook(TestEnviroment):

    def setUpClass(self) -> None:
        self.main = Enviroment()
        self.wh = self.main.build_webhook(name="athens_dactylios", paths=self.DEFAULT_GEOFENCE)

    def tearDown(self) -> None:
        self.wh.kill_webhook()
        time.sleep(1)

    def test_deploy_webhook(self):
        self.fail()

    def test_kill_webhook(self):
        self.fail()



class TestFleetVessel(TestEnviroment):
    def setUpClass(self) -> None:
        self.scooter = self.main.build_fleet(name="skouterakias", paths=self.DEFAULT_POINTS)

    def test_deploy(self):
        self.fail()

    def test_kill(self):
        self.fail()

    def test_get_status(self):
        self.fail()


class TestGenerics(TestEnviroment):
    def test_open_file(self):
        self.main.open_file( )



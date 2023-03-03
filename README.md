


Hypothesis:
We know that in Tile38 geofencing server, any position requires at least two spatial dimensions X,Y
(latitude,longitude) to be defined (haversine formula). The third coordinate Z is reserved for elevation(3rd
spatial dimension), zoom-in/out operations and other application-specific purposes,provided it is
expressed in integer or float numbers.
In addition, Time is also a dimension, although temporal instead of spatial , it can still be measured and
expressed in R numbers. So, it seems intuitively probable that the server, although understands integers
and floats, it is completely “blind” to the concepts of Space and Time and even though Z constitutes a
numerical expression of time, it would still take it into consideration in the interaction between tile38
objects. But we also know that a geofence calculates only spatial X,Y properties of an object in order to
determine it’s (new) position and transmit the proper Webhook event.
The hypothesis is that webhook emits events regardless of Z property, as long as the fence does not filter
against Z.
Problem:
We need to find out:
1. If a geofence is aware of any object points that have a Unix timestamp at Z.
Result: positive / negative
*types of event to consider: any
2. What types of events* are emitted from geofence webhook upon detection of object
on each case:
a) with Z timestamp .
b) without Z timestamp .
c) Result: Same / Different
*types of event to consider: cross,enter,inside,exit
3. What types of events* are emitted from geofence webhook upon detection of object that is
filtered against Z property:
a) with timestamp in accepted range.
b) With Z timestamp out of accepted range
*types of event to consider: cross,enter,inside,exit
Assessment Report
Experiment:

 First test
1. The following geofence is set:
SETHOOK zone {endpoint} INTERSECTS fleet FENCE OBJECT {athens_dactylios.geojson}
2. Move object to points to yield any detection.
3. Log results from endpoint.
4. Expected results: geofence to be aware
5. Reset enviroment: drop fleet & pdelhook *

 Second test
1. The geofence is set :
SETHOOK zone {endpoint} INTERSECTS fleet FENCE DETECT enter ,exit ,inside,cross
OBJECT {athens_dactylios.geojson}
2. Move object to points to yield any detection.
SET fleet scooter POINT lat lon
3. Log results from endpoint.
4.
 Move object to points to yield any detection.
SET fleet scooter POINT lat lon timestamp
5. Log results from endpoint.
6. Expected results: Results same.
7. Reset enviroment: drop fleet & pdelhook *

 Third test
1. The geofence is set :
SETHOOK zone {endpoint} INTERSECTS fleet FENCE DETECT enter ,exit ,inside,cross
WHERE z timestamp +inf OBJECT {athens_dactylios.geojson}
2. Move object to points as in point_movement.geojson to yield any detection.
"SET fleet scooter POINT lat lon timestamp
3. Log the results.
4. Reset enviroment: drop fleet & pdelhook *
5. The geofence is re-set :
Assessment Report
SETHOOK zone_athens_dactylios {endpoint} INTERSECTS fleet FENCE DETECT
enter ,exit ,inside,cross WHERE z -inf timestamp OBJECT {athens_dactylios.geojson}
6. Move object to points to yield detections.
SET fleet scooter POINT lat lon timestamp
7. Log the results.
8. Expected results: Results between the two tests will be different.
JSON file for key points : point_movement.geojson
JSON file for fence: athens_dactylios.geojson
Results as shown in log texts:
I.
 Test 1
i.
 log_test_1_case_1.txt
Success : Webhook is aware of objects that include timestamp at Z property
II. Test 2
i.
 log_test_2_case_1.txt
ii.
 log_test_2_case_2.txt
Success : Webhook emits same events between objects that have a timestamp Z and
those without.
III. Test 3
i.
 log_test_2_case_1.txt
ii.
 log_test_2_case_1.txt
Success : Webhook emits different results when objects are filtered against Z property
and are out of time range.
CONCLUSION:
In response to the initial question of the assignment, the answer is that indeed
Webhooks are completely aware of all the objects of a given collection that are set to
observe, regardless of wether the objects have a Z property or not.
However, when using a filter against Z , then the results are very different. Objects that are
either outside of the spatial boundaries X,Y and/or the temporal boundaries of Z trigger
events,but still detected as outside of the Geofence.
Assessment Report
PYTHON DOCUMENTATION
A) Commands:
1.
 Run
a) $ python3 -i dispatch.py from the main dir.
i.
 usage: Enviroment [-u URL] [-p PORT] [-d]
options:
-u [HOST], --url [HOST] server uri
-p [PORT], --port [PORT]
 server port : integer
-d, --defaults Enable default objects
2. Console:
a) main = Enviroment(
 )
(a) name = str
b) webhook = main.build_webhook(name=”test”)
 #(instantiated Webhook class)
params:
(a) name : str
(b) path = “filepath” ( optional)
ii. .deploy_webhook()
params: name
(a) trigger = Optional. automatic initially with defaults (enter,exit,inside,cross)
(b) timeLow: str or int = 0 distance from lowest filtering value- optional
(c) timeHi :str or int = 60 distance from highest filtering value- optional
iii. .kill_webhook()
params:
(a) all:bool = False if all == True →deletes all webhooks else deletes self
iv. .set_triggers( )
param:
B)Assessment Report
(a) trigger = list of strings of detection triggers
c) Fleet
i. scooter = main.build_fleet()
(a) name = required
(b) filepath of geoJson point object
(c)
ii.
 .create_steps(interval =0) builds Generator object that returns points one by one
interval : optional integer. time difference from timestamp in seconds. plus/
minus
iii. .run_step()
 generator - yields XY point and executes it in tile38 server
iv. .run_sequence()
 iterates the generator and executes all movements at once
v. .drop_fleet( ) drops current object from server
Technologies used:
i.
 Python 3.10
ii.
 Django rest framework as a basic oversimplified endpoint
iii. https://vector.rocks
iv. PyCharm
C) DJANGO CODE
class webhook(GenericViewSet, CreateModelMixin):
permission_classes = [AllowAny]
def create(self, request, *args, **kwargs):
import json
##get items from JSON
payload =json.loads(request.body)
log_detect= payload('detect')
Assessment Report
log_time =payload('time')
log_id =payload.get('id')
log_coords = payload.get('object').get('coordinates')
log_key = payload.get('key')
file =f"log_{log_key}_{log_id}.txt"
path = pathlib.Path(f"python_tile38_assign/test_cases/{file}")
path.parent.mkdir(parents=True, exist_ok=True)
path = path.resolve()
# print( "\n", "\n", )
print(payload,log_detect )
#
# print( "\n", "\n", )
_list = [
log_detect,
log_time,
log_coords,
log_id,
log_key,
]
_list= " : ".join([str(item) for item in _list])
with path.open ("a+") as f:
f.write(_list + "\n")
return Response(status=200)

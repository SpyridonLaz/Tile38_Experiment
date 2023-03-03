# Tile38 Experiment

## Hypothesis:

We know that in a Tile38 geofencing system, any position requires at least two spatial dimensions X,Y
(latitude,longitude) to be defined (haversine formula). The third coordinate Z is reserved for elevation(3rd
spatial dimension), zoom-in/out operations and other application-specific purposes,provided it is
expressed in integer or float numbers.
In addition, Time is also a dimension, although temporal instead of spatial , it can still be measured and
expressed in R numbers. So, it seems intuitively probable that the server, although understands integers
and floats, it is completely “blind” to the concepts of Space and Time and even though Z constitutes a
numerical expression of time, it would still take it into consideration in the interaction between tile38
objects. But we also know that a geofence calculates only spatial X,Y properties of an object in order to
determine it’s (new) position and transmit the proper Webhook event.

#### Assertion:

The hypothesis is that webhook emits events regardless of Z property, as long as the fence does not filter
against Z.

#### We need to figure:

1. If a geofence is aware of any object points that have a Unix timestamp at Z.

   **Result**: positive / negative

   **types of event to consider**: any
2. Which events* are emitted from geofence webhook upon detection of object
   on each case:
   a) with Z timestamp .
   b) without Z timestamp .

   **Result:** Same / Different

   **types of event to consider:** cross,enter,inside,exit
3. What types of events* are emitted from geofence webhook upon detection of object that is
   filtered against Z property:

   a) with timestamp in accepted range.

   b) With Z timestamp out of accepted range

   **types of event to consider:** cross,enter,inside,exit

## Experiment:

#### First test:

1. The following geofence is set:
   
   ```
   SETHOOK zone {endpoint} INTERSECTS fleet FENCE DETECT enter ,exit ,inside,cross
   OBJECT {athens_dactylios.geojson}
   ```
2. Move fleet object to the predefined points to yield any detection.
3. Log results from endpoint.
4. Expected results: geofence to be aware
5. Reset enviroment: `drop fleet & pdelhook *`

#### Second test

1. The geofence is set :
   
   ```
   SETHOOK zone {endpoint} INTERSECTS fleet FENCE DETECT enter ,exit           ,inside,cross
   OBJECT {athens_dactylios.geojson}
   ```
2. Move fleet object to points to yield any detection.
   
   ```
   SET fleet scooter POINT lat lon
   ```
3. Log results from endpoint.
4. Move object to points to yield any detection.
   
   ```
   SET fleet scooter POINT lat lon timestamp
   ```
5. Log results from endpoint.
6. Expected results: Results same.
7. Reset enviroment: `drop fleet & pdelhook *`

#### Third test

1. The geofence is set :
   
   ```
   SETHOOK zone {endpoint} INTERSECTS fleet FENCE DETECT enter ,exit ,inside,cross
   WHERE z timestamp +inf OBJECT {athens_dactylios.geojson}
   ```
2. Move object to points as in `point_movement.geojson` to yield any detection.
   
   ```
   SET fleet scooter POINT lat lon timestamp
   ```
3. Log the results.
4. Reset enviroment: `drop fleet & pdelhook *`
5. The geofence is re-set :
   
   ```
   SETHOOK zone_athens_dactylios {endpoint} INTERSECTS fleet FENCE DETECT
   enter ,exit ,inside,cross WHERE z -inf timestamp OBJECT  {athens_dactylios.geojson}
   ```
6. Move object to points to yield detections.
   
   ```
   SET fleet scooter POINT lat lon timestamp
   ```
7. Log the results.
8. Expected results: Results between the two tests will be different.
   JSON file for key points : point_movement.geojson
   JSON file for fence: athens_dactylios.geojson
   
   #### Results as shown in log texts:
   
   - Test 1
     
     - log_test_1_case_1.txt
       Success : Webhook is aware of objects that include timestamp at Z property
   - Test 2
     
     - log_test_2_case_1.txt
     - log_test_2_case_2.txt
     - Success : Webhook emits same events between objects that have a timestamp Z and
       those without.
   - Test 3
     
     - log_test_2_case_1.txt
     - log_test_2_case_1.txt
       Success : Webhook emits different results when objects are filtered against Z property
       and are out of time range.

# CONCLUSION:

In response to the initial question of the assignment, the answer is that indeed
Webhooks are completely aware of all the objects of a given collection that are set to
observe, regardless of wether the objects have a Z property or not.

However, when using a filter against Z , then the results are very different. 

**Objects that move
either beyond the spatial boundaries X,Y or the temporal boundaries of Z trigger
events, yet are detected as being outside of the geofence.**

## PYTHON DOCUMENTATION

#### Commands:

```
$ python3 -i dispatch.py
```

- usage: Enviroment [-u URL] [-p PORT] [-d]
  options:
  - -u [HOST], --url [HOST] server uri
  - -p [PORT], --port [PORT] server port : integer
  - -d, --defaults Enable default objects

2. Console:
   
   - `main = Enviroment( )`
     
     - name = str
   
   1. Webhook
   
   - `webhook = main.build_webhook(name=”test”)`
     #(instantiated Webhook class)
     
     - params:
       - `name : str`
       - `path = “filepath”` ( optional)
   - `.deploy_webhook()`
     
     - params: name
       - `trigger` : Optional. automatic initially with defaults (enter,exit,inside,cross)
       - `timeLow: str or int = 0` distance from lowest filtering value- optional
       - `timeHi :str or int = 60` distance from highest filtering value- optional
   - `.kill_webhook()`
     
     - params:
       - `all:bool = False if all == True` →deletes all webhooks else deletes self
   - `.set_triggers( )`
     
     - params:
       - trigger = list of strings of detection triggers
   
   2. Fleet
      - `scooter = main.build_fleet()`
        
        - name = required
        - filepath of geoJson point object
      - `.create_steps(interval =0)` builds Generator object that returns points one by one
        
        - interval : optional integer. time difference from timestamp in seconds. plus/
          minus
      - `.run_step()`
        generator - yields XY point and executes it in tile38 server
      - `.run_sequence()`
        iterates the generator and executes all movements at once
      - ` .drop_fleet( )` drops current object from server

## Technologies used:

- Python 3.10.7
- Django rest framework as a basic oversimplified endpoint
- [vector.rocks](https://vector.rocks)
- PyCharm

C) DJANGO CODE

```python
import json
class webhook(GenericViewSet, CreateModelMixin):
        permission_classes = [AllowAny]
        def create(self, request, *args, **kwargs):
             
                ##get items from JSON#
                payload =json.loads(request.body)
                log_detect= payload('detect')log_time =payload('time')
                log_id =payload.get('id')
                log_coords = payload.get('object').get('coordinates')
                log_key = payload.get('key')
                file =f"log_{log_key}_{log_id}.txt"
                path = pathlib.Path(f"python_tile38_assign/test_cases/{file}")
                path.parent.mkdir(parents=True, exist_ok=True)
                path = path.resolve()
                print(payload,log_detect )
                list = [ 
                       log_detect,
                        log_time,
                         log_coords,
                          log_id,
                            log_key,]
                 _list= " : ".join([str(item) for item in _list])
                 with path.open ("a+") as f:
                         f.write(_list + "\n")
                 return Response(status=200)
```




import os
from datetime import datetime
from sys import argv

import pytz

from person import Person
import folium
import json

with open("./simulated_traffic_script+json/10.json", "r") as json_file:
    data = json.load(json_file)
from folium.plugins import TimestampedGeoJson


def increase(longitude_latitude, _times, degree):
    if longitude_latitude == "latitude":
        x = 0
    # else is longitude
    else:
        x = 1
    is_present = True
    while is_present:
        no_match_found = 0
        for marker in no_overlay:
            existing_coords = marker[0]  # legt eigenen array nur für bereits existierende koordinaten an
            if existing_coords[x] == degree and marker[1] - _times < 60 * chosen_duration:
                degree = degree + 0.000008
                break  # loop beenden um laufzeit zu verringern
            else:
                no_match_found = no_match_found + 1
            if no_match_found == len(no_overlay):
                return degree


def decrease(longitude_latitude, _times, degree):
    if longitude_latitude == "latitude":
        x = 0
    # else is longitude
    else:
        x = 1
    is_present = True
    while is_present:
        no_match_found = 0
        for marker in no_overlay:
            existing_coords = marker[0]  # legt eigenen array nur für bereits existierende koordinaten an
            if existing_coords[x] == degree and marker[1] - _times < 60 * chosen_duration:
                degree = degree - 0.000008
                break  # loop beenden um laufzeit zu verringern
            else:
                no_match_found = no_match_found + 1
            if no_match_found == len(no_overlay):
                return degree


def increase_offset(coords, times):
    coords[0] = decrease("latitude", times, coords[0])
    coords[1] = decrease("longitude", times, coords[1])
    return coords


def decrease_offset(coords, times):
    coords[0] = decrease("latitude", times, coords[0])
    coords[1] = decrease("longitude", times, coords[1])
    return coords


def set_offset(coords, times, id):
    global offset_plus
    if offset_plus:
        offset_plus = False
        coords = increase_offset(coords, times)
    else:
        offset_plus = True
        coords = decrease_offset(coords, times)
    return coords


def create_waypoints(coords, _times, _id):
    is_to_add = True
    for i in range(len(no_overlay)):
        if no_overlay[i][0] != coords:  # check if coordinates already exist
            is_to_add = True
            continue
        else:  # if coordinates exist in array
            if no_overlay[i][1] == _times:  # check if times of those coordinates match
                is_to_add = False
                continue  # if so continue to prevent double entry
            else:
                if 0 < no_overlay[i][1] - _times < 60 * chosen_duration:
                    is_to_add = False
                    coords = set_offset(coords, _times, id)
                    no_overlay.append([coords, _times, _id])

    if is_to_add:
        no_overlay.append([coords, _times, _id])

    if len(no_overlay) == 0:
        no_overlay.append([coords, _times, _id])


def calculate_color(how_many):
    # 16777148 is FFFFBC in decimal, white is omitted
    return int(16777148 / how_many)


def seconds_to_cet(seconds):
    utc_time = datetime.utcfromtimestamp(seconds)
    utc_timezone = pytz.timezone("UTC")
    utc_aware_time = utc_timezone.localize(utc_time)
    cet_timezone = pytz.timezone("Europe/Berlin")
    cet_aware_time = utc_aware_time.astimezone(cet_timezone)
    return cet_aware_time.strftime('%Y-%m-%d %H:%M:%S %Z')


chosen_day = int(argv[1]) - 1
chosen_speed = int(argv[2])
chosen_speed_minutes_hours = "M" if argv[3] == "Minuten" else "H"
chosen_duration = int(argv[4]) if argv[5] == "Minuten" else int(argv[4]) * 60
chosen_duration_settings = argv[4]
chosen_duration_minutes_hours = "M" if argv[5] == "Minuten" else "H"
people = []
# cut off of "0x" from hex
mySlice = slice(2, 8, 1)

# initialize Person objects with coordinates and locations (home, work, free time)
for i in data["people"]:
    people.append(Person(i["id"], i["home_location"], i["workplace"], i["free_time_places"]))

color_breadth = calculate_color(len(people))
color = 0

# insert waypoints into upper objects and save indices of their locations (home, work, free time)
for id in range(len(data["daily_routes"][chosen_day])):
    for coord_or_according_time in range(len(data["daily_routes"][chosen_day][id]["coords"])):
        times = data["daily_routes"][chosen_day][id]["times"][coord_or_according_time]
        people[id].fill_arrays(data["daily_routes"][chosen_day][id]["coords"][coord_or_according_time],
                               data["daily_routes"][chosen_day][id]["times"][coord_or_according_time],
                               coord_or_according_time)

m = folium.Map(
    location=(52.27, 8.04),
    zoom_start=14,
    prefer_canvas=True
)

# Erstellen der Legende als HTML
legend_html = '''
<div style="position: absolute; 
     top: 0px; right: 0px; width: 100px; height: 200px; 
     border:2px solid grey; z-index:9999; font-size:14px;
     overflow: auto; background: rgba(188, 188, 188, 0.6);">
     &nbsp; Legende:
'''
# Array der IDs anlegen
id_array = []
for current_id in range(len(data["people"])):
    id_array.append(data["people"][current_id]["id"])

no_overlay = []
colors = []
opacity = 0.8
offset_plus = True

# Farben der IDs anlegen
for i in range(0, len(people)):
    colors.append(color)
    color = color + color_breadth

# Legende für IDs und deren Farben erzeugen
id_legende_html = ""
for i in range(len(colors)):
    id_color = "#" + str(hex(colors[id_array[i]]))[mySlice] if id_array[i] != 0 else "#000000"
    id_legende_html += ("""
    <br>
    &nbsp; ID: """ + str(id_array[i]) + """&nbsp; <div style="background:""" + id_color +
                        """;width:30px;height:15px;display:inline-block;"></div>""")

id_legende_html += """</div>"""
m.get_root().html.add_child(folium.Element(legend_html + id_legende_html))

for j in range(len(people)):
    for i in range(len(people[j].coords)):
        create_waypoints(data["daily_routes"][chosen_day][j]["coords"][i], data["daily_routes"][chosen_day][j]["times"][i],
                         data["people"][j]["id"])

features = [
    {
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [no_overlay[i][0][1], no_overlay[i][0][0]], [no_overlay[i + 1][0][1], no_overlay[i + 1][0][0]]
            ] if no_overlay[i][2] == no_overlay[i + 1][2] else [[no_overlay[i][0][1], no_overlay[i][0][0]],
                                                                [no_overlay[i][0][1], no_overlay[i][0][0]]],
        },
        "properties": {
            "id": str(no_overlay[i][2]),
            "tooltip": str(no_overlay[i][2]) + "<br>" + str(i + 1) + "<br>" + str(seconds_to_cet(no_overlay[i][1])),
            "times": [seconds_to_cet(no_overlay[i][1])[:-4].replace(" ", "T"),
                      seconds_to_cet(no_overlay[i + 1][1])[:-4].replace(" ", "T")],
            "style": {
                "color": "#" + str(hex(colors[no_overlay[i][2]])[mySlice]) if no_overlay[i][2] != 0 else "#000000",
                "weight": 5,
                "opacity": opacity,
            },
            "icon": "circle",
            "iconstyle": {
                "iconUrl": "./house-solid.svg",
                "fillColor": "#" + str(hex(colors[no_overlay[i][2]])[mySlice]),
                "fillOpacity": opacity,
                "radius": 3,
                "line_join": "square",
            },
        },
    }
    for i in range(len(no_overlay) - 1)
]

TimestampedGeoJson(
    {
        "type": "FeatureCollection",
        "features": features,
    },
    period="PT" + str(chosen_speed) + chosen_speed_minutes_hours,
    add_last_point=True,
    duration="PT" + chosen_duration_settings + chosen_duration_minutes_hours
).add_to(m)

m.save("marker.html")

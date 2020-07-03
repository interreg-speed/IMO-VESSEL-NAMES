import json
from datetime import datetime

from chromedriver_py import binary_path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class HAPAG:
    location_map = {}

    # def get_unlocode(self, city,state, country):
    #     possible_name = "%s, %s" % (city.lower(), country.lower())
    #     another_possible_name = "%s, %s, %s" % (city.lower(),state.lower(), country.lower())
    #     return self.location_map.get(another_possible_name, self.location_map.get(possible_name, "%s-%s-%s" % (city, state, country)) )

    def mapping_helper(self, items):
        eventType = ""
        fullStatus = "full"
        description = items[0]
        actual = items[-1]
        location = self.location_map.get(items[1].lower(), items[1])
        date = items[2]
        time = items[3]
        vessel = ""
        voyage = ""
        if actual:
            actual = "actual"
        else:
            actual = "estimated"

        if "Truck" in items or "Inland Transport" in items:
            if description == "Gate out empty":
                eventType = actual + "GateOut"
                fullStatus = "empty"
            elif description == "Gate in empty":
                eventType = actual + "GateIn"
                fullStatus = "empty"
            elif description == "Departure from":
                eventType = actual + "GateOut"
            elif description == "Arrival in":
                eventType = actual + "GateIn"
            else:
                eventType = actual + "" + description
        elif "Waterway" in items:
            if description == "Loaded":
                eventType = actual + "LoadedOnVessel"
            elif description == "Loading":
                eventType = actual + "LoadedOnVessel"
            elif description == "Discharged":
                eventType = actual + "DischargeFromVessel"
            elif description == "Discharge":
                eventType = actual + "DischargeFromVessel"
            elif description == "Departure from":
                eventType = actual + "VesselDeparture"
            elif description == "Arrival in":
                eventType = actual + "VesselArrival"
            elif description == "Vessel arrival":
                eventType = actual + "VesselArrival"
            elif description == "Vessel departure":
                eventType = actual + "VesselDeparture"
            elif description == "Vessel departed":
                eventType = actual + "VesselDeparture"
            elif description == "Vessel arrived":
                eventType = actual + "VesselArrival"
            else:
                print("Waterway other .... ")
        elif "Rail" in items:
            if description == "Departure from":
                eventType = actual + "RailDeparture"
            elif description == "Arrival in":
                eventType = actual + "RailArrival"
            else:
                eventName = actual + "" + description
                print(eventName)

        else:
            vessel = items[4]
            voyage = items[5]
            if description == "Loaded":
                eventType = actual + "LoadedOnVessel"
            elif description == "Loading":
                eventType = actual + "LoadedOnVessel"
            elif description == "Discharged":
                eventType = actual + "DischargeFromVessel"
            elif description == "Discharge":
                eventType = actual + "DischargeFromVessel"
            elif description == "Departure from":
                eventType = actual + "VesselDeparture"
            elif description == "Arrival in":
                eventType = actual + "VesselArrival"
            elif description == "Vessel arrival":
                eventType = actual + "VesselArrival"
            elif description == "Vessel departure":
                eventType = actual + "VesselDeparture"
            elif description == "Vessel departed":
                eventType = actual + "VesselDeparture"
            elif description == "Vessel arrived":
                eventType = actual + "VesselArrival"
            else:
                eventType = actual + " " + description
        dtime = date
        if len(time) > 0:
            datetime_str = date + "T" + time
            datetime_obj = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M')
            dtime = datetime_obj.isoformat()
        else:
            datetime_str = date + "T00:00"
            datetime_obj = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M')
            dtime = datetime_obj.isoformat()

        return [eventType, fullStatus, location, dtime, vessel, voyage]

    service = None
    driver = None

    def __init__(self):

        self.service = webdriver.chrome.service.Service(binary_path)
        self.service.start()

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        # chrome_options.binary_location = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
        self.driver = webdriver.Remote(self.service.service_url, desired_capabilities=chrome_options.to_capabilities())
        self.driver.implicitly_wait(20)

        with open('reports/MSC_Ports.json') as f:
            locations = json.load(f)
            self.location_map = {
                "%s, %s" % (item.get("LocationName").lower(), item.get("CountryIsoCode").lower()): item.get(
                    "LocationCode") for item in
                locations}

        with open('reports/TL_UNLOCODE.json') as f:
            obj = json.load(f)
            for location in obj.get("locations"):
                self.location_map[location.get("name").lower()] = location.get("unlocode")
                city = location.get("name").lower().split(",")[0]
                if city not in self.location_map:
                    self.location_map[city] = location.get("unlocode")

    def parse_event(self, item):
        tl_event = {}
        eventType, fullStatus, location, dtime, vessel, voyage = self.mapping_helper(item)
        tl_event["eventType"] = eventType
        tl_event["fullStatus"] = fullStatus
        if len(voyage) > 0:
            tl_event["voyageId"] = voyage
        if len(vessel) > 0:
            tl_event["vehicleName"] = vessel
        tl_event['eventOccurrenceTime8601'] = dtime
        tl_event['eventSubmissionTime8601'] = dtime

        if len(location) == 5:
            tl_event['location'] = {"type": "UN/Locode", "value": location}
        else:
            tl_event['location'] = {
                "type": "address",
                "value": location
            }

        return tl_event

    def load_consignment_page(self, bill_of_lading_number='HLCUNG12005BARE9'):
        url = "https://www.hapag-lloyd.com/en/online-business/tracing/tracing-by-booking.html?blno=%s" % bill_of_lading_number
        self.driver.get(url)
        return

    def load_consignment(self):
        containers = []
        for container_row in self.driver.find_elements_by_css_selector('table.data>tbody>tr'):
            row = [elem.text for elem in container_row.find_elements_by_tag_name("td")]
            containers.append(row)

        return containers

    def load_container_page(self, container=""):
        self.driver.get(
            "https://www.hapag-lloyd.com/en/online-business/tracing/tracing-by-booking.html?view=S8510&container=%s" %
            container)
        return

    def load_container(self, cbn, bol):
        all_events = []
        for event_row in self.driver.find_elements_by_css_selector('table.data>tbody>tr'):
            items = event_row.find_elements_by_tag_name("td")
            row = [elem.text for elem in items]
            actual = False
            if len(items) > 0:
                actual = "strong" in items[1].get_attribute("class")
            row.append(actual)
            all_events.append(row)

        return all_events

    def parse_events(self, tl_cbn, bill_of_lading_number, equipment, hl_events):
        events = []
        final_arrival = None
        first_depart = None
        for event in hl_events:
            try:
                tl_event = self.parse_event(event)
                self.set_originator(tl_event)
                tl_event["carrierBookingNumber"] = tl_cbn
                tl_event["billOfLadingNumber"] = bill_of_lading_number
                tl_event["equipmentNumber"] = equipment.replace(" ", "")
                if "VesselArrival" in tl_event["eventType"]:
                    final_arrival = tl_event
                if "VesselDeparture" in tl_event["eventType"] and first_depart is None:
                    first_depart = tl_event
                events.append(tl_event)
            except Exception as e:
                print("failed to parse %s" % e)
        phase = "Export"
        for event in events:
            event["transportationPhase"] = phase
            if event == first_depart:
                phase = "transshipment"
            elif event == final_arrival:
                phase = "import"

        return events

    def get_data(self, cbn, bol):
        self.load_consignment_page(bol)
        containers = self.load_consignment()
        all_tl_events = []
        for container in containers:
            self.load_container_page(container[2])
            hl_events = self.load_container(cbn, bol)
            tl_events = self.parse_events(cbn, bol, container[2], hl_events)
            all_tl_events += tl_events

        return all_tl_events

    consignment = {
        "eventSubmissionTime8601": None,
        "carrierBookingNumber": None,
        "billOfLadingNumber": None,
        "bookingData": {
            "originLocation": {},
            "destinationLocation": {},
            "departureTime8601": None,
            "vehicleId": None,
            "vehicleName": None,
            "voyageId": None,
            "transportEquipmentDetails": []
        }
    }
    consignment_te = {"equipmentType": None, "equipmentQuantity": None}
    consignment_commodity = {
        "itemNumber": None,
        "commodityDescription": None,
        "commodityHarmonizedCode": None,
        "commodityQuantity": None,
        "commodityWeight": None}

    transportEquipment = {
        "eventSubmissionTime8601": None,
        "carrierBookingNumber": None,
        "equipmentNumber": None}
    tes = {}

    def set_originator(self, event):
        event["originatorName"] = "Happag-Lloyd"
        event["originatorId"] = "HLCU"

    def parse_admin(self, tl_events):
        first_event = tl_events[-1]
        last_event = tl_events[0]
        first_vessel = None
        for event in tl_events:
            if "vessel" in event.get("eventType", "").lower() and first_vessel is None:
                first_vessel = event
            if event.get("equipmentNumber") not in self.tes:
                te = json.loads(json.dumps(self.transportEquipment))
                self.set_originator(te)
                te["equipmentNumber"] = event.get("equipmentNumber")
                te["carrierBookingNumber"] = event.get("carrierBookingNumber")
                te["eventSubmissionTime8601"] = first_event.get("eventSubmissionTime8601")
                self.tes[event.get("equipmentNumber")] = te
        self.set_originator(self.consignment)
        self.consignment["carrierBookingNumber"] = first_event.get("carrierBookingNumber")
        self.consignment["billOfLadingNumber"] = first_event.get("billOfLadingNumber")
        self.consignment["eventSubmissionTime8601"] = first_event.get("eventSubmissionTime8601")

        if first_event.get("location", {}).get("type") == "UN/Locode":
            self.consignment["bookingData"]["originLocation"]["unlocode"] = first_event.get("location", {}).get("value")
        else:
            self.consignment["bookingData"]["originLocation"]["type"] = "address"
            self.consignment["bookingData"]["originLocation"]["value"] = first_event.get("location", {}).get("value")

        if last_event.get("location", {}).get("type") == "UN/Locode":
            self.consignment["bookingData"]["destinationLocation"]["unlocode"] = last_event.get("location", {}).get(
                "value")
        else:
            self.consignment["bookingData"]["destinationLocation"]["type"] = "address"
            self.consignment["bookingData"]["destinationLocation"]["value"] = last_event.get("location", {}).get(
                "value")

        # self.consignment["bookingData"]["originLocation"]["unlocode"] = first_event.get("location", {}).get("unlocode")
        # self.consignment["bookingData"]["destinationLocation"]["unlocode"] = last_event.get("location", {}).get("unlocode")
        self.consignment["bookingData"]["departureTime8601"] = first_vessel.get("eventOccurrenceTime8601", "") + "Z"
        self.consignment["bookingData"]["vehicleId"] = first_vessel.get("vehicleId")
        self.consignment["bookingData"]["vehicleName"] = first_vessel.get("vehicleName")
        self.consignment["bookingData"]["voyageId"] = first_vessel.get("voyageId")
        return self.consignment, self.tes

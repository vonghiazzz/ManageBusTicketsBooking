# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []

# actions.py

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet

from rasa_sdk.executor import CollectingDispatcher
import sqlite3
import requests

# class ActionQueryDatabase(Action):

#     def name(self) -> Text:
#         return "action_query_database"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#         start = tracker.get_slot('departure')
#         end = tracker.get_slot('destination')
#         travel_date = tracker.get_slot('date')  # Assuming the slot name for date is 'date'

#         # Kết nối tới database
#         database_path = r'D:\AllProject\Website\Python\Web\Final\ManageBusTicketsBooking\db.sqlite3'

#         connection = sqlite3.connect(database_path)

#         try:
#             cursor = connection.cursor()

#             # Kiểm tra xem slot 'date' có giá trị hay không
#             if travel_date:
#                 # Query để lấy dữ liệu từ bảng Trip và Route với giới hạn 3 kết quả và kiểm tra ngày khởi hành
#                 sql = """
#                 SELECT trip.id, route.startPoint, route.endPoint 
#                 FROM app_trip trip
#                 INNER JOIN app_route route ON trip.id_Route_id = route.id
#                 WHERE route.startPoint = ? AND route.endPoint = ? AND DATE(trip.departure_Time) = ?
#                 LIMIT 1
#                 """
#                 cursor.execute(sql, (start, end, travel_date))
#             else:
#                 # Query để lấy dữ liệu từ bảng Trip và Route với giới hạn 3 kết quả mà không kiểm tra ngày khởi hành
#                 sql = """
#                 SELECT trip.id, route.startPoint, route.endPoint 
#                 FROM app_trip trip
#                 INNER JOIN app_route route ON trip.id_Route_id = route.id
#                 WHERE route.startPoint = ? AND route.endPoint = ?
#                 LIMIT 1
#                 """
#                 cursor.execute(sql, (start, end))

#             result = cursor.fetchall()

#             # Kiểm tra kết quả và gửi phản hồi tới người dùng
#             if result:
#                 trips_info = []
#                 for trip in result:
#                     trip_info = {
#                         "id": trip[0],
#                         "startPoint": trip[1],
#                         "endPoint": trip[2]
#                     }
#                     trips_info.append(trip_info)
                
#                 response = f"Result: {trips_info}"
#                 # Truyền id trip vào URL
#                 for trip in trips_info:
#                     trip_id = trip["id"]
#                     url = f"http://127.0.0.1:8000/booking/{trip_id}/"
#                     dispatcher.utter_message(text=f"Click here to view trip : <a href='{url}' target='_blank'>Click here to view trip</a>")
#             else:
#                 response = "No trips found."

#             dispatcher.utter_message(text=response)

#         except Exception as e:
#             dispatcher.utter_message(text=f"Error: {e}")

#         finally:
#             connection.close()

#         return []

class ActionQueryDatabase(Action):

    def name(self) -> Text:
        return "action_query_database"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        start = tracker.get_slot('departure')
        end = tracker.get_slot('destination')
        # dispatcher.utter_message(text=f"departure is {start} to destination is {end}.")

        # Kết nối tới database
        database_path = r'D:\AllProject\Website\Python\Web\Final\ManageBusTicketsBooking\db.sqlite3'

        connection = sqlite3.connect(database_path)

        try:
            cursor = connection.cursor()

            # Query để lấy dữ liệu từ bảng Trip và Route với giới hạn 3 kết quả
            sql = """
            SELECT trip.id, route.startPoint, route.endPoint 
            FROM app_trip trip
            INNER JOIN app_route route ON trip.id_Route_id = route.id
            WHERE route.startPoint = ? AND route.endPoint = ?
            LIMIT 1
            """
            cursor.execute(sql, (start, end))
            result = cursor.fetchall()

            # Kiểm tra kết quả và gửi phản hồi tới người dùng
            if result:
                trips_info = []
                for trip in result:
                    trip_info = {
                        "id": trip[0],
                        "startPoint": trip[1],
                        "endPoint": trip[2],
                    }
                    trips_info.append(trip_info)
                
                response = f"Result: {trips_info}"
                # Truyền id trip vào URL
                for trip in trips_info:
                    trip_id = trip["id"]
                    url = f"http://127.0.0.1:8000/booking/{trip_id}/"
                    requests.get(url)
                dispatcher.utter_message(text=f"Click here to clear view trip : <a href='{url}' target='_blank'>{start} -> {end}</a>")
            else:
                response = "No trip found. Please, can you choose another trip?"

            dispatcher.utter_message(text=response)

        except Exception as e:
            dispatcher.utter_message(text=f"Error: {e}")

        finally:
            connection.close()

        return []
    

class ActionAskPrice(Action):

    def name(self) -> Text:
        return "action_ask_price"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        start = tracker.get_slot('departure')
        end = tracker.get_slot('destination')
        # dispatcher.utter_message(text=f"departure is {start} to destination is {end}.")
        print("start: ",start)
        print("end: ",end)

        # Kết nối tới database
        database_path = r'D:\AllProject\Website\Python\Web\Final\ManageBusTicketsBooking\db.sqlite3'

        connection = sqlite3.connect(database_path)

        try:
            cursor = connection.cursor()

            # Query để lấy dữ liệu từ bảng Trip và Route với giới hạn 3 kết quả
            sql = """
            SELECT trip.id, route.startPoint, route.endPoint, trip.price
            FROM app_trip trip
            INNER JOIN app_route route ON trip.id_Route_id = route.id
            WHERE route.startPoint = ? AND route.endPoint = ?
            LIMIT 1
            """
            cursor.execute(sql, (start, end))
            result = cursor.fetchall()

            # Kiểm tra kết quả và gửi phản hồi tới người dùng
            if result:
                trips_info = []
                for trip in result:
                    trip_info = {
                        "id": trip[0],
                        "startPoint": trip[1],
                        "endPoint": trip[2],
                        "price":trip[3],

                    }
                    trips_info.append(trip_info)
                
                response = f"Trip from {trip_info['startPoint']} to {trip_info['endPoint']} costs {trip_info['price']}. Click here to clear view trip: <a href='http://127.0.0.1:8000/booking/{trip_info['id']}/' target='_blank'>{start} -> {end}</a>"
                dispatcher.utter_message(text=response)

            else:
                response = "No trip found. Please, can you choose another trip?"

            # dispatcher.utter_message(text=response)

        except Exception as e:
            dispatcher.utter_message(text=f"Error: {e}")

        finally:
            connection.close()

        return []
# class ActionQueryDatabase(Action):

#     def name(self) -> Text:
#         return "action_query_database"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#         departure = tracker.get_slot('departure')
#         destination = tracker.get_slot('destination')
#         dispatcher.utter_message(text=f"departure is {departure} to destination is {destination}.")

#         # Kết nối tới database
#         database_path = r'D:\AllProject\Website\Python\Web\Final\ManageBusTicketsBooking\db.sqlite3'

#         connection = sqlite3.connect(database_path)

#         try:
#             cursor = connection.cursor()

#             # Viết query để lấy dữ liệu từ database
#             sql = "SELECT * FROM app_trip WHERE departure=? AND  destination=?"
#             cursor.execute(sql, (departure,destination))
#             # result = cursor.fetchone()
#             result = cursor.fetchall()


#             # Kiểm tra kết quả và gửi phản hồi tới người dùng
#             if result:
#                 dispatcher.utter_message(text=f"We found {len(result)} routes from {departure} to {destination}.")
#                 return [SlotSet("trips", result)]            
#             else:
#                 dispatcher.utter_message(text="Sorry, we couldn't find any routes matching your criteria.")
#                 return []
#         except Exception as e:
#             dispatcher.utter_message(text=f"Error: {e}")
#             return []

#         finally:
#             connection.close()

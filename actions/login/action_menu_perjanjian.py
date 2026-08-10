from typing import Any, Dict, List, Text
import requests

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

class MenuPerjanjian(Action):
    def name(self) -> Text:
        return "action_menu_perjanjian"
    
    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        
        pilihan_menu = tracker.get_slot("menu_perjanjian")
        confirmation = tracker.get_slot("menu_perjanjian_confirmation")

        if confirmation is False:
            dispatcher.utter_message(response="utter_menu_perjanjian_cancelled")
            return [
                SlotSet("menu_perjanjian", None),
                SlotSet("menu_perjanjian_confirmation", None)
            ]

        dispatcher.utter_message(response = "utter_menu_perjanjian_ok")
        dispatcher.utter_message(json_message={"context": "perjanjian"})
        
        def fetch_peraturan_api(sender: str, context_name: str) -> bool:
            try:
                payload = {
                    "IdLogin": sender,
                    "context": context_name
                }
                response = requests.post(
                    "https://sismob.trisakti.ac.id/api/get-peraturan",
                    json=payload,
                    timeout=10
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == 200 and "body" in data and "data" in data["body"] and data["body"]["data"]:
                        aturan = data["body"]["data"].get("aturan")
                        if aturan:
                            dispatcher.utter_message(text=aturan)
                            return True
            except Exception as e:
                print(f"Failed to fetch from get-peraturan API: {e}")
            return False

        match pilihan_menu:
            case "Prosedur Perjanjian":
                if not fetch_peraturan_api(tracker.sender_id, "perjanjian_prosedur"):
                    dispatcher.utter_message(response="utter_answer_prosedur_perjanjian")
            case "Persyaratan Perjanjian":
                if not fetch_peraturan_api(tracker.sender_id, "perjanjian_persyaratan"):
                    dispatcher.utter_message(response="utter_answer_persyaratan_perjanjian")
            case "Transaksi Perjanjian":
                dispatcher.utter_message(response="utter_answer_transaksi_perjanjian")
            case "Hasil Perjanjian":
                if not fetch_peraturan_api(tracker.sender_id, "perjanjian_hasil"):
                    dispatcher.utter_message(response="utter_answer_hasil_perjanjian")
            case _:
                pass

        return [
            SlotSet("menu_perjanjian", None),
            SlotSet("menu_perjanjian_confirmation", None)
        ]

from typing import Any, Dict, List, Text
import requests

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

class MenuHasilSeleksi(Action):
    def name(self) -> Text:
        return "action_menu_hasil_seleksi"
    
    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        
        pilihan_menu = tracker.get_slot("menu_hasil_seleksi")
        confirmation = tracker.get_slot("menu_hasil_seleksi_confirmation")

        if confirmation is False:
            dispatcher.utter_message(response="utter_menu_hasil_seleksi_cancelled")
            return [
                SlotSet("menu_hasil_seleksi", None),
                SlotSet("menu_hasil_seleksi_confirmation", None)
            ]

        dispatcher.utter_message(response = "utter_menu_hasil_seleksi_ok")
        dispatcher.utter_message(json_message={"context": "hasil_seleksi"})
        
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
            case "Prosedur Hasil Seleksi":
                if not fetch_peraturan_api(tracker.sender_id, "hasil_seleksi_prosedur"):
                    dispatcher.utter_message(response="utter_answer_prosedur_hasil_seleksi")
            case "Persyaratan Hasil Seleksi":
                if not fetch_peraturan_api(tracker.sender_id, "hasil_seleksi_persyaratan"):
                    dispatcher.utter_message(response="utter_answer_persyaratan_hasil_seleksi")
            case "Hasil Hasil Seleksi":
                if not fetch_peraturan_api(tracker.sender_id, "hasil_seleksi_hasil"):
                    dispatcher.utter_message(response="utter_answer_hasil_hasil_seleksi")
            case _:
                pass

        return [
            SlotSet("menu_hasil_seleksi", None),
            SlotSet("menu_hasil_seleksi_confirmation", None)
        ]

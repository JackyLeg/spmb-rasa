from typing import Any, Dict, List, Text
import requests

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

class MenuKartuUjian(Action):
    def name(self) -> Text:
        return "action_menu_kartu_ujian"
    
    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        
        pilihan_menu = tracker.get_slot("menu_kartu_ujian")
        confirmation = tracker.get_slot("menu_kartu_ujian_confirmation")

        if confirmation is False:
            dispatcher.utter_message(response="utter_menu_kartu_ujian_cancelled")
            return [
                SlotSet("menu_kartu_ujian", None),
                SlotSet("menu_kartu_ujian_confirmation", None)
            ]

        dispatcher.utter_message(response = "utter_menu_kartu_ujian_ok")
        dispatcher.utter_message(json_message={"context": "kartu_ujian"})
        
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

        if pilihan_menu == "Prosedur Kartu Ujian":
                if not fetch_peraturan_api(tracker.sender_id, "kartu_ujian_prosedur"):
                    dispatcher.utter_message(response="utter_answer_prosedur_kartu_ujian")
        elif pilihan_menu == "Persyaratan Kartu Ujian":
                if not fetch_peraturan_api(tracker.sender_id, "kartu_ujian_persyaratan"):
                    dispatcher.utter_message(response="utter_answer_persyaratan_kartu_ujian")
        elif pilihan_menu == "Hasil Kartu Ujian":
                if not fetch_peraturan_api(tracker.sender_id, "kartu_ujian_hasil"):
                    dispatcher.utter_message(response="utter_answer_hasil_kartu_ujian")
        else:
                pass

        return [
            SlotSet("menu_kartu_ujian", None),
            SlotSet("menu_kartu_ujian_confirmation", None)
        ]

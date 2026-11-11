from typing import Any, Dict, List, Text
import requests

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

class MenuDiskonAlumni(Action):
    def name(self) -> Text:
        return "action_menu_diskon_alumni"
    
    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        
        pilihan_menu = tracker.get_slot("menu_diskon_alumni")
        confirmation = tracker.get_slot("menu_diskon_alumni_confirmation")

        if confirmation is False:
            dispatcher.utter_message(response="utter_menu_diskon_alumni_cancelled")
            return [
                SlotSet("menu_diskon_alumni", None),
                SlotSet("menu_diskon_alumni_confirmation", None)
            ]

        dispatcher.utter_message(response = "utter_menu_diskon_alumni_ok")
        dispatcher.utter_message(json_message={"context": "diskon_alumni"})
        
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

        if pilihan_menu == "Prosedur Diskon Alumni":
                if not fetch_peraturan_api(tracker.sender_id, "diskon_alumni_prosedur"):
                    dispatcher.utter_message(response="utter_answer_prosedur_diskon_alumni")
        elif pilihan_menu == "Persyaratan Diskon Alumni":
                if not fetch_peraturan_api(tracker.sender_id, "diskon_alumni_persyaratan"):
                    dispatcher.utter_message(response="utter_answer_persyaratan_diskon_alumni")
        elif pilihan_menu == "Transaksi Diskon Alumni":
                dispatcher.utter_message(response="utter_answer_transaksi_diskon_alumni")
        elif pilihan_menu == "Hasil Diskon Alumni":
                if not fetch_peraturan_api(tracker.sender_id, "diskon_alumni_hasil"):
                    dispatcher.utter_message(response="utter_answer_hasil_diskon_alumni")
        else:
                pass

        return [
            SlotSet("menu_diskon_alumni", None),
            SlotSet("menu_diskon_alumni_confirmation", None)
        ]

from typing import Any, Dict, List, Text
import requests

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

class MenuPendaftaran(Action):
    def name(self) -> Text:
        return "action_menu_pendaftaran"
    
    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        
        pilihan_menu = tracker.get_slot("menu_pendaftaran")
        confirmation = tracker.get_slot("menu_pendaftaran_confirmation")

        if confirmation is False:
            dispatcher.utter_message(response="utter_menu_pendaftaran_cancelled")
            return [
                SlotSet("menu_pendaftaran", None),
                SlotSet("menu_pendaftaran_confirmation", None)
            ]

        dispatcher.utter_message(response = "utter_menu_pendaftaran_ok")
        dispatcher.utter_message(json_message={"context": "pendaftaran"})
        
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

        if pilihan_menu == "Prosedur Pendaftaran":
                if not fetch_peraturan_api(tracker.sender_id, "pendaftaran_prosedur"):
                    dispatcher.utter_message(response="utter_answer_prosedur_pendaftaran")
        elif pilihan_menu == "Persyaratan Pendaftaran":
                if not fetch_peraturan_api(tracker.sender_id, "pendaftaran_persyaratan"):
                    dispatcher.utter_message(response="utter_answer_persyaratan_pendaftaran")
        elif pilihan_menu == "Transaksi Pendaftaran":
                dispatcher.utter_message(response="utter_answer_transaksi_pendaftaran")
        elif pilihan_menu == "Hasil Pendaftaran":
                if not fetch_peraturan_api(tracker.sender_id, "pendaftaran_hasil"):
                    dispatcher.utter_message(response="utter_answer_hasil_pendaftaran")
        else:
                pass

        return [
            SlotSet("menu_pendaftaran", None),
            SlotSet("menu_pendaftaran_confirmation", None)
        ]

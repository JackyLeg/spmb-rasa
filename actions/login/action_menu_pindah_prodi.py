from typing import Any, Dict, List, Text
import requests

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

class MenuPindahProdi(Action):
    def name(self) -> Text:
        return "action_menu_pindah_prodi"
    
    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        
        pilihan_menu = tracker.get_slot("menu_pindah_prodi")
        confirmation = tracker.get_slot("menu_pindah_prodi_confirmation")

        if confirmation is False:
            dispatcher.utter_message(response="utter_menu_pindah_prodi_cancelled")
            return [
                SlotSet("menu_pindah_prodi", None),
                SlotSet("menu_pindah_prodi_confirmation", None)
            ]

        dispatcher.utter_message(response = "utter_menu_pindah_prodi_ok")
        dispatcher.utter_message(json_message={"context": "pindah_prodi"})
        
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

        if pilihan_menu == "Prosedur Pindah Prodi":
                if not fetch_peraturan_api(tracker.sender_id, "pindah_prodi_prosedur"):
                    dispatcher.utter_message(response="utter_answer_prosedur_pindah_prodi")
        elif pilihan_menu == "Persyaratan Pindah Prodi":
                if not fetch_peraturan_api(tracker.sender_id, "pindah_prodi_persyaratan"):
                    dispatcher.utter_message(response="utter_answer_persyaratan_pindah_prodi")
        elif pilihan_menu == "Transaksi Pindah Prodi":
                dispatcher.utter_message(response="utter_answer_transaksi_pindah_prodi")
        elif pilihan_menu == "Hasil Pindah Prodi":
                if not fetch_peraturan_api(tracker.sender_id, "pindah_prodi_hasil"):
                    dispatcher.utter_message(response="utter_answer_hasil_pindah_prodi")
        else:
                pass

        return [
            SlotSet("menu_pindah_prodi", None),
            SlotSet("menu_pindah_prodi_confirmation", None)
        ]

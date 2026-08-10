from typing import Any, Dict, List, Text
import requests

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

class MenuPembayaran(Action):
    def name(self) -> Text:
        return "action_menu_pembayaran"
    
    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        
        pilihan_menu = tracker.get_slot("menu_pembayaran")
        confirmation = tracker.get_slot("menu_pembayaran_confirmation")

        if confirmation is False:
            dispatcher.utter_message(response="utter_menu_pembayaran_cancelled")
            return [
                SlotSet("menu_pembayaran", None),
                SlotSet("menu_pembayaran_confirmation", None)
            ]

        dispatcher.utter_message(response = "utter_menu_pembayaran_ok")
        dispatcher.utter_message(json_message={"context": "pembayaran"})
        
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
            case "Prosedur Pembayaran":
                if not fetch_peraturan_api(tracker.sender_id, "pembayaran_prosedur"):
                    dispatcher.utter_message(response="utter_answer_prosedur_pembayaran")
            case "Persyaratan Pembayaran":
                if not fetch_peraturan_api(tracker.sender_id, "pembayaran_persyaratan"):
                    dispatcher.utter_message(response="utter_answer_persyaratan_pembayaran")
            case "Transaksi Pembayaran":
                dispatcher.utter_message(response="utter_answer_transaksi_pembayaran")
            case "Hasil Pembayaran":
                if not fetch_peraturan_api(tracker.sender_id, "pembayaran_hasil"):
                    dispatcher.utter_message(response="utter_answer_hasil_pembayaran")
            case _:
                pass

        return [
            SlotSet("menu_pembayaran", None),
            SlotSet("menu_pembayaran_confirmation", None)
        ]

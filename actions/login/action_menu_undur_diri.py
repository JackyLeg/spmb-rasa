from typing import Any, Dict, List, Text
import requests

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

class MenuUndurDiri(Action):
    def name(self) -> Text:
        return "action_menu_undur_diri"
    
    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        
        pilihan_menu = tracker.get_slot("menu_undur_diri")
        confirmation = tracker.get_slot("menu_undur_diri_confirmation")

        if confirmation is False:
            dispatcher.utter_message(response="utter_menu_undur_diri_cancelled")
            return [
                SlotSet("menu_undur_diri", None),
                SlotSet("menu_undur_diri_confirmation", None)
            ]

        dispatcher.utter_message(response = "utter_menu_undur_diri_ok")
        dispatcher.utter_message(json_message={"context": "pembatalan_pendaftaran"})
        
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

        if pilihan_menu in ["Prosedur Undur Diri", "Prosedur Pembatalan Pendaftaran"]:
            if not (fetch_peraturan_api(tracker.sender_id, "pembatalan_pendaftaran_prosedur") or fetch_peraturan_api(tracker.sender_id, "undur_diri_prosedur")):
                dispatcher.utter_message(response="utter_answer_prosedur_undur_diri")
        elif pilihan_menu in ["Persyaratan Undur Diri", "Persyaratan Pembatalan Pendaftaran"]:
            if not (fetch_peraturan_api(tracker.sender_id, "pembatalan_pendaftaran_persyaratan") or fetch_peraturan_api(tracker.sender_id, "undur_diri_persyaratan")):
                dispatcher.utter_message(response="utter_answer_persyaratan_undur_diri")
        elif pilihan_menu in ["Transaksi Undur Diri", "Transaksi Pembatalan Pendaftaran"]:
            dispatcher.utter_message(response="utter_answer_transaksi_undur_diri")
        elif pilihan_menu in ["Hasil Undur Diri", "Hasil Pembatalan Pendaftaran"]:
            if not (fetch_peraturan_api(tracker.sender_id, "pembatalan_pendaftaran_hasil") or fetch_peraturan_api(tracker.sender_id, "undur_diri_hasil")):
                dispatcher.utter_message(response="utter_answer_hasil_undur_diri")
        else:
            pass

        return [
            SlotSet("menu_undur_diri", None),
            SlotSet("menu_undur_diri_confirmation", None)
        ]

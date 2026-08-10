from typing import Any, Dict, List, Text
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

class ActionShowMenu(Action):
    def name(self) -> Text:
        return "action_show_menu"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        
        login_state = tracker.get_slot("login_state")
        if login_state == "login":
            dispatcher.utter_message(response="utter_ask_list_menu_spmb")
        else:
            dispatcher.utter_message(response="utter_ask_list_menu_not_login")
        return []

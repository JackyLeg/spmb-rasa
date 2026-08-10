from typing import Any, Text, Dict, List
import requests
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

class ActionCheckLoginState(Action):
    def name(self) -> Text:
        return "action_check_login_state"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        login_state = tracker.get_slot("login_state")
        
        if not login_state:
            # try:
            #     # Query the get-role API to check if the sender_id has a valid logged-in session/role
            #     role_response = requests.post(
            #         "https://sismob.trisakti.ac.id/api/get-role",
            #         json={"IdLogin": tracker.sender_id},
            #         timeout=10
            #     )
            #     if role_response.status_code == 200:
            #         role = role_response.json().get("role")
            #         # If a role is found and it is not "No Role" or empty, they are logged in
            #         if role and role != "No Role":
            #             login_state = "login"
            #         else:
            #             login_state = "not_login"
            #     else:
            #         login_state = "not_login"
            # except Exception as e:
            #     print(f"Failed to fetch get-role API for login state: {e}")
            #     login_state = "not_login"
            login_state = "not_login"

        return [SlotSet("login_state", login_state)]


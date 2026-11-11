from skills.base import BaseSkill


class BookRideSkill(BaseSkill):
    name = "book_ride"
    required_fields = ["pickup", "destination"]

    def run(self, params: dict, session: dict) -> dict:
        missing = self.get_missing_fields(params)

        if missing:
            return {
                "status": "need_input",
                "missing_fields": missing,
                "message": f"I need these details for the ride: {', '.join(missing)}."
            }

        return {
            "status": "awaiting_approval",
            "summary": {
                "skill": self.name,
                "pickup": params.get("pickup"),
                "destination": params.get("destination"),
                "time": params.get("time", "now")
            },
            "message": f"I am ready to book your ride from {params.get('pickup')} to {params.get('destination')}."
        }

    def execute(self, params: dict, session: dict) -> dict:
        return {
            "status": "success",
            "message": f"Ride execution placeholder: booking ride from {params.get('pickup')} to {params.get('destination')} at {params.get('time', 'now')}."
        }
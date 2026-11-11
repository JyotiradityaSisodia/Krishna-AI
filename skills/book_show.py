from skills.base import BaseSkill


class BookShowSkill(BaseSkill):
    name = "book_show"
    required_fields = ["show_name"]

    def run(self, params: dict, session: dict) -> dict:
        missing = self.get_missing_fields(params)

        if missing:
            return {
                "status": "need_input",
                "missing_fields": missing,
                "message": f"I need these details for show booking: {', '.join(missing)}."
            }

        return {
            "status": "awaiting_approval",
            "summary": {
                "skill": self.name,
                "show_name": params.get("show_name")
            },
            "message": f"I am ready to help book the show '{params.get('show_name')}'."
        }

    def execute(self, params: dict, session: dict) -> dict:
        return {
            "status": "success",
            "message": f"Show execution placeholder: booking show '{params.get('show_name')}'."
        }
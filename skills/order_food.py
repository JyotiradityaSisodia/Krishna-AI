from skills.base import BaseSkill


class OrderFoodSkill(BaseSkill):
    name = "order_food"
    required_fields = ["item_or_cuisine"]

    def run(self, params: dict, session: dict) -> dict:
        missing = self.get_missing_fields(params)

        if missing:
            return {
                "status": "need_input",
                "missing_fields": missing,
                "message": f"I need these details for food ordering: {', '.join(missing)}."
            }

        return {
            "status": "awaiting_approval",
            "summary": {
                "skill": self.name,
                "item_or_cuisine": params.get("item_or_cuisine"),
                "restaurant": params.get("restaurant", "not specified")
            },
            "message": f"I am ready to order {params.get('item_or_cuisine')} for you."
        }

    def execute(self, params: dict, session: dict) -> dict:
        from tools.zomato_orderer import prepare_zomato_order

        return prepare_zomato_order(
            item_or_cuisine=params.get("item_or_cuisine", ""),
            restaurant=params.get("restaurant", "")
        )
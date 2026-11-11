from skills.book_ride import BookRideSkill
from skills.order_food import OrderFoodSkill
from skills.book_show import BookShowSkill
from skills.call_person import CallPersonSkill
from skills.send_whatsapp import SendWhatsAppSkill


SKILL_REGISTRY = {
    "book_ride": {
        "keywords": ["book a ride", "ride", "cab", "taxi"],
        "handler": BookRideSkill(),
    },
    "order_food": {
        "keywords": ["order food", "food", "hungry", "eat"],
        "handler": OrderFoodSkill(),
    },
    "book_show": {
        "keywords": ["book show", "movie", "cinema", "show"],
        "handler": BookShowSkill(),
    },
    "call_person": {
        "keywords": ["call", "phone", "ring"],
        "handler": CallPersonSkill(),
    },
    "send_whatsapp": {
        "keywords": [
            "send whatsapp",
            "whatsapp",
            "message on whatsapp",
            "send message",
            "message mom",
            "message dad",
            "reply to mom",
            "reply to mother",
            "reply on whatsapp"
        ],
        "handler": SendWhatsAppSkill(),
    },
}
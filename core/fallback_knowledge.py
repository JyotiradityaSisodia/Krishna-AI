from __future__ import annotations

import re


KNOWLEDGE_BASE = {
    "jet engine": (
        "A jet engine is a machine that produces thrust by taking in air, compressing it, "
        "mixing it with fuel, burning that mixture, and expelling hot gases at high speed. "
        "Most modern aircraft use gas turbine jet engines. In simple terms, the engine pulls air in, "
        "raises its pressure with a compressor, burns fuel in a combustion chamber, and then drives turbines "
        "with the hot exhaust. Those turbines power the compressor, and the remaining fast-moving exhaust creates thrust."
    ),
    "jet engines": (
        "Jet engines are propulsion systems that create thrust by expelling high-speed gases. "
        "Most aircraft jet engines work by compressing incoming air, mixing it with fuel, burning it, "
        "and pushing the hot gases out the back. The main stages are intake, compression, combustion, "
        "turbine extraction, and exhaust. Turbofan engines are the most common in commercial aviation."
    ),
    "black hole": (
        "A black hole is a region of space where gravity is so strong that not even light can escape once it crosses the event horizon. "
        "Black holes usually form when very massive stars collapse at the end of their lives. They are not empty holes; "
        "they are extremely dense concentrations of mass. Scientists infer their presence by observing how nearby matter and light behave."
    ),
    "recursion": (
        "Recursion is a problem-solving technique where a function solves a problem by calling itself on a smaller version of that same problem. "
        "A recursive solution usually has two parts: a base case, which stops the recursion, and a recursive case, which reduces the problem step by step."
    ),
    "neural network": (
        "A neural network is a machine learning model inspired by layers of interconnected units. "
        "It takes inputs, transforms them through layers of weighted computations, and produces outputs. "
        "During training, the model adjusts its weights to reduce error on examples."
    ),
    "artificial intelligence": (
        "Artificial intelligence is the field of building systems that can perform tasks that normally require human intelligence, "
        "such as understanding language, recognizing patterns, making decisions, and solving problems."
    ),
    "machine learning": (
        "Machine learning is a branch of AI where systems learn patterns from data instead of being explicitly programmed for every case. "
        "The system improves its performance by training on examples."
    ),
}


def normalize_text(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s\-]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


def extract_topic(user_text: str) -> str:
    text = normalize_text(user_text)

    prefixes = [
        "tell me about ",
        "what is ",
        "whats ",
        "what are ",
        "explain ",
        "who is ",
        "define ",
    ]

    for prefix in prefixes:
        if text.startswith(prefix):
            return text[len(prefix):].strip()

    return text.strip()


def lookup_knowledge(user_text: str) -> str | None:
    topic = extract_topic(user_text)

    if topic in KNOWLEDGE_BASE:
        return KNOWLEDGE_BASE[topic]

    # soft match
    for key, value in KNOWLEDGE_BASE.items():
        if key in topic or topic in key:
            return value

    return None


def generic_explanatory_reply(user_text: str) -> str:
    topic = extract_topic(user_text)

    if not topic:
        return "Ask me anything, and I’ll do my best to explain it clearly."

    return (
        f"I can help with that. Based on your question, it sounds like you want a basic explanation of {topic}. "
        f"At a high level, {topic} is a concept that should be understood by looking at what it is, how it works, "
        f"why it matters, and where it is used. If you want, I can help refine Krishna’s built-in knowledge on this topic next."
    )
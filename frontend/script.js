const chat = document.getElementById("chat");
const input = document.getElementById("input");
const status = document.getElementById("status");

function escapeHtml(text) {
    return String(text)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
}

function renderKrishnaMarkdown(text) {
    if (!text) return "";

    let cleaned = String(text);

    // Normalize line endings
    cleaned = cleaned.replace(/\r\n/g, "\n");
    cleaned = cleaned.replace(/\r/g, "\n");
    cleaned = cleaned.replace(/\\n/g, "\n");

    // Escape first for safety
    cleaned = escapeHtml(cleaned);

    // Bold: **text**
    cleaned = cleaned.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");

    // Italic: *text*
    cleaned = cleaned.replace(/\*(.*?)\*/g, "<em>$1</em>");

    // Headings
    cleaned = cleaned.replace(/^###\s+(.*)$/gm, "<h3>$1</h3>");
    cleaned = cleaned.replace(/^####\s+(.*)$/gm, "<h4>$1</h4>");
    cleaned = cleaned.replace(/^##\s+(.*)$/gm, "<h2>$1</h2>");
    cleaned = cleaned.replace(/^#\s+(.*)$/gm, "<h1>$1</h1>");

    // Line breaks
    cleaned = cleaned.replace(/\n/g, "<br>");

    return cleaned;
}

function addMessage(text, type) {
    const div = document.createElement("div");
    div.className = "message " + type;

    if (type === "bot") {
        div.innerHTML = renderKrishnaMarkdown(text);
    } else {
        div.textContent = text;
    }

    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
}

async function sendMessage() {
    const text = input.value.trim();
    if (!text) return;

    addMessage(text, "user");
    input.value = "";
    status.innerText = "🟡 Thinking...";

    try {
        const res = await fetch("http://127.0.0.1:8000/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message: text })
        });

        const data = await res.json();

        if (!res.ok) {
            addMessage(`Backend error: ${JSON.stringify(data)}`, "bot");
        } else {
            addMessage(data.response, "bot");
        }
    } catch (err) {
        addMessage("Error connecting to Krishna.", "bot");
    }

    status.innerText = "🟢 Ready";
}

input.addEventListener("keypress", function (e) {
    if (e.key === "Enter") {
        sendMessage();
    }
});
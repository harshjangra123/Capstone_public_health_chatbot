const chat = document.getElementById("chat");
const input = document.getElementById("messageInput");
const button = document.getElementById("sendBtn");

// Generate a simple session ID for the user
const sessionId = `session_${Date.now()}`;

button.addEventListener("click", sendMessage);
input.addEventListener("keypress", function(event) {
  if (event.key === "Enter") {
    sendMessage();
  }
});

async function sendMessage() {
  const text = input.value;
  if (!text) return;

  addMessage(text, "user");
  input.value = "";

  try {
    const res = await fetch("http://localhost:8000/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text, session_id: sessionId })
    });

    if (!res.ok) {
      addMessage("Error: Could not connect to the server.", "bot");
      return;
    }

    const data = await res.json();
    addMessage(data.response, "bot");
  } catch (error) {
    addMessage("Error: An unexpected error occurred.", "bot");
  }
}

function addMessage(text, sender) {
  const wrapper = document.createElement("div");
  wrapper.className = "w-full flex " + (sender === "user" ? "justify-end" : "justify-start");

  const div = document.createElement("div");
  div.className =
    "border-2 border-black rounded-xl p-2 max-w-[70%] " +
    (sender === "user" ? "bg-blue-100" : "bg-green-100");

  div.innerText = text;

  wrapper.appendChild(div);
  chat.appendChild(wrapper);

  chat.scrollTop = chat.scrollHeight;
}
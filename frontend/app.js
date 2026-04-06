const chat = document.getElementById("chat");
const input = document.getElementById("messageInput");
const button = document.getElementById("sendBtn");

function addLoadingSpinner() {
  const wrapper = document.createElement("div");
  wrapper.className = "w-full flex justify-start";

  const div = document.createElement("div");
  div.className =
    "border-2 border-black rounded-xl p-3 max-w-[70%] bg-green-100 flex items-center justify-center";

  const spinner = document.createElement("div");
  spinner.className = "spinner";

  div.appendChild(spinner);
  wrapper.appendChild(div);
  chat.appendChild(wrapper);
  chat.scrollTop = chat.scrollHeight;

  return wrapper;
}

// Safe markdown renderer — never throws, always falls back to plain text
function renderMarkdown(text) {
  try {
    // Strip any raw tool result prefixes the LLM may have leaked into its response
    text = text
      .replace(/^DATASET_RESULT:\s*/i, "")
      .replace(/^NO_DATA_FOUND\s*/i, "")
      .replace(/^INSUFFICIENT_DATA\s*/i, "");

    let html = text
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");

    // LaTeX block math \[ ... \] → show as plain monospace
    html = html.replace(/\\\[[\s\S]*?\\\]/g, (match) => {
      const inner = match.slice(2, -2).trim();
      return `<div class="my-1 text-sm text-gray-700 font-mono">${inner}</div>`;
    });

    // LaTeX inline \( ... \)
    html = html.replace(/\\\([\s\S]*?\\\)/g, (match) => {
      return `<span class="font-mono text-sm">${match.slice(2, -2).trim()}</span>`;
    });

    // Headers
    html = html.replace(/^### (.+)$/gm, '<h3 class="font-bold text-base mt-2 mb-1">$1</h3>');
    html = html.replace(/^## (.+)$/gm,  '<h2 class="font-bold text-lg mt-2 mb-1">$1</h2>');
    html = html.replace(/^# (.+)$/gm,   '<h1 class="font-bold text-xl mt-2 mb-1">$1</h1>');

    // Horizontal rule
    html = html.replace(/^---$/gm, '<hr class="my-2 border-gray-400">');

    // Bold and italic
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');

    // Inline code
    html = html.replace(/`(.+?)`/g, '<code class="bg-gray-100 px-1 rounded text-sm font-mono">$1</code>');

    // Tables — STRICT validation: must have a separator row (---|---) to be a real table
    const lines = html.split('\n');
    const outputLines = [];
    let i = 0;
    while (i < lines.length) {
      const line = lines[i];
      // Only treat as a table if the NEXT line is a proper separator row (e.g. |---|---|)
      const isTableRow = /^\|.+\|$/.test(line.trim());
      const nextLine = lines[i + 1] ? lines[i + 1].trim() : "";
      const isSeparatorNext = /^\|[\s\-|:]+\|$/.test(nextLine);

      if (isTableRow && isSeparatorNext) {
        // Confirmed markdown table — collect all rows
        const tableLines = [];
        while (i < lines.length && /^\|.+\|$/.test(lines[i].trim())) {
          tableLines.push(lines[i].trim());
          i++;
        }
        if (tableLines.length >= 2) {
          const headerCells = tableLines[0].split('|').slice(1, -1);
          const bodyRows = tableLines.slice(2); // skip separator row
          const thead = `<thead><tr>${headerCells.map(c =>
            `<th class="border border-gray-400 px-2 py-1 bg-gray-100 font-semibold text-left text-sm">${c.trim()}</th>`
          ).join('')}</tr></thead>`;
          const tbody = `<tbody>${bodyRows.map(row => {
            const cells = row.split('|').slice(1, -1);
            return `<tr>${cells.map(c =>
              `<td class="border border-gray-400 px-2 py-1 text-sm">${c.trim()}</td>`
            ).join('')}</tr>`;
          }).join('')}</tbody>`;
          outputLines.push(`<div class="overflow-x-auto my-2"><table class="border-collapse border border-gray-400 w-full">${thead}${tbody}</table></div>`);
        }
      } else {
        outputLines.push(line);
        i++;
      }
    }
    html = outputLines.join('\n');

    // Bullet lists
    html = html.replace(/^[-•] (.+)$/gm, '<li class="ml-4 list-disc text-sm">$1</li>');
    html = html.replace(/(<li[^>]*>.*<\/li>\n?)+/g, m => `<ul class="my-1 pl-2">${m}</ul>`);

    // Numbered lists
    html = html.replace(/^\d+\. (.+)$/gm, '<li class="ml-4 list-decimal text-sm">$1</li>');

    // Line breaks
    html = html.replace(/\n\n/g, '<br><br>');
    html = html.replace(/\n/g, '<br>');

    return html;

  } catch (err) {
    console.error("Markdown render error:", err);
    return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }
}

const sessionId = `session_${Date.now()}`;

button.addEventListener("click", sendMessage);
input.addEventListener("keypress", function (event) {
  if (event.key === "Enter") sendMessage();
});

async function sendMessage() {
  const text = input.value.trim();
  if (!text) return;

  addMessage(text, "user");
  input.value = "";

  const loadingMsg = addLoadingSpinner();

  try {
    const res = await fetch("http://localhost:8000/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text, session_id: sessionId })
    });

    removeMessage(loadingMsg);

    if (!res.ok) {
      addMessage("Error: Could not connect to the server.", "bot");
      return;
    }

    const data = await res.json();

    if (!data.response || data.response.trim() === "") {
      addMessage("Sorry, I could not generate a response. Please try again.", "bot");
    } else {
      addMessage(data.response, "bot");
    }

  } catch (error) {
    removeMessage(loadingMsg);
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

  if (sender === "bot") {
    try {
      div.innerHTML = renderMarkdown(text);
    } catch (err) {
      div.innerText = text;
    }
  } else {
    div.innerText = text;
  }

  wrapper.appendChild(div);
  chat.appendChild(wrapper);
  chat.scrollTop = chat.scrollHeight;

  return wrapper;
}

function removeMessage(element) {
  if (element && element.parentNode === chat) {
    chat.removeChild(element);
  }
}
import { useEffect, useState } from "react";

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8100";

export default function App() {
  const [items, setItems] = useState([]);
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);

  async function refresh() {
    const response = await fetch(`${apiBaseUrl}/items`);
    setItems(await response.json());
  }

  useEffect(() => {
    refresh();
  }, []);

  async function addItem(event) {
    event.preventDefault();
    const trimmed = text.trim();
    if (!trimmed) {
      return;
    }
    setBusy(true);
    try {
      await fetch(`${apiBaseUrl}/items`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: trimmed }),
      });
      setText("");
      await refresh();
    } finally {
      setBusy(false);
    }
  }

  return (
    <main>
      <h1>Sample App</h1>
      <form onSubmit={addItem}>
        <label htmlFor="new-item">New item</label>
        <input
          id="new-item"
          data-testid="new-item-input"
          value={text}
          disabled={busy}
          onChange={(event) => setText(event.target.value)}
        />
        <button type="submit" disabled={busy}>
          Add
        </button>
      </form>
      <ul aria-label="Items" data-testid="item-list">
        {items.map((item) => (
          <li key={item.id}>{item.name}</li>
        ))}
      </ul>
    </main>
  );
}

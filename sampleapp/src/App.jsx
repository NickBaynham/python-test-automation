import { useState } from "react";

export default function App() {
  const [items, setItems] = useState([]);
  const [text, setText] = useState("");

  function addItem(event) {
    event.preventDefault();
    const trimmed = text.trim();
    if (!trimmed) {
      return;
    }
    setItems([...items, trimmed]);
    setText("");
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
          onChange={(event) => setText(event.target.value)}
        />
        <button type="submit">Add</button>
      </form>
      <ul aria-label="Items" data-testid="item-list">
        {items.map((item, index) => (
          <li key={index}>{item}</li>
        ))}
      </ul>
    </main>
  );
}

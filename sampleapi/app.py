"""Sample REST API: an in-memory items service for platform integration tests.

Storage is a module-level dict for now; Phase 3 replaces it with MongoDB
so the full-stack scenario can verify database state.
"""

from itertools import count

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI(title="Sample API")

_items: dict[int, "Item"] = {}
_ids = count(1)


class ItemIn(BaseModel):
    name: str = Field(min_length=1)


class Item(ItemIn):
    id: int


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/items")
def list_items() -> list[Item]:
    return list(_items.values())


@app.post("/items", status_code=status.HTTP_201_CREATED)
def create_item(payload: ItemIn) -> Item:
    item = Item(id=next(_ids), name=payload.name)
    _items[item.id] = item
    return item


@app.get("/items/{item_id}")
def get_item(item_id: int) -> Item:
    if item_id not in _items:
        raise HTTPException(status_code=404, detail="item not found")
    return _items[item_id]


@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int) -> None:
    if item_id not in _items:
        raise HTTPException(status_code=404, detail="item not found")
    del _items[item_id]

"""Sample REST API: a MongoDB-backed items service for platform testing.

Storage lives in the `items` collection so the platform's full-stack
scenario can verify database state behind API effects.
"""

import os
from typing import Any

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pymongo import MongoClient

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27100")
MONGO_DATABASE = os.environ.get("MONGO_DATABASE", "sampledb")

client: MongoClient[dict[str, Any]] = MongoClient(MONGO_URL)
items = client[MONGO_DATABASE]["items"]

app = FastAPI(title="Sample API")

# Test fixture: the browser-served sample app calls this API cross-origin.
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"])


class ItemIn(BaseModel):
    name: str = Field(min_length=1)


class Item(ItemIn):
    id: str


def _object_id(item_id: str) -> ObjectId:
    try:
        return ObjectId(item_id)
    except InvalidId:
        raise HTTPException(status_code=404, detail="item not found") from None


def _to_item(document: dict[str, Any]) -> Item:
    return Item(id=str(document["_id"]), name=document["name"])


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/items")
def list_items() -> list[Item]:
    return [_to_item(document) for document in items.find()]


@app.post("/items", status_code=status.HTTP_201_CREATED)
def create_item(payload: ItemIn) -> Item:
    result = items.insert_one({"name": payload.name})
    return Item(id=str(result.inserted_id), name=payload.name)


@app.get("/items/{item_id}")
def get_item(item_id: str) -> Item:
    document = items.find_one({"_id": _object_id(item_id)})
    if document is None:
        raise HTTPException(status_code=404, detail="item not found")
    return _to_item(document)


@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: str) -> None:
    result = items.delete_one({"_id": _object_id(item_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="item not found")

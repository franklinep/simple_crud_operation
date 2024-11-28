from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from pymongo import ReturnDocument
from dotenv import dotenv_values

from serializer import convert_doc, convert_doc_list

config = dotenv_values(".env")

client = AsyncIOMotorClient(config["ATLAS_URI"])
app = FastAPI()

database = client.get_database("learningbyte")
collection = database.get_collection("items")

class Item(BaseModel):
    name: str
    age: int

@app.get("/")
async def root():
    collections = await client.list_database_names()
    return {
        "message": "Connected to MongoDB Atlas",
        "collections": collections,
    }

# CREATE 
@app.post("/items/")
async def create_item(item: Item):
    await collection.insert_one(item.model_dump()) # model->dict
    return {"message": "Item created", "item": item}

# READ 
@app.get("/items/")
async def read_items():
    items = await collection.find().to_list(length=10)
    return {"items": convert_doc_list(items)}

# UPDATE 
@app.put("/items/{name}")
async def update_item(name: str, item: Item):
    updated_item = await collection.find_one_and_update(
        {"name": name}, # filtro
        {"$set": item.model_dump()}, # actualizacion
        return_document=ReturnDocument.AFTER,
    )
    if updated_item:
        return{"message": "Item Updated", "item": convert_doc(updated_item)}
    else:
        raise HTTPException(status_code=404, detail=f"The item {name} was not found")
    
# DELETE 
@app.delete("/items/{name}")
async def delete_item(name: str):
    #deleted_item = await collection.find_one_and_delete({"name": name})
    deleted_item = await collection.delete_one({"name": name})

    if deleted_item.deleted_count:
        return {"message":f"Item with name {name} deleted"}
    else:
        raise HTTPException(status_code=404, detail=f"Item with name {name} not found")

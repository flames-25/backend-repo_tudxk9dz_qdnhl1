import os
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from database import create_document, get_documents, db

app = FastAPI(title="Travel Explorer API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SearchQuery(BaseModel):
    type: str = Field(..., description="flights | hotels | trains")
    origin: Optional[str] = Field(None, description="Origin city/airport/station")
    destination: Optional[str] = Field(None, description="Destination city/airport/station")
    date: Optional[str] = Field(None, description="YYYY-MM-DD for flights/trains")
    city: Optional[str] = Field(None, description="City for hotels")
    checkin: Optional[str] = Field(None, description="YYYY-MM-DD for hotels check-in")
    checkout: Optional[str] = Field(None, description="YYYY-MM-DD for hotels check-out")


class FlightOption(BaseModel):
    airline: str
    flight_number: str
    depart_time: str
    arrive_time: str
    duration: str
    price: float
    origin: str
    destination: str


class HotelOption(BaseModel):
    name: str
    location: str
    rating: float
    price_per_night: float
    image: Optional[str] = None


class TrainOption(BaseModel):
    train_name: str
    train_number: str
    depart_time: str
    arrive_time: str
    duration: str
    price: float
    origin: str
    destination: str


@app.get("/")
def read_root():
    return {"message": "Travel Explorer Backend is running"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the Travel Explorer API!"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": [],
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, "name") else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


@app.post("/api/search", response_model=dict)
def create_search(search: SearchQuery):
    try:
        doc_id = create_document("search", search)
        return {"status": "ok", "id": doc_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/searches")
def list_recent_searches(limit: int = Query(10, ge=1, le=50)):
    try:
        docs = get_documents("search", {}, limit=limit)
        # Convert ObjectId to str if present
        for d in docs:
            if "_id" in d:
                d["_id"] = str(d["_id"])
            if "created_at" in d and hasattr(d["created_at"], "isoformat"):
                d["created_at"] = d["created_at"].isoformat()
        # Sort by created_at desc if exists
        docs.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return {"items": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/search/flights", response_model=List[FlightOption])
def search_flights(origin: str, destination: str, date: str):
    # Mock results similar to aggregator style
    base_price = 79.0
    flights = [
        {
            "airline": "SkyJet",
            "flight_number": "SJ201",
            "depart_time": f"{date}T06:30",
            "arrive_time": f"{date}T09:05",
            "duration": "2h 35m",
            "price": base_price + 20,
            "origin": origin.upper(),
            "destination": destination.upper(),
        },
        {
            "airline": "AeroWings",
            "flight_number": "AW318",
            "depart_time": f"{date}T10:15",
            "arrive_time": f"{date}T12:55",
            "duration": "2h 40m",
            "price": base_price + 35,
            "origin": origin.upper(),
            "destination": destination.upper(),
        },
        {
            "airline": "CloudAir",
            "flight_number": "CA722",
            "depart_time": f"{date}T19:45",
            "arrive_time": f"{date}T22:25",
            "duration": "2h 40m",
            "price": base_price + 10,
            "origin": origin.upper(),
            "destination": destination.upper(),
        },
    ]
    # Save search for recents
    try:
        create_document(
            "search",
            {
                "type": "flights",
                "origin": origin,
                "destination": destination,
                "date": date,
            },
        )
    except Exception:
        pass
    return [FlightOption(**f) for f in flights]


@app.get("/api/search/hotels", response_model=List[HotelOption])
def search_hotels(city: str, checkin: str, checkout: str):
    hotels = [
        {
            "name": "Grand Central Hotel",
            "location": city.title(),
            "rating": 4.5,
            "price_per_night": 129.0,
            "image": "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?q=80&w=1200&auto=format&fit=crop",
        },
        {
            "name": "Urban Stay Boutique",
            "location": city.title(),
            "rating": 4.2,
            "price_per_night": 99.0,
            "image": "https://images.unsplash.com/photo-1496412705862-e0088f16f791?q=80&w=1200&auto=format&fit=crop",
        },
        {
            "name": "Skyline Suites",
            "location": city.title(),
            "rating": 4.8,
            "price_per_night": 189.0,
            "image": "https://images.unsplash.com/photo-1502920917128-1aa500764cbd?q=80&w=1200&auto=format&fit=crop",
        },
    ]
    try:
        create_document(
            "search",
            {"type": "hotels", "city": city, "checkin": checkin, "checkout": checkout},
        )
    except Exception:
        pass
    return [HotelOption(**h) for h in hotels]


@app.get("/api/search/trains", response_model=List[TrainOption])
def search_trains(origin: str, destination: str, date: str):
    trains = [
        {
            "train_name": "Express Line",
            "train_number": "EX123",
            "depart_time": f"{date}T07:10",
            "arrive_time": f"{date}T13:30",
            "duration": "6h 20m",
            "price": 24.0,
            "origin": origin.upper(),
            "destination": destination.upper(),
        },
        {
            "train_name": "Rapid Rider",
            "train_number": "RR452",
            "depart_time": f"{date}T15:00",
            "arrive_time": f"{date}T21:10",
            "duration": "6h 10m",
            "price": 27.5,
            "origin": origin.upper(),
            "destination": destination.upper(),
        },
    ]
    try:
        create_document(
            "search",
            {
                "type": "trains",
                "origin": origin,
                "destination": destination,
                "date": date,
            },
        )
    except Exception:
        pass
    return [TrainOption(**t) for t in trains]


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

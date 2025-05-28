from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import pandas as pd
from surprise import SVD
import joblib
import duckdb
from fastapi.middleware.cors import CORSMiddleware

# Load trained model once
model = joblib.load('trained_svd_model.pkl')

# Load product IDs once
conn = duckdb.connect()
reviews = '../../data/parquet_files/reviews.parquet'
review_df = conn.execute(
    f"SELECT author_id, product_id, rating FROM '{reviews}'"
).fetchdf()
all_product_ids = review_df['product_id'].unique()

# FastAPI setup
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request schemas
class RatingInput(BaseModel):
    product_id: str
    rating: int

class RecommendationRequest(BaseModel):
    user_id: str
    ratings: List[RatingInput]

# Endpoint
@app.post("/recommend")
def recommend_products(user_data: RecommendationRequest):
    try:
        # Products the user already rated
        rated_products = set(item.product_id for item in user_data.ratings)
        unseen_products = [pid for pid in all_product_ids if pid not in rated_products]

        print("Knows user? : ", model.trainset.knows_user(user_data.user_id))


        # Predict ratings for unseen products
        predictions = [model.predict(user_data.user_id, pid) for pid in unseen_products]
        predictions.sort(key=lambda x: x.est, reverse=True)

        # Return top 3
        top_recommendations = [
            {"product_id": pred.iid, "predicted_rating": round(pred.est, 2)}
            for pred in predictions[:3]
        ]

        return {"recommendations": top_recommendations}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
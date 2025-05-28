from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import pandas as pd
from surprise import SVD, Dataset, Reader
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import duckdb
import joblib
from surprise import SVD
import json
from fastapi.responses import JSONResponse


conn = duckdb.connect()

# --- Your real dataset should be loaded here ---
# For example purposes, we're initializing an empty DataFrame
reviews = '../../../data/parquet_files/reviews.parquet'
review_df = conn.execute(
    f'''
    SELECT * FROM '{reviews}'
    '''
)
review_df = pd.DataFrame(columns=["author_id", "product_id", "rating"])

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # Vue dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dummy review data (Replace this with your actual dataset)
review_df = pd.DataFrame(columns=["author_id", "product_id", "rating"])

class RatingInput(BaseModel):
    product_id: str
    rating: int

class RecommendationRequest(BaseModel):
    user_id: str
    ratings: List[RatingInput]

@app.post("/recommend")
def recommend_products(user_data: RecommendationRequest):
    try:
        print("User Data:", user_data)

        conn = duckdb.connect()

        reviews = '../../../data/parquet_files/reviews.parquet'
        review_df = conn.execute(
            f'''
            SELECT author_id, product_id, rating FROM '{reviews}'
            '''
        ).fetchdf()

        product_data = '../../../data/parquet_files/products_data.parquet'
        product_df = conn.execute(
            f'''
            SELECT product_id, brand_name, product_name FROM '{product_data}'
            '''
        ).fetchdf()

        new_ratings = [
            (user_data.user_id, item.product_id, item.rating)  # Access product_id and rating directly
            for item in user_data.ratings
        ]
        
        # Convert to DataFrame
        new_ratings_df = pd.DataFrame(new_ratings, columns=["author_id", "product_id", "rating"])

        print(new_ratings_df)

        # Combine with full review dataset
        full_df = pd.concat([review_df, new_ratings_df], ignore_index=True)

        # Build and train recommendation model
        # reader = Reader(rating_scale=(1, 5))
        # data = Dataset.load_from_df(full_df[['author_id', 'product_id', 'rating']], reader)
        # train_set = data.build_full_trainset()

        # model = SVD()
        # model.fit(train_set)
        # Load model on startup
        model = joblib.load("../models/svd_model.pkl")    

        # Get all product IDs
        all_product_ids = full_df['product_id'].unique()
        rated_products = set(item.product_id for item in user_data.ratings)  # Access product_id directly
        unseen_products = [pid for pid in all_product_ids if pid not in rated_products]

        # Make predictions
        predictions = [model.predict(user_data.user_id, pid) for pid in unseen_products]
        predictions.sort(key=lambda x: x.est, reverse=True)

# Return top 3 recommended products
        top_recommendations = []
        for pred in predictions[:3]:
            product_info = product_df[product_df['product_id'] == pred.iid].iloc[0]
            top_recommendations.append({
                "brand_name": product_info["brand_name"],
                "product_name": product_info["product_name"],
                "product_id": pred.iid,
                "predicted_rating": round(pred.est, 2)
            })

        print("top recs:", top_recommendations)

        return {"recommendations": top_recommendations}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/get-products")
async def get_products():
    try:
        with open("product_names.json", "r") as file:
            data = json.load(file)
        return JSONResponse(content=data)
    except Exception as e:
        return {"error": str(e)}
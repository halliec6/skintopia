import joblib
import numpy as np
from pydantic import BaseModel
from typing import List
import duckdb 
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
from fastapi.responses import JSONResponse
from collections import defaultdict
# Function to generate product recommendations
import numpy as np
from scipy.sparse import csr_matrix

from typing import List
import duckdb

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Vue dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RatingInput(BaseModel):
    product_id: str
    rating: int

class RatingInputWithName(BaseModel):
    product_name: str
    rating: int

class RecommendationRequest(BaseModel):
    user_id: str
    ratings: List[RatingInputWithName]
    skin_tone: str  
    skin_type: str 
    product_category: List[str] 

def map_product_name_to_ID(original_ratings: List[RatingInputWithName]):
    conn = duckdb.connect() 
    product_data = '../../../data/parquet_files/products_data.parquet' 

    return_ids = []
    for rating in original_ratings:
        query = f"""
            SELECT product_id
            FROM '{product_data}'
            WHERE product_name = '{rating.product_name}'
        """
        result_df = conn.execute(query).df()
        if not result_df.empty:
            product_id = result_df.loc[0, 'product_id']
            return_ids.append({
                "product_id": product_id,
                "rating": rating.rating
            })
        else:
            return_ids.append({
                "product_id": None,
                "rating": rating.rating
            })

    return return_ids


@app.post("/recommend_lightfm")
def recommend_products_from_request(request: RecommendationRequest, N=5):
    """
    Recommend products based on user ratings, skin tone, and skin type.
    
    Args:
    - request (RecommendationRequest): The user request object containing user ID, ratings, skin tone, and skin type.
    - model: The trained LightFM model.
    - dataset: The LightFM Dataset object.
    - N (int): The number of recommendations to return.

    Returns:
    - recommendations (list): A list of product IDs recommended to the user.
    """
    try: 
        conn = duckdb.connect()

        # Load the trained model from a file
        model = joblib.load('../models/lightfm_model.pkl')

        # Load the dataset object (contains the mappings) from a file
        dataset = joblib.load('../models/lightfm_dataset.pkl')

        product_data = '../../../data/parquet_files/products_data.parquet'

        _, _, item_id_map, _ = dataset.mapping()
        index_to_item_id = {v: k for k, v in item_id_map.items()}

        print("STARTING")
        print("REQUEST: ", request)

        user_id = request.user_id
        original_ratings = request.ratings  # List of RatingInput objects
        skin_tone = request.skin_tone
        skin_type = request.skin_type

        print("\nORIGINAL RATINGS:", original_ratings)
        ratings = map_product_name_to_ID(original_ratings)
        print("past map")

        print("\nRATINGS AFTER MAP: ", ratings)
        # Check if the user has provided ratings (existing user or cold start)
        known_product_ids = [rating["product_id"] for rating in ratings]

        # Get the internal index of the user
        user_index = dataset._user_id_mapping.get(user_id, None)
        print(f"User Index for user_id {user_id}: {user_index}")
 
        user_features = []
        
        # Check if skin_tone exists in user feature mapping
        if skin_tone and skin_tone in dataset._user_feature_mapping:
            user_features.append(dataset._user_feature_mapping[skin_tone])
        else:
            print(f"Skin tone '{skin_tone}' not found in user features!")

        # Check if skin_type exists in user feature mapping
        if skin_type and skin_type in dataset._user_feature_mapping:
            user_features.append(dataset._user_feature_mapping[skin_type])
        else:
            print(f"Skin type '{skin_type}' not found in user features!")

        # Convert user_features list to a sparse matrix (CSR format)
        if user_features:
            user_features_sparse = csr_matrix(([1] * len(user_features), (np.zeros(len(user_features)), user_features)), shape=(1, len(dataset._user_feature_mapping)))

            # Generate predictions for all items (products)
            n_items = len(dataset._item_id_mapping)  # Total number of products in the dataset
            scores = model.predict(0, np.arange(n_items), user_features=user_features_sparse)  # Use user index 0 for cold start
        else:
            print("No valid user features found!")
            return []

        top_items = np.argsort(-scores)

        # Filter out products the user has already reviewed (exclude known product IDs)
        recommended_ids = [
            index_to_item_id.get(i)
            for i in top_items
            if index_to_item_id.get(i) not in known_product_ids
        ]
        print(recommended_ids[:N])

        if recommended_ids:
            placeholders = ",".join([f"'{pid}'" for pid in recommended_ids[:50]])
   
            query = f"""
                SELECT * FROM '{product_data}'
                WHERE product_id IN ({placeholders})
            """
            enriched_recommendations = conn.execute(query).df()
            
            # Ensure DataFrame is serializable
            enriched_recommendations = enriched_recommendations.to_dict(orient='records')
            
            # Convert numpy.int64 to native int for all dictionary values
            enriched_recommendations = [
                {k: (int(v) if isinstance(v, np.int64) else v) for k, v in rec.items()}
                for rec in enriched_recommendations
            ]
        else:
            print("No recommendations.")

        category_to_products = defaultdict(list)
        for rec in enriched_recommendations:
            if rec["category"] in request.product_category:
                category_to_products[rec["category"]].append(rec)

        num_categories = len(category_to_products)
        products_per_category = 1 if num_categories >= 3 else 2

        # Select the top products per category
        final_recommendations = []
        for category, products in category_to_products.items():
            # Assuming enriched_recommendations is already in order of best predictions
            final_recommendations.extend(products[:products_per_category])

        # Limit total recommendations to N if necessary
        final_recommendations = final_recommendations[:N]

        for rec in final_recommendations:
            print("FILTERED PRODUCT:", rec["product_name"], rec["product_id"])

        print("LENGTH OF FILTERED PRODUCTS:", len(final_recommendations))

        return final_recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.get("/get-products")
async def get_products():
    try:
        with open("../products.json", "r") as file:
            data = json.load(file)
        
        # Concatenate brand and product name
        product_names = [
            f"{item['brand_name']} - {item['product_name']}"
            for item in data
        ]
        return JSONResponse(content={"product_names": product_names})
    
    except Exception as e:
        return {"error": str(e)}

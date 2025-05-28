from surprise import SVD, Dataset, Reader
import pandas as pd
import joblib
import duckdb

# Load data
conn = duckdb.connect()
reviews = '../../data/parquet_files/reviews.parquet'
review_df = conn.execute(
    f'''
    SELECT author_id, product_id, rating FROM '{reviews}'
    '''
).fetchdf()

# Train model
reader = Reader(rating_scale=(1, 5))
data = Dataset.load_from_df(review_df[['author_id', 'product_id', 'rating']], reader)
trainset = data.build_full_trainset()

model = SVD()
model.fit(trainset)

# Save model
joblib.dump(model, 'svd_model.pkl')


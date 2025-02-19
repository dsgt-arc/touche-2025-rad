from ingestion_pipeline.ingest import DebateIngestionPipeline

# Initialize pipeline with PostgreSQL connection
pipeline = DebateIngestionPipeline()

# 1. Basic ingestion with automatic chunking and stats
# Step 1: Generate and save embeddings to PostgreSQL
pipeline.ingest_csv("../data/data.csv", debug=False)

# # 2. Only analyze data without ingesting
# pipeline.ingest_csv(
#     "data.csv",
#     analyze_only=True
# )  # Show stats for each topic and exit

# # 3. Skip statistics and directly ingest
# pipeline.ingest_csv(
#     "data.csv",
#     skip_stats=True
# )  # Process and ingest data without stats

# # 4. With specific embedding model
# pipeline_mpnet = DebateIngestionPipeline(
#     embedding_model="all-mpnet-base-v2",
#     max_tokens=384  # Adjust token limit for model
# )

# # 5. Quick analysis of multiple datasets
# for dataset in ["train.csv", "test.csv", "val.csv"]:
#     print(f"\nAnalyzing {dataset}:")
#     pipeline.ingest_csv(dataset, analyze_only=True)

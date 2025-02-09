from ingestion_pipeline.ingest import DebateIngestionPipeline

# Initialize pipeline
pipeline = DebateIngestionPipeline()

# 1. basic ingestion with automatic chunking and stats
# Step 1: Generate and save embeddings to parquet
pipeline.ingest_csv("../data/data.csv", debug=False)
# Step 2: Load embeddings from parquet into ChromaDB
pipeline.load_embeddings_to_chroma("../embedded_data")

# # 2. only analyze data without ingesting
# pipeline.ingest_csv(
#     "data.csv",
#     analyze_only=True
# )  # show stats for each topic and exit

# # 3. skip statistics and directly ingest
# pipeline.ingest_csv(
#     "data.csv",
#     skip_stats=True
# )  # process and ingest data without stats

# # 4. with specific embedding model
# pipeline_mpnet = DebateIngestionPipeline(
#     embedding_model="all-mpnet-base-v2",
#     max_tokens=384  # adjust token limit for model
# )

# # using custom ChromaDB path and collection
# pipeline_custom = DebateIngestionPipeline(
#     chroma_path="../my_embeddings",
#     collection_name="my_debate_collection"
# )

# # 5. Quick analysis of multiple datasets
# for dataset in ["train.csv", "test.csv", "val.csv"]:
#     print(f"\nAnalyzing {dataset}:")
#     pipeline.ingest_csv(dataset, analyze_only=True)

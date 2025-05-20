import streamlit as st
from touche_rad.elasticsearch_test.function import (
    search_by_text,
    search_by_support,
    search_by_attack,
    search_all,
)

st.title("Elasticsearch Retrieval Test Interface")
st.markdown(
    """
    This interface allows you to test different types of argument retrieval from the Elasticsearch index.
    You can search for arguments based on:
    - Text similarity
    - Supporting arguments
    - Attacking arguments
    - Or all of the above combined
    """
)

# Search parameters
col1, col2 = st.columns(2)
with col1:
    k = st.number_input(
        "Number of results to return (k)", min_value=1, max_value=50, value=10
    )
with col2:
    num_candidates = st.number_input(
        "Number of candidates to consider", min_value=10, max_value=1000, value=100
    )

# Search type selection
search_type = st.radio(
    "Select search type",
    ["Text Similarity", "Supporting Arguments", "Attacking Arguments", "All Types"],
    horizontal=True,
)

# Query input
query = st.text_area("Enter your query", height=100)

if st.button("Search"):
    if not query:
        st.warning("Please enter a query")
    else:
        with st.spinner("Searching..."):
            print("searching print to console")
            try:
                if search_type == "Text Similarity":
                    results = search_by_text(query, k=k, num_candidates=num_candidates)
                    st.subheader("Text Similarity Results")
                elif search_type == "Supporting Arguments":
                    results = search_by_support(
                        query, k=k, num_candidates=num_candidates
                    )
                    st.subheader("Supporting Arguments")
                elif search_type == "Attacking Arguments":
                    results = search_by_attack(
                        query, k=k, num_candidates=num_candidates
                    )
                    st.subheader("Attacking Arguments")
                else:  # All Types
                    results = search_all(query, k=k, num_candidates=num_candidates)
                    st.subheader("All Results")

                # Display results
                if search_type == "All Types":
                    for category, category_results in results.items():
                        st.markdown(f"### {category.replace('_', ' ').title()}")
                        for i, hit in enumerate(category_results, 1):
                            with st.expander(
                                f"Result {i} (Score: {hit.get('_score', 'N/A'):.4f})"
                            ):
                                st.json(hit["_source"])
                else:
                    for i, hit in enumerate(results, 1):
                        with st.expander(
                            f"Result {i} (Score: {hit.get('_score', 'N/A'):.4f})"
                        ):
                            st.json(hit["_source"])

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

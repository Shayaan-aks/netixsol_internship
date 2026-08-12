# Justification for Structured vs. Semantic Retrieval

## 1. Why Separate the Retrieval Mechanisms?

In a production real estate AI agent, data exists in two fundamentally different forms: **Structured** and **Unstructured**.

### Structured Retrieval (SQL)
- **Use Case:** Exact matches, aggregations, and filtering.
- **Data Types:** Property prices, availability status, number of bedrooms, agent names, and sizes.
- **Justification:** If a user asks "Show me properties under 5 Crore in Islamabad", a Vector DB using semantic search might return properties that *mention* 5 Crore or Islamabad but don't strictly adhere to the numerical constraints. SQL guarantees precise, deterministic filtering (`WHERE price < 50000000 AND city = 'Islamabad'`). 

### Semantic Retrieval (Vector DB)
- **Use Case:** Conceptual queries, fuzzy matching, and long-form information extraction.
- **Data Types:** Brochures, FAQs, payment plan policies, project overviews.
- **Justification:** If a user asks "How do I pay if I live in Dubai?", a SQL database cannot easily map "Dubai" to "Overseas Pakistani Payment Plan". A Vector DB (like ChromaDB) captures the semantic meaning of the query and retrieves the relevant policy document based on embedding cosine similarity.

## 2. LLM Router
To make the experience seamless, the `rag_pipeline.py` implements an **LLM Router**. This router analyzes the incoming user query and decides whether to send it to the `create_sql_agent` or the Vector-based `create_retrieval_chain`. This ensures the best of both worlds.

## 3. Chunk Size Evaluation for Vector Retrieval
When implementing the RAG pipeline, choosing the right chunk size is critical for minimizing hallucinations and maximizing relevance:
- **Chunk Size = 1000 characters:** Often pulls in too much surrounding context (e.g., mixing payment plans with project amenities), confusing the LLM and causing it to merge unrelated facts.
- **Chunk Size = 500 characters (Chosen):** FAQs and policy rules in real estate are generally short paragraphs. A chunk size of 500 (with an overlap of 50) cleanly isolates specific answers (e.g., Transfer Fee Policy) without bleeding into the next policy, resulting in a higher Grounding Rate.

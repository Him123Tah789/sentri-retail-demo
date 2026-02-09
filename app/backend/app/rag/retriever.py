"""
RAG Retriever - Main Interface
Retrieval Augmented Generation for knowledge base search.

Combines:
- Document ingestion
- Embedding generation
- Vector search
- Context building for LLM
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from .embeddings import EmbeddingEngine, embedding_engine
from .vector_store import VectorStore, vector_store, SearchResult


@dataclass
class RetrievalContext:
    """Context retrieved for RAG."""
    documents: List[str]
    scores: List[float]
    prompt_addition: str
    metadata: Dict[str, Any]


class RAGRetriever:
    """
    RAG Retriever - Knowledge Base Search.
    
    Usage:
        retriever = RAGRetriever()
        
        # Add documents
        await retriever.add_document("Phishing is a type of cyber attack...")
        await retriever.add_document("Strong passwords should be...")
        
        # Search and get context
        context = await retriever.retrieve("How do I detect phishing?")
        
        # Use context.prompt_addition in LLM prompt
    """
    
    def __init__(
        self, 
        embedder: Optional[EmbeddingEngine] = None,
        store: Optional[VectorStore] = None
    ):
        """
        Initialize RAG Retriever.
        
        Args:
            embedder: Embedding engine (default: global instance)
            store: Vector store (default: global instance)
        """
        self.embedder = embedder or embedding_engine
        self.store = store or vector_store
    
    async def add_document(
        self, 
        content: str, 
        metadata: Optional[Dict[str, Any]] = None,
        doc_id: Optional[str] = None
    ) -> str:
        """
        Add document to knowledge base.
        
        Args:
            content: Document text
            metadata: Optional metadata (source, category, etc.)
            doc_id: Optional custom ID
        
        Returns:
            Document ID
        """
        embedding = await self.embedder.embed(content)
        return await self.store.add(content, embedding, metadata, doc_id)
    
    async def add_documents(
        self, 
        documents: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Add multiple documents.
        
        Args:
            documents: List of dicts with 'content' and optional 'metadata'
        
        Returns:
            List of document IDs
        """
        ids = []
        for doc in documents:
            doc_id = await self.add_document(
                content=doc["content"],
                metadata=doc.get("metadata"),
                doc_id=doc.get("id")
            )
            ids.append(doc_id)
        return ids
    
    async def retrieve(
        self, 
        query: str, 
        top_k: int = 3,
        min_score: float = 0.5
    ) -> RetrievalContext:
        """
        Retrieve relevant documents for query.
        
        Args:
            query: User's question
            top_k: Max documents to retrieve
            min_score: Minimum similarity score
        
        Returns:
            RetrievalContext with documents and prompt addition
        """
        # Embed query
        query_embedding = await self.embedder.embed(query)
        
        # Search
        results = await self.store.search(query_embedding, top_k)
        
        # Filter by minimum score
        results = [r for r in results if r.score >= min_score]
        
        # Build context
        documents = [r.document.content for r in results]
        scores = [r.score for r in results]
        
        # Build prompt addition
        prompt_addition = self._build_prompt(documents, query)
        
        return RetrievalContext(
            documents=documents,
            scores=scores,
            prompt_addition=prompt_addition,
            metadata={
                "query": query,
                "num_results": len(results),
                "top_score": max(scores) if scores else 0.0
            }
        )
    
    def _build_prompt(self, documents: List[str], query: str) -> str:
        """Build prompt addition from retrieved documents."""
        if not documents:
            return ""
        
        context_parts = []
        for i, doc in enumerate(documents, 1):
            context_parts.append(f"[Document {i}]: {doc}")
        
        context_text = "\n".join(context_parts)
        
        return f"""
Based on the following knowledge base documents:

{context_text}

Please answer the user's question: {query}

Use the information from the documents above to provide an accurate response.
If the documents don't contain relevant information, state that clearly.
"""
    
    async def search_with_filter(
        self, 
        query: str, 
        filter_metadata: Dict[str, Any],
        top_k: int = 3
    ) -> List[SearchResult]:
        """
        Search with metadata filtering.
        
        Args:
            query: Search query
            filter_metadata: Metadata filters (e.g., {"category": "phishing"})
            top_k: Max results
        
        Returns:
            List of SearchResult
        """
        query_embedding = await self.embedder.embed(query)
        return await self.store.search(query_embedding, top_k, filter_metadata)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get retriever statistics."""
        return {
            "total_documents": self.store.count(),
            "embedding_provider": self.embedder.provider,
            "embedding_dimension": self.embedder.dimension
        }


# Initialize with demo security knowledge base
async def init_security_knowledge_base(retriever: RAGRetriever):
    """
    Initialize knowledge base with security documents.
    Call this on startup for demo.
    """
    security_docs = [
        {
            "content": "Phishing is a cyber attack where attackers impersonate legitimate organizations to steal sensitive information like passwords and credit card numbers. Common signs include suspicious sender addresses, urgent language, and mismatched URLs.",
            "metadata": {"category": "phishing", "type": "definition"}
        },
        {
            "content": "To detect phishing emails, check: 1) Sender address matches the company domain, 2) No spelling/grammar errors, 3) Links point to legitimate URLs, 4) No urgent requests for personal information, 5) No suspicious attachments.",
            "metadata": {"category": "phishing", "type": "detection"}
        },
        {
            "content": "Strong passwords should be at least 12 characters long, include uppercase, lowercase, numbers, and special characters. Never reuse passwords across accounts. Use a password manager to generate and store unique passwords.",
            "metadata": {"category": "passwords", "type": "best_practice"}
        },
        {
            "content": "Two-factor authentication (2FA) adds an extra layer of security by requiring a second verification method. Use authenticator apps (like Google Authenticator or Authy) instead of SMS when possible, as SMS can be intercepted.",
            "metadata": {"category": "authentication", "type": "best_practice"}
        },
        {
            "content": "Malware types include: Viruses (self-replicating), Trojans (disguised as legitimate software), Ransomware (encrypts files for ransom), Spyware (monitors activity), and Adware (displays unwanted ads).",
            "metadata": {"category": "malware", "type": "definition"}
        },
        {
            "content": "To prevent retail fraud: Verify all vendor invoices, implement approval workflows for payments over certain amounts, train employees to recognize social engineering, and use secure payment methods with fraud protection.",
            "metadata": {"category": "retail_fraud", "type": "prevention"}
        },
        {
            "content": "Security logs should be reviewed for: Failed login attempts (possible brute force), Unusual access times, Privilege escalation attempts, Data exfiltration patterns, and Configuration changes.",
            "metadata": {"category": "logs", "type": "monitoring"}
        },
        {
            "content": "Business Email Compromise (BEC) involves attackers impersonating executives or vendors to request wire transfers or sensitive data. Always verify unusual requests through a secondary channel like a phone call.",
            "metadata": {"category": "bec", "type": "prevention"}
        }
    ]
    
    await retriever.add_documents(security_docs)
    return len(security_docs)


# Global instance
rag_retriever = RAGRetriever()

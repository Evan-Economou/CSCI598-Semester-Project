"""
RAG (Retrieval-Augmented Generation) service for context-aware analysis
"""
from typing import List, Optional, Dict, Any
import os
import uuid
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer


class RAGService:
    """Manage RAG knowledge base for style guides and references"""

    def __init__(self):
        self.rag_data_path = os.getenv("RAG_DATA_PATH", "./rag_data")
        self.chunk_size = int(os.getenv("CHUNK_SIZE", "500"))
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "50"))

        # Initialize ChromaDB and embedder
        self.chroma_client = chromadb.PersistentClient(
            path=self.rag_data_path,
            settings=Settings(anonymized_telemetry=False)
        )
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.collection = self._get_or_create_collection()

    def _get_or_create_collection(self):
        """Get or create ChromaDB collection"""
        return self.chroma_client.get_or_create_collection(
            name="code_style_guides",
            metadata={"description": "Code style guides and reference documents"}
        )

    def add_document(
        self,
        content: str,
        doc_type: str,
        metadata: Optional[dict] = None
    ) -> str:
        """
        Add a document to the RAG knowledge base

        Args:
            content: Document content
            doc_type: Type of document (style_guide, reference, etc.)
            metadata: Additional metadata

        Returns:
            Document ID
        """
        # Generate unique document ID
        doc_id = str(uuid.uuid4())
        print(f"\n{'='*60}")
        print(f"Adding document to RAG database")
        print(f"Document ID: {doc_id}")
        print(f"Type: {doc_type}")
        print(f"Content length: {len(content)} chars")
        if metadata:
            print(f"Metadata: {metadata}")
        print(f"{'='*60}\n")

        # Chunk the document
        print(f"Step 1: Chunking document...")
        chunks = self._chunk_document(content)
        print(f"[OK] Created {len(chunks)} chunks")

        # Generate embeddings for each chunk
        print(f"Step 2: Generating embeddings...")
        embeddings = self.embedder.encode(chunks).tolist()
        print(f"[OK] Generated {len(embeddings)} embeddings")

        # Prepare metadata for each chunk
        print(f"Step 3: Preparing metadata...")
        chunk_ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
        chunk_metadata = []
        for i in range(len(chunks)):
            meta = {
                "doc_id": doc_id,
                "doc_type": doc_type,
                "chunk_index": i,
                "total_chunks": len(chunks)
            }
            if metadata:
                meta.update(metadata)
            chunk_metadata.append(meta)

        # Add to ChromaDB
        print(f"Step 4: Storing in ChromaDB...")
        self.collection.add(
            ids=chunk_ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=chunk_metadata
        )

        print(f"[OK] Successfully added document {doc_id} to RAG database")
        print(f"{'='*60}\n")
        return doc_id

    def _chunk_document(self, content: str) -> List[str]:
        """
        Split document into overlapping chunks

        Args:
            content: Full document content

        Returns:
            List of text chunks
        """
        chunks = []
        lines = content.split('\n')
        current_chunk = []
        current_size = 0

        for line in lines:
            line_size = len(line)

            if current_size + line_size > self.chunk_size and current_chunk:
                # Save current chunk
                chunks.append('\n'.join(current_chunk))

                # Start new chunk with overlap
                overlap_lines = current_chunk[-3:]  # Keep last 3 lines for overlap
                current_chunk = overlap_lines + [line]
                current_size = sum(len(l) for l in current_chunk)
            else:
                current_chunk.append(line)
                current_size += line_size

        # Add final chunk
        if current_chunk:
            chunks.append('\n'.join(current_chunk))

        return chunks

    def search_relevant_context(
        self,
        query: str,
        top_k: int = 3
    ) -> List[str]:
        """
        Search for relevant context based on query

        Args:
            query: Search query (e.g., code snippet or violation description)
            top_k: Number of results to return

        Returns:
            List of relevant text chunks
        """
        try:
            print(f"  -> Searching RAG database...")
            print(f"    Query length: {len(query)} chars")
            print(f"    Requesting top {top_k} results")

            # Generate query embedding
            print(f"  -> Generating query embedding...")
            query_embedding = self.embedder.encode([query])[0].tolist()

            # Search ChromaDB
            print(f"  -> Querying ChromaDB collection...")
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )

            # Extract and return document texts
            if results and 'documents' in results and len(results['documents']) > 0:
                found_docs = results['documents'][0]
                print(f"    Found {len(found_docs)} relevant chunks")
                return found_docs  # First query's results

            print(f"    No documents found in RAG database")
            return []

        except Exception as e:
            print(f"[ERROR] Error searching for context: {e}")
            import traceback
            traceback.print_exc()
            return []

    def delete_document(self, doc_id: str) -> bool:
        """Remove document from knowledge base"""
        try:
            # Get all chunks belonging to this document
            results = self.collection.get(
                where={"doc_id": doc_id}
            )

            if results and 'ids' in results and len(results['ids']) > 0:
                # Delete all chunks
                self.collection.delete(ids=results['ids'])
                print(f"Deleted document {doc_id} with {len(results['ids'])} chunks")
                return True

            return False

        except Exception as e:
            print(f"Error deleting document: {e}")
            return False

    def list_documents(self) -> List[Dict[str, Any]]:
        """List all documents in knowledge base"""
        try:
            # Get all items from collection
            results = self.collection.get()

            if not results or 'metadatas' not in results:
                return []

            # Group chunks by document ID
            docs_dict = {}
            for metadata in results['metadatas']:
                doc_id = metadata.get('doc_id')
                if doc_id and doc_id not in docs_dict:
                    docs_dict[doc_id] = {
                        'id': doc_id,
                        'doc_type': metadata.get('doc_type', 'unknown'),
                        'filename': metadata.get('filename', 'unknown'),
                        'total_chunks': metadata.get('total_chunks', 0)
                    }

            return list(docs_dict.values())

        except Exception as e:
            print(f"Error listing documents: {e}")
            return []

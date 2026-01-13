#!/usr/bin/env python3
"""
Populate the knowledge base with Noovy data
"""

import json
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.knowledge_base import KnowledgeBase

def populate_knowledge_base():
    """Load Noovy knowledge data and populate the knowledge base"""
    
    print("🚀 Starting knowledge base population...")
    
    # Initialize knowledge base
    kb = KnowledgeBase()
    
    # Load Noovy data
    noovy_file = 'backend/data/noovy_knowledge.json'
    print(f"📂 Loading data from: {noovy_file}")
    
    with open(noovy_file, 'r', encoding='utf-8') as f:
        noovy_data = json.load(f)
    
    print(f"📊 Found {len(noovy_data)} articles to process")
    
    # Process each article
    documents = []
    metadatas = []
    
    for idx, article in enumerate(noovy_data):
        # Create document text
        doc_text = f"""
כותרת: {article['title']}
קטגוריה: {article['category']}

{article['content']}

מקור: Noovy Knowledge Base
קישור: {article['url']}
"""
        
        documents.append(doc_text)
        metadatas.append({
            'title': article['title'],
            'category': article['category'],
            'source': 'Noovy KB',
            'url': article['url'],
            'type': 'hotel_management'
        })
        
        print(f"   ✓ Processed: {article['title'][:50]}...")
    
    # Add to knowledge base
    print(f"\n💾 Adding {len(documents)} documents to knowledge base...")
    kb.add_documents(documents, metadatas)
    
    print("\n✅ Knowledge base populated successfully!")
    print(f"   Total documents: {len(documents)}")
    
    # Test search
    print("\n🔍 Testing search functionality...")
    test_queries = [
        "איך לעשות צ'ק אין?",
        "How to cancel a booking?",
        "מה זה Room Calendar?"
    ]
    
    for query in test_queries:
        print(f"\n   Query: {query}")
        results = kb.search(query, k=2)
        for i, result in enumerate(results, 1):
            print(f"      {i}. {result['metadata'].get('title', 'No title')[:60]}...")
            print(f"         Relevance: {result['score']:.2f}")

if __name__ == "__main__":
    populate_knowledge_base()

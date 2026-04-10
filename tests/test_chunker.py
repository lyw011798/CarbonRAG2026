import pytest
from src.chunker import ChunkStrategy

def test_chunk_strategy_legal_articles():
    chunker = ChunkStrategy(max_chunk_size=100)
    
    text = """
    This is the preamble.
    第一條
    This is the first article text. It defines the purpose of the act.
    
    第二條之三
    This is an amended article with a sub-number. Very important context here.
    """
    
    metadata = {"source": "test_act.txt"}
    chunks = chunker.split_text(text, metadata)
    
    assert len(chunks) == 3
    
    assert chunks[0]['metadata']['article'] == 'Preamble'
    assert chunks[0]['text'] == 'This is the preamble.'
    
    assert chunks[1]['metadata']['article'] == '第一條'
    assert chunks[1]['text'].startswith('第一條')
    assert "purpose of the act" in chunks[1]['text']
    assert chunks[1]['metadata']['source'] == "test_act.txt"
    
    assert chunks[2]['metadata']['article'] == '第二條之三'
    assert chunks[2]['text'].startswith('第二條之三')

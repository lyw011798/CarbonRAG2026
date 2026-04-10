import chromadb
client = chromadb.PersistentClient(path='./db/chroma')
col = client.get_collection('taiwan_carbon_market')
print(f'Collection: {col.name}')
print(f'Total records: {col.count()}')
print()
# Peek at first 3 records
data = col.peek(limit=3)
print('=== Sample Documents (first 100 chars) ===')
for doc in data['documents']:
    print(f'  {doc[:100]}...')
print()
print('=== Sample Metadata ===')
for meta in data['metadatas']:
    print(f'  {meta}')
print()
print('=== Metadata Keys ===')
print(f'  {list(data["metadatas"][0].keys())}')

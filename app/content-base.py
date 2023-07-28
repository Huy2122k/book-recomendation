import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def get_encoded_vectors(books):
    titles = [book["BookName"] for book in books]
    authors = [book["Author"] for book in books]
    publishers = [book["Publisher"] for book in books]

    # Tạo mã hóa vector cho tiêu đề, tác giả và nhà xuất bản
    vectorizer = CountVectorizer()
    title_vectors = vectorizer.fit_transform(titles).toarray()
    author_vectors = vectorizer.fit_transform(authors).toarray()
    publisher_vectors = vectorizer.fit_transform(publishers).toarray()

    return title_vectors, author_vectors, publisher_vectors

def book_recommendation(books, query_book, top_n=5):
    query_title = query_book["BookName"]
    query_author = query_book["Author"]
    query_publisher = query_book["Publisher"]

    title_vectors, author_vectors, publisher_vectors = get_encoded_vectors(books)

    # Tìm vị trí của sách cần tìm
    book_index = next((index for index, book in enumerate(books) if book == query_book), None)

    if book_index is None:
        return "Không tìm thấy sách trong danh sách."

    # Lấy vector của sách cần tìm
    query_title_vector = title_vectors[book_index].reshape(1, -1)
    query_author_vector = author_vectors[book_index].reshape(1, -1)
    query_publisher_vector = publisher_vectors[book_index].reshape(1, -1)

    # Tính cosine similarity với các cuốn sách khác
    title_similarity = cosine_similarity(query_title_vector, title_vectors)[0]
    author_similarity = cosine_similarity(query_author_vector, author_vectors)[0]
    publisher_similarity = cosine_similarity(query_publisher_vector, publisher_vectors)[0]

    # Tổng hợp điểm số dựa trên tiêu đề, tác giả và nhà xuất bản
    total_similarity = title_similarity + author_similarity + publisher_similarity

    # Sắp xếp và lấy top n sách gợi ý
    similar_books_indices = np.argsort(total_similarity)[::-1][1:top_n + 1]  # Bỏ qua sách cần tìm
    recommended_books = [books[i] for i in similar_books_indices]

    return recommended_books

# Ví dụ danh sách các cuốn sách
books = [
    {
        "BookName": "Harry Potter and the Philosopher's Stone",
        "Author": "J.K. Rowling",
        "Publisher": "Bloomsbury Publishing"
    },
    {
        "BookName": "To Kill a Mockingbird",
        "Author": "Harper Lee",
        "Publisher": "J. B. Lippincott & Co."
    },
    {
        "BookName": "The Great Gatsby",
        "Author": "F. Scott Fitzgerald",
        "Publisher": "Charles Scribner's Sons"
    },
    # Thêm các cuốn sách khác vào đây
]

# Chọn một cuốn sách để tìm gợi ý
query_book = {
    "BookName": "Harry Potter and the Philosopher's Stone",
    "Author": "J.K. Rowling",
    "Publisher": "Bloomsbury Publishing"
}

# Gợi ý sách dựa trên cuốn sách trên
recommended_books = book_recommendation(books, query_book)

# In kết quả gợi ý sách
if recommended_books:
    print("Sách được gợi ý:")
    for book in recommended_books:
        print(f"Tên sách: {book['BookName']}, Tác giả: {book['Author']}, Nhà xuất bản: {book['Publisher']}")
else:
    print("Không có sách gợi ý.")

import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { formatDate } from '../utils/dateUtils'

const Books = () => {
  const [books, setBooks] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [filters, setFilters] = useState({
    title: '',
    author: '',
    genre: '',
    availableOnly: true,
  })
  const [showAddForm, setShowAddForm] = useState(false)
  const [newBook, setNewBook] = useState({
    title: '',
    author: '',
    genre: '',
    publish_year: '',
    meeting_address: '',
    description: '',
  })

  const { token } = useAuth()
  const API_BASE_URL = 'http://localhost:5000/api'

  const fetchBooks = async () => {
    try {
      const params = new URLSearchParams({
        limit: '20',
        available_only: filters.availableOnly.toString(),
        ...(filters.title && { title: filters.title }),
        ...(filters.author && { author: filters.author }),
        ...(filters.genre && { genre: filters.genre }),
      })

      const response = await fetch(`${API_BASE_URL}/books?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        setBooks(data.books)
      } else {
        setError('Failed to fetch books')
      }
    } catch (error) {
      setError('Network error')
    } finally {
      setLoading(false)
    }
  }

  const handleTakeBook = async (bookId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/books/${bookId}/take`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        fetchBooks()
      } else {
        const data = await response.json()
        setError(data.error || 'Failed to take book')
      }
    } catch (error) {
      setError('Network error')
    }
  }

  const handleAddBook = async (e) => {
    e.preventDefault()
    try {
      const response = await fetch(`${API_BASE_URL}/books`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          ...newBook,
          publish_year: parseInt(newBook.publish_year),
        }),
      })

      if (response.ok) {
        setNewBook({
          title: '',
          author: '',
          genre: '',
          publish_year: '',
          meeting_address: '',
          description: '',
        })
        setShowAddForm(false)
        fetchBooks()
      } else {
        const data = await response.json()
        setError(data.error || 'Failed to add book')
      }
    } catch (error) {
      setError('Network error')
    }
  }

  useEffect(() => {
    fetchBooks()
  }, [filters])

  const handleFilterChange = (e) => {
    const { name, value, type, checked } = e.target
    setFilters(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }))
  }

  const handleNewBookChange = (e) => {
    setNewBook(prev => ({
      ...prev,
      [e.target.name]: e.target.value,
    }))
  }

  if (loading) return <div className="loading">Loading books...</div>

  return (
    <div>
      <div className="card-header">
        <h1 className="card-title">Browse Books</h1>
        <button 
          onClick={() => setShowAddForm(!showAddForm)}
          className="btn btn-primary"
        >
          {showAddForm ? 'Cancel' : 'Add Book'}
        </button>
      </div>

      {error && (
        <div className="alert alert-error">
          {error}
          <button 
            onClick={() => setError('')}
            style={{ marginLeft: '1rem', background: 'none', border: 'none', color: 'inherit', cursor: 'pointer' }}
          >
            ×
          </button>
        </div>
      )}

      {showAddForm && (
        <div className="card">
          <h3>Add New Book</h3>
          <form onSubmit={handleAddBook}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1rem' }}>
              <div className="form-group">
                <label className="form-label">Title</label>
                <input
                  type="text"
                  name="title"
                  className="form-input"
                  value={newBook.title}
                  onChange={handleNewBookChange}
                  required
                />
              </div>
              <div className="form-group">
                <label className="form-label">Author</label>
                <input
                  type="text"
                  name="author"
                  className="form-input"
                  value={newBook.author}
                  onChange={handleNewBookChange}
                  required
                />
              </div>
              <div className="form-group">
                <label className="form-label">Genre</label>
                <input
                  type="text"
                  name="genre"
                  className="form-input"
                  value={newBook.genre}
                  onChange={handleNewBookChange}
                  required
                />
              </div>
              <div className="form-group">
                <label className="form-label">Publication Year</label>
                <input
                  type="number"
                  name="publish_year"
                  className="form-input"
                  value={newBook.publish_year}
                  onChange={handleNewBookChange}
                  required
                />
              </div>
            </div>
            <div className="form-group">
              <label className="form-label">Meeting Address</label>
              <input
                type="text"
                name="meeting_address"
                className="form-input"
                value={newBook.meeting_address}
                onChange={handleNewBookChange}
                placeholder="Where should people meet to get the book?"
                required
              />
            </div>
            <div className="form-group">
              <label className="form-label">Description (Optional)</label>
              <textarea
                name="description"
                className="form-input form-textarea"
                value={newBook.description}
                onChange={handleNewBookChange}
                placeholder="Book condition, notes, etc."
              />
            </div>
            <button type="submit" className="btn btn-primary">
              Add Book
            </button>
          </form>
        </div>
      )}

      <div className="card">
        <h3>Filter Books</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
          <div className="form-group">
            <label className="form-label">Title</label>
            <input
              type="text"
              name="title"
              className="form-input"
              placeholder="Search by title..."
              value={filters.title}
              onChange={handleFilterChange}
            />
          </div>
          <div className="form-group">
            <label className="form-label">Author</label>
            <input
              type="text"
              name="author"
              className="form-input"
              placeholder="Search by author..."
              value={filters.author}
              onChange={handleFilterChange}
            />
          </div>
          <div className="form-group">
            <label className="form-label">Genre</label>
            <input
              type="text"
              name="genre"
              className="form-input"
              placeholder="Search by genre..."
              value={filters.genre}
              onChange={handleFilterChange}
            />
          </div>
          <div className="form-group">
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <input
                type="checkbox"
                name="availableOnly"
                checked={filters.availableOnly}
                onChange={handleFilterChange}
              />
              Available only
            </label>
          </div>
        </div>
      </div>

      <div className="books-grid">
        {books.length === 0 ? (
          <p>No books found matching your criteria.</p>
        ) : (
          books.map((book) => (
            <div key={book.id} className="card book-card">
              <div className="card-header">
                <h3 className="card-title">{book.title}</h3>
                <span className={`btn btn-small ${book.is_available ? 'btn-secondary' : 'btn-danger'}`}>
                  {book.is_available ? 'Available' : 'Taken'}
                </span>
              </div>
              <div className="card-content">
                <div className="book-meta">
                  <span><strong>Author:</strong> {book.author}</span>
                  <span><strong>Year:</strong> {book.publish_year}</span>
                </div>
                <div className="book-meta">
                  <span><strong>Genre:</strong> {book.genre}</span>
                </div>
                {book.description && (
                  <p style={{ margin: '1rem 0' }}>{book.description}</p>
                )}
                <p><strong>Meeting Address:</strong> {book.meeting_address}</p>
                <p style={{ fontSize: '0.875rem', color: '#64748b', marginTop: '1rem' }}>
                  Posted on {formatDate(book.created_at)}
                </p>
                {book.is_available && (
                  <button
                    onClick={() => handleTakeBook(book.id)}
                    className="btn btn-primary"
                    style={{ marginTop: '1rem' }}
                  >
                    Take This Book
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default Books
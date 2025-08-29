import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { formatDate } from '../utils/dateUtils'

const MyBooks = () => {
  const [books, setBooks] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [editingBook, setEditingBook] = useState(null)

  const { token } = useAuth()
  const API_BASE_URL = 'http://localhost:5000/api'

  const fetchMyBooks = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/books/my`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        setBooks(data.books)
      } else {
        setError('Failed to fetch your books')
      }
    } catch (error) {
      setError('Network error')
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteBook = async (bookId) => {
    if (!confirm('Are you sure you want to delete this book?')) return

    try {
      const response = await fetch(`${API_BASE_URL}/books/${bookId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        fetchMyBooks()
      } else {
        const data = await response.json()
        setError(data.error || 'Failed to delete book')
      }
    } catch (error) {
      setError('Network error')
    }
  }

  const handleEditBook = async (bookId, updatedData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/books/${bookId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          ...updatedData,
          publish_year: parseInt(updatedData.publish_year),
        }),
      })

      if (response.ok) {
        setEditingBook(null)
        fetchMyBooks()
      } else {
        const data = await response.json()
        setError(data.error || 'Failed to update book')
      }
    } catch (error) {
      setError('Network error')
    }
  }

  const EditForm = ({ book, onSave, onCancel }) => {
    const [formData, setFormData] = useState({
      title: book.title,
      author: book.author,
      genre: book.genre,
      publish_year: book.publish_year.toString(),
      meeting_address: book.meeting_address,
      description: book.description || '',
    })

    const handleChange = (e) => {
      setFormData(prev => ({
        ...prev,
        [e.target.name]: e.target.value,
      }))
    }

    const handleSubmit = (e) => {
      e.preventDefault()
      onSave(book.id, formData)
    }

    return (
      <form onSubmit={handleSubmit}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1rem' }}>
          <div className="form-group">
            <label className="form-label">Title</label>
            <input
              type="text"
              name="title"
              className="form-input"
              value={formData.title}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label className="form-label">Author</label>
            <input
              type="text"
              name="author"
              className="form-input"
              value={formData.author}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label className="form-label">Genre</label>
            <input
              type="text"
              name="genre"
              className="form-input"
              value={formData.genre}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label className="form-label">Publication Year</label>
            <input
              type="number"
              name="publish_year"
              className="form-input"
              value={formData.publish_year}
              onChange={handleChange}
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
            value={formData.meeting_address}
            onChange={handleChange}
            required
          />
        </div>
        <div className="form-group">
          <label className="form-label">Description</label>
          <textarea
            name="description"
            className="form-input form-textarea"
            value={formData.description}
            onChange={handleChange}
          />
        </div>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button type="submit" className="btn btn-primary btn-small">
            Save
          </button>
          <button type="button" onClick={onCancel} className="btn btn-secondary btn-small">
            Cancel
          </button>
        </div>
      </form>
    )
  }

  useEffect(() => {
    fetchMyBooks()
  }, [])

  if (loading) return <div className="loading">Loading your books...</div>

  return (
    <div>
      <h1>My Books</h1>
      
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

      <div className="books-grid">
        {books.length === 0 ? (
          <div className="card">
            <p>You haven't posted any books yet.</p>
          </div>
        ) : (
          books.map((book) => (
            <div key={book.id} className="card book-card">
              {editingBook === book.id ? (
                <EditForm
                  book={book}
                  onSave={handleEditBook}
                  onCancel={() => setEditingBook(null)}
                />
              ) : (
                <>
                  <div className="card-header">
                    <h3 className="card-title">{book.title}</h3>
                    <div>
                      <span className={`btn btn-small ${book.is_available ? 'btn-secondary' : 'btn-danger'}`}>
                        {book.is_available ? 'Available' : 'Taken'}
                      </span>
                    </div>
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
                    {book.taken_by && (
                      <p style={{ color: '#ef4444', fontWeight: 'bold' }}>
                        Taken on {formatDate(book.taken_at)}
                      </p>
                    )}
                    <p style={{ fontSize: '0.875rem', color: '#64748b', marginTop: '1rem' }}>
                      Posted on {formatDate(book.created_at)}
                    </p>
                    <div style={{ display: 'flex', gap: '0.5rem', marginTop: '1rem' }}>
                      <button
                        onClick={() => setEditingBook(book.id)}
                        className="btn btn-secondary btn-small"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDeleteBook(book.id)}
                        className="btn btn-danger btn-small"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                </>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default MyBooks
import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { formatDate } from '../utils/dateUtils'

const TakenBooks = () => {
  const [books, setBooks] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const { token } = useAuth()
  const API_BASE_URL = 'http://localhost:5000/api'

  const fetchTakenBooks = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/books/taken`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        setBooks(data.books)
      } else {
        setError('Failed to fetch taken books')
      }
    } catch (error) {
      setError('Network error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchTakenBooks()
  }, [])

  if (loading) return <div className="loading">Loading taken books...</div>

  return (
    <div>
      <h1>Books I've Taken</h1>
      
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
            <p>You haven't taken any books yet.</p>
          </div>
        ) : (
          books.map((book) => (
            <div key={book.id} className="card book-card">
              <div className="card-header">
                <h3 className="card-title">{book.title}</h3>
                <span className="btn btn-small btn-danger">
                  Taken
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
                <p style={{ color: '#16a34a', fontWeight: 'bold', marginTop: '1rem' }}>
                  Taken on {formatDate(book.taken_at)}
                </p>
                <p style={{ fontSize: '0.875rem', color: '#64748b' }}>
                  Originally posted on {formatDate(book.created_at)}
                </p>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default TakenBooks
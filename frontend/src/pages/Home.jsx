import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

const Home = () => {
  const { isAuthenticated } = useAuth()

  return (
    <div>
      <section className="hero">
        <h1>Welcome to BookCrossing</h1>
        <p>Share books with your community. Give a book, take a book.</p>
        {!isAuthenticated && (
          <div style={{ marginTop: '2rem' }}>
            <Link to="/register" className="btn btn-secondary" style={{ marginRight: '1rem' }}>
              Get Started
            </Link>
            <Link to="/login" className="btn btn-primary">
              Sign In
            </Link>
          </div>
        )}
      </section>

      <section className="features">
        <div className="feature card">
          <div className="feature-icon">📚</div>
          <h3>Share Books</h3>
          <p>Post books you no longer need and let others discover them</p>
        </div>
        
        <div className="feature card">
          <div className="feature-icon">🔍</div>
          <h3>Discover Books</h3>
          <p>Browse through books shared by your community</p>
        </div>
        
        <div className="feature card">
          <div className="feature-icon">🤝</div>
          <h3>Meet Locally</h3>
          <p>Arrange pickup locations and meet fellow book lovers</p>
        </div>
      </section>

      {isAuthenticated && (
        <section className="card">
          <h2>Quick Actions</h2>
          <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem', flexWrap: 'wrap' }}>
            <Link to="/books" className="btn btn-primary">
              Browse Books
            </Link>
            <Link to="/my-books" className="btn btn-secondary">
              My Books
            </Link>
          </div>
        </section>
      )}
    </div>
  )
}

export default Home
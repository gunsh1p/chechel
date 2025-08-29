import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

const Header = () => {
  const { user, isAuthenticated, logout } = useAuth()
  const location = useLocation()

  const handleLogout = () => {
    logout()
  }

  const isActive = (path) => location.pathname === path

  return (
    <header className="header">
      <div className="header-content">
        <Link to="/" className="logo">
          BookCrossing
        </Link>
        
        <nav>
          <ul className="nav-links">
            {!isAuthenticated ? (
              <>
                <li>
                  <Link 
                    to="/login" 
                    className={`nav-link ${isActive('/login') ? 'active' : ''}`}
                  >
                    Login
                  </Link>
                </li>
                <li>
                  <Link 
                    to="/register" 
                    className={`nav-link ${isActive('/register') ? 'active' : ''}`}
                  >
                    Register
                  </Link>
                </li>
              </>
            ) : (
              <>
                <li>
                  <Link 
                    to="/books" 
                    className={`nav-link ${isActive('/books') ? 'active' : ''}`}
                  >
                    Browse Books
                  </Link>
                </li>
                <li>
                  <Link 
                    to="/my-books" 
                    className={`nav-link ${isActive('/my-books') ? 'active' : ''}`}
                  >
                    My Books
                  </Link>
                </li>
                <li>
                  <Link 
                    to="/taken-books" 
                    className={`nav-link ${isActive('/taken-books') ? 'active' : ''}`}
                  >
                    Taken Books
                  </Link>
                </li>
                {user?.role === 'admin' && (
                  <li>
                    <Link 
                      to="/admin" 
                      className={`nav-link ${isActive('/admin') ? 'active' : ''}`}
                    >
                      Admin Panel
                    </Link>
                  </li>
                )}
                <li>
                  <span className="nav-link">
                    Welcome, {user?.username}!
                  </span>
                </li>
                <li>
                  <button 
                    onClick={handleLogout} 
                    className="nav-link" 
                    style={{ background: 'none', border: 'none', cursor: 'pointer' }}
                  >
                    Logout
                  </button>
                </li>
              </>
            )}
          </ul>
        </nav>
      </div>
    </header>
  )
}

export default Header
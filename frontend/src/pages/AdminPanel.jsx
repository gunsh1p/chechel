import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { formatDate } from '../utils/dateUtils'

const AdminPanel = () => {
  const [users, setUsers] = useState([])
  const [statistics, setStatistics] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [activeTab, setActiveTab] = useState('statistics')

  const { token } = useAuth()
  const API_BASE_URL = 'http://localhost:5000/api'

  const fetchStatistics = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/admin/statistics`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        setStatistics(data)
      } else {
        setError('Failed to fetch statistics')
      }
    } catch (error) {
      setError('Network error')
    }
  }

  const fetchUsers = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/admin/users?limit=50`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        setUsers(data.users)
      } else {
        setError('Failed to fetch users')
      }
    } catch (error) {
      setError('Network error')
    }
  }

  const handleDeleteUser = async (userId) => {
    if (!confirm('Are you sure you want to delete this user and all their books?')) return

    try {
      const response = await fetch(`${API_BASE_URL}/admin/users/${userId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        fetchUsers()
        fetchStatistics()
      } else {
        const data = await response.json()
        setError(data.error || 'Failed to delete user')
      }
    } catch (error) {
      setError('Network error')
    }
  }

  const handleRoleChange = async (userId, newRole) => {
    try {
      const response = await fetch(`${API_BASE_URL}/admin/users/${userId}/role`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ role: newRole }),
      })

      if (response.ok) {
        fetchUsers()
      } else {
        const data = await response.json()
        setError(data.error || 'Failed to update user role')
      }
    } catch (error) {
      setError('Network error')
    }
  }

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      await Promise.all([fetchStatistics(), fetchUsers()])
      setLoading(false)
    }
    fetchData()
  }, [])

  if (loading) return <div className="loading">Loading admin panel...</div>

  return (
    <div>
      <h1>Admin Panel</h1>
      
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

      <div className="card">
        <div style={{ display: 'flex', gap: '1rem', marginBottom: '2rem' }}>
          <button
            onClick={() => setActiveTab('statistics')}
            className={`btn ${activeTab === 'statistics' ? 'btn-primary' : 'btn-secondary'}`}
          >
            Statistics
          </button>
          <button
            onClick={() => setActiveTab('users')}
            className={`btn ${activeTab === 'users' ? 'btn-primary' : 'btn-secondary'}`}
          >
            User Management
          </button>
        </div>

        {activeTab === 'statistics' && statistics && (
          <div>
            <h2>Platform Statistics</h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginTop: '1rem' }}>
              <div className="card" style={{ textAlign: 'center' }}>
                <h3 style={{ color: '#3b82f6', fontSize: '2rem', margin: '0' }}>
                  {statistics.total_users}
                </h3>
                <p>Total Users</p>
              </div>
              <div className="card" style={{ textAlign: 'center' }}>
                <h3 style={{ color: '#16a34a', fontSize: '2rem', margin: '0' }}>
                  {statistics.total_books}
                </h3>
                <p>Total Books</p>
              </div>
              <div className="card" style={{ textAlign: 'center' }}>
                <h3 style={{ color: '#ea580c', fontSize: '2rem', margin: '0' }}>
                  {statistics.available_books}
                </h3>
                <p>Available Books</p>
              </div>
              <div className="card" style={{ textAlign: 'center' }}>
                <h3 style={{ color: '#dc2626', fontSize: '2rem', margin: '0' }}>
                  {statistics.total_exchanges}
                </h3>
                <p>Total Exchanges</p>
              </div>
              <div className="card" style={{ textAlign: 'center' }}>
                <h3 style={{ color: '#7c3aed', fontSize: '2rem', margin: '0' }}>
                  {statistics.books_created_today}
                </h3>
                <p>Books Added Today</p>
              </div>
              <div className="card" style={{ textAlign: 'center' }}>
                <h3 style={{ color: '#0891b2', fontSize: '1.5rem', margin: '0' }}>
                  {statistics.most_popular_genre}
                </h3>
                <p>Most Popular Genre</p>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'users' && (
          <div>
            <h2>User Management</h2>
            <div className="table-container" style={{ overflowX: 'auto' }}>
              <table className="table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Username</th>
                    <th>Role</th>
                    <th>Created At</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((user) => (
                    <tr key={user.id}>
                      <td>{user.id}</td>
                      <td>{user.username}</td>
                      <td>
                        <select
                          value={user.role}
                          onChange={(e) => handleRoleChange(user.id, e.target.value)}
                          className="form-input"
                          style={{ padding: '0.25rem', fontSize: '0.875rem' }}
                        >
                          <option value="user">User</option>
                          <option value="admin">Admin</option>
                        </select>
                      </td>
                      <td>{formatDate(user.created_at)}</td>
                      <td>
                        <button
                          onClick={() => handleDeleteUser(user.id)}
                          className="btn btn-danger btn-small"
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {users.length === 0 && (
              <p>No users found.</p>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default AdminPanel
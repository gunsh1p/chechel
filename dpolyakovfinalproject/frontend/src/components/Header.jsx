import React from 'react';
import {Link, useNavigate} from 'react-router-dom';
import {useAuth} from '../context/AuthContext';
import './Header.css';

function Header() {
    const {isAuthenticated, user, logout, isAdmin} = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <header className="app-header">
            <div className="header-container">
                <Link to="/" className="logo-link"><h1>CuWorking</h1></Link>
                <nav>
                    <ul className="nav-links">
                        <li><Link to="/places">Все места</Link></li>
                        {isAuthenticated ? (
                            <>
                                <li><Link to="/my-bookings">Мои бронирования</Link></li>
                                {isAdmin && <li><Link to="/add-place">Добавить место</Link></li>}
                                {isAdmin && (
                                    <>
                                        <li><Link to="/admin/places">Все места (Админ)</Link></li>
                                        <li><Link to="/admin/users">Все пользователи (Админ)</Link></li>
                                    </>
                                )}
                            </>
                        ) : (
                            <>
                                <li><Link to="/login">Войти</Link></li>
                                <li><Link to="/register">Регистрация</Link></li>
                            </>
                        )}
                    </ul>
                </nav>
                <div className="header-actions">
                    {isAuthenticated && (
                        <button onClick={handleLogout} className="nav-button nav-btn-logout">
                            Выйти ({user?.username})
                        </button>
                    )}
                </div>
            </div>
        </header>
    );
}

export default Header;
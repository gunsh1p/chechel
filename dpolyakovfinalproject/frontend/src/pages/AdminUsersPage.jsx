import React, {useState, useEffect} from 'react';
import {useAuth} from '../context/AuthContext';

function AdminUsersPage() {
    const [allUsers, setAllUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const {isLoading: authLoading, isAdmin, getAuthHeader} = useAuth();

    useEffect(() => {
        if (authLoading) {
            return;
        }

        const fetchAllUsers = async () => {
            setLoading(true);
            setError(null);

            try {
                const response = await fetch('/api/admin/users', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': getAuthHeader(),
                    },
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.message || `Ошибка загрузки всех пользователей: ${response.status}`);
                }

                const data = await response.json();
                setAllUsers(data);
            } catch (err) {
                console.error("Failed to fetch all users for admin:", err);
                setError('Не удалось загрузить список всех пользователей. Попробуйте позже.');
            } finally {
                setLoading(false);
            }
        };

        fetchAllUsers();

    }, [authLoading, isAdmin]);
    if (authLoading || loading) {
        return <p>Загрузка всех пользователей (Админ)...</p>;
    }


    if (error) {
        return <p className="error-message">Ошибка при загрузке всех пользователей: {error}</p>;
    }

    const handleDeleteUser = async (userId) => {
        if (!window.confirm('Админ: удалить этого пользователя?')) return;
        try {
            const response = await fetch(`/api/admin/users/${userId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': getAuthHeader(),
                },
            });
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Ошибка удаления пользователя');
            }
            setAllUsers(prevUsers => prevUsers.filter(user => user.id !== userId));
        } catch (err) {
            alert('Ошибка при удалении пользователя: ' + err.message);
        }
    };

    return (
        <div>
            <h2>Все пользователи в системе (Админ)</h2>
            {allUsers.length === 0 ? (
                <p>В системе пока нет пользователей (кроме, возможно, вас).</p>
            ) : (
                <ul>
                    {allUsers.map(user => (
                        <li key={user.id}>
                            <strong>ID: {user.id}</strong> - {user.username} ({user.email})
                            - {user.is_admin ? 'Администратор' : 'Пользователь'}
                            <button onClick={() => handleDeleteUser(user.id)} style={{color: 'red', marginLeft: '10px'}}>Удалить</button>
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
}

export default AdminUsersPage;

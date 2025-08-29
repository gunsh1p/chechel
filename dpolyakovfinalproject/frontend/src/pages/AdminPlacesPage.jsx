import React, {useState, useEffect} from 'react';
import {useAuth} from '../context/AuthContext';

function AdminPlacesPage() {
    const [allPlaces, setAllPlaces] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const {isLoading: authLoading, isAdmin, getAuthHeader} = useAuth();

    useEffect(() => {
        if (authLoading) return;
        const fetchAllPlaces = async () => {
            setLoading(true);
            setError(null);
            try {
                const response = await fetch('/api/places', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': getAuthHeader(),
                    },
                });
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.message || `Ошибка загрузки всех мест: ${response.status}`);
                }
                const data = await response.json();
                setAllPlaces(data);
            } catch (err) {
                setError('Не удалось загрузить список всех мест. Попробуйте позже.');
            } finally {
                setLoading(false);
            }
        };
        fetchAllPlaces();
    }, [authLoading, isAdmin, getAuthHeader]);

    const handleDeletePlace = async (placeId) => {
        if (!window.confirm('Админ: удалить это место?')) return;
        try {
            const response = await fetch(`/api/admin/places/${placeId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': getAuthHeader(),
                },
            });
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Ошибка удаления места');
            }
            setAllPlaces(prevPlaces => prevPlaces.filter(place => place.id !== placeId));
        } catch (err) {
            alert('Ошибка при удалении места: ' + err.message);
        }
    };

    if (authLoading || loading) {
        return <p>Загрузка всех мест (Админ)...</p>;
    }
    if (!isAdmin) {
        return null;
    }
    if (error) {
        return <p className="error-message">{error}</p>;
    }
    return (
        <div>
            <h2>Все места в системе (Админ)</h2>
            {allPlaces.length === 0 ? (
                <p>В системе пока нет мест.</p>
            ) : (
                <ul>
                    {allPlaces.map(place => (
                        <li key={place.id}>
                            <strong>{place.name}</strong> - <em>{place.location}</em>
                            {place.description && <span> | {place.description}</span>}
                            <span> | {place.is_available ? 'Доступно' : 'Недоступно'}</span>
                            <button onClick={() => handleDeletePlace(place.id)} style={{color: 'red', marginLeft: '10px'}}>Удалить</button>
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
}

export default AdminPlacesPage; 
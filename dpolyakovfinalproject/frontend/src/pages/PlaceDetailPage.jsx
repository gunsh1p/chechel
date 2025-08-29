import React, {useState, useEffect} from 'react';
import {useParams} from 'react-router-dom';
import {useAuth} from '../context/AuthContext';
import './PlaceDetailPage.css';

function PlaceDetailPage() {
    const {place_id} = useParams();
    const [place, setPlace] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const {user, isAuthenticated, isLoading: authLoading, getAuthHeader} = useAuth();
    const [bookingDate, setBookingDate] = useState('');
    const [bookingStartTime, setBookingStartTime] = useState('');
    const [bookingEndTime, setBookingEndTime] = useState('');
    const [bookingError, setBookingError] = useState(null);
    const [bookingSuccess, setBookingSuccess] = useState(null);

    useEffect(() => {
        const fetchPlace = async () => {
            setLoading(true);
            setError(null);
            try {
                const response = await fetch(`/api/places/${place_id}`);
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.message || `Ошибка загрузки места: ${response.status}`);
                }
                const data = await response.json();
                setPlace(data);
            } catch (err) {
                setError('Не удалось загрузить информацию о месте. Попробуйте позже.');
            } finally {
                setLoading(false);
            }
        };
        fetchPlace();
    }, [place_id]);

    const handleBookingSubmit = async (e) => {
        e.preventDefault();
        setBookingError(null);
        setBookingSuccess(null);
        if (!bookingDate || !bookingStartTime || !bookingEndTime) {
            setBookingError('Укажите дату, время начала и окончания бронирования');
            return;
        }
        const start_time = bookingDate + 'T' + bookingStartTime;
        const end_time = bookingDate + 'T' + bookingEndTime;
        try {
            const response = await fetch('/api/bookings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': getAuthHeader(),
                },
                body: JSON.stringify({
                    place_id: place.id,
                    start_time,
                    end_time
                })
            });
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || errorData.message || 'Ошибка бронирования');
            }
            setBookingSuccess('Место успешно забронировано!');
        } catch (err) {
            setBookingError(err.message);
        }
    };

    if (authLoading || loading) {
        return <p>Загрузка деталей места...</p>;
    }
    if (error) {
        return <p className="error-message">Ошибка: {error}</p>;
    }
    if (!place && !loading) {
        return <p>Место не найдено.</p>;
    }
    return (
        <div className="place-detail-container">
            <h2>{place.name}</h2>
            <p><strong>Локация:</strong> {place.location}</p>
            {place.description && <p><strong>Описание:</strong> {place.description}</p>}
            <p><strong>Владелец (ID):</strong> {place.owner_id}
                {isAuthenticated && user?.id === place.owner_id && <span> (Это ваше место)</span>}
            </p>
            <p><strong>Статус:</strong> {place.is_available ? 'Доступно для бронирования' : 'Недоступно'}</p>
            {isAuthenticated && place.is_available && (
                <form onSubmit={handleBookingSubmit} className="booking-form">
                    <label>
                        Дата:
                        <input type="date" value={bookingDate} onChange={e => setBookingDate(e.target.value)} required />
                    </label>
                    <label>
                        Время начала:
                        <input type="time" value={bookingStartTime} onChange={e => setBookingStartTime(e.target.value)} required />
                    </label>
                    <label>
                        Время окончания:
                        <input type="time" value={bookingEndTime} onChange={e => setBookingEndTime(e.target.value)} required />
                    </label>
                    {bookingError && <div className="error-message">{bookingError}</div>}
                    {bookingSuccess && <div className="success-message">{bookingSuccess}</div>}
                    <button type="submit" className="filter-button apply">Забронировать</button>
                </form>
            )}
        </div>
    );
}

export default PlaceDetailPage;

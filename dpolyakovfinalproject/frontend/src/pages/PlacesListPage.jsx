import React, {useState, useEffect, useCallback} from 'react';
import {Link} from 'react-router-dom';
import {useAuth} from '../context/AuthContext';
import './PlacesListPage.css';

function PlacesListPage() {
    const [places, setPlaces] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const {isAuthenticated, isLoading: authLoading, getAuthHeader} = useAuth();
    const [bookingPlace, setBookingPlace] = useState(null);
    const [bookingDate, setBookingDate] = useState('');
    const [bookingStartTime, setBookingStartTime] = useState('');
    const [bookingEndTime, setBookingEndTime] = useState('');
    const [bookingError, setBookingError] = useState(null);
    const [bookingSuccess, setBookingSuccess] = useState(null);

    const fetchPlaces = useCallback(async () => {
        setLoading(true);
        setError(null);
        const queryParams = new URLSearchParams();
        const queryString = queryParams.toString();
        try {
            const response = await fetch(`/api/places${queryString ? `?${queryString}` : ''}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                },
            });
            if (!response.ok) {
                let errorText = await response.text();
                throw new Error(errorText || `Ошибка загрузки мест: ${response.status}`);
            }
            const data = await response.json();
            setPlaces(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        if (!authLoading) {
            fetchPlaces();
        }
    }, [fetchPlaces, authLoading]);

    const handleOpenBooking = (place) => {
        setBookingPlace(place);
        setBookingDate('');
        setBookingStartTime('');
        setBookingEndTime('');
        setBookingError(null);
        setBookingSuccess(null);
    };

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
                    place_id: bookingPlace.id,
                    start_time,
                    end_time
                })
            });
            if (response.status === 409) {
                setBookingError('Это время уже занято другим бронированием. Пожалуйста, выберите другое время.');
                return;
            }
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || errorData.message || 'Ошибка бронирования');
            }
            setBookingSuccess('Место успешно забронировано!');
            setTimeout(() => {
                setBookingPlace(null);
                fetchPlaces();
            }, 1200);
        } catch (err) {
            setBookingError(err.message);
        }
    };

    if (authLoading || (loading && places.length === 0)) {
        return <p>Загрузка мест...</p>;
    }

    if (error) {
        return <p className="error-message">Ошибка при загрузке мест: {error}</p>;
    }

    return (
        <div className="places-list-container">
            <h2>Доступные места для бронирования</h2>
            {loading && <p>Обновление списка мест...</p>}
            {places.length === 0 && !loading ? (
                <p>Нет доступных мест.</p>
            ) : (
                <ul className="places-ul">
                    {places.map(place => (
                        <li key={place.id} className="place-item">
                            <div>
                                <span className="place-title-link"><strong>{place.name}</strong></span>
                                <span> - <em>{place.location}</em></span>
                                {place.description && <span> | {place.description}</span>}
                            </div>
                            <span className={place.is_available ? 'status-available' : 'status-unavailable'}>
                                ({place.is_available ? 'Доступно' : 'Недоступно'})
                            </span>
                            {isAuthenticated && place.is_available && (
                                <button className="reserve-button" onClick={() => handleOpenBooking(place)}>
                                    Забронировать
                                </button>
                            )}
                        </li>
                    ))}
                </ul>
            )}
            {bookingPlace && (
                <div className="modal-backdrop">
                    <div className="modal modal-booking">
                        <h3>Бронирование места: {bookingPlace.name}</h3>
                        <form onSubmit={handleBookingSubmit} className="booking-form">
                            <label>
                                Дата:
                                <input type="date" value={bookingDate} onChange={e => setBookingDate(e.target.value)} required className="booking-input" />
                            </label>
                            <label>
                                Время начала:
                                <input type="time" value={bookingStartTime} onChange={e => setBookingStartTime(e.target.value)} required className="booking-input" />
                            </label>
                            <label>
                                Время окончания:
                                <input type="time" value={bookingEndTime} onChange={e => setBookingEndTime(e.target.value)} required className="booking-input" />
                            </label>
                            {bookingError && <div className="error-message">{bookingError}</div>}
                            {bookingSuccess && <div className="success-message">{bookingSuccess}</div>}
                            <div style={{marginTop: '1em'}}>
                                <button type="submit" className="filter-button apply">Забронировать</button>
                                <button type="button" className="filter-button clear" onClick={() => setBookingPlace(null)}>
                                    Отмена
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}

export default PlacesListPage;

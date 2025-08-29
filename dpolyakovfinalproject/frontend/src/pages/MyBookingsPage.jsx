import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';

function MyBookingsPage() {
  const [bookings, setBookings] = useState([]);
  const [places, setPlaces] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [moveId, setMoveId] = useState(null);
  const [moveStart, setMoveStart] = useState('');
  const [moveEnd, setMoveEnd] = useState('');
  const [moveError, setMoveError] = useState(null);
  const [moveSuccess, setMoveSuccess] = useState(null);
  const [moveStartTime, setMoveStartTime] = useState('');
  const [moveEndTime, setMoveEndTime] = useState('');

  const { isLoading: authLoading, isAuthenticated, getAuthHeader } = useAuth();

  // Загружаем все места
  useEffect(() => {
    const fetchPlaces = async () => {
      try {
        const response = await fetch('/api/places', {
          headers: { 'Content-Type': 'application/json' }
        });
        if (!response.ok) throw new Error('Ошибка загрузки мест');
        const data = await response.json();
        setPlaces(data);
      } catch (err) {
        setError('Ошибка загрузки мест');
      }
    };
    fetchPlaces();
  }, []);

  // Загружаем бронирования пользователя
  useEffect(() => {
    if (authLoading) return;
    const fetchBookings = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch('/api/bookings', {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': getAuthHeader(),
          },
          credentials: 'include',
        });
        if (response.status === 401) {
          setError('Вы не авторизованы. Пожалуйста, войдите в систему.');
          setBookings([]);
          setLoading(false);
          return;
        }
        if (!response.ok) {
          const err = await response.json();
          throw new Error(err.message || 'Ошибка загрузки бронирований');
        }
        const data = await response.json();
        setBookings(data);
      } catch (err) {
        setError(err.message);
        setBookings([]);
      } finally {
        setLoading(false);
      }
    };
    if (isAuthenticated) fetchBookings();
  }, [authLoading, isAuthenticated, getAuthHeader]);

  const handleCancel = async (id) => {
    if (!window.confirm('Точно отменить бронирование?')) return;
    try {
      const res = await fetch(`/api/bookings/${id}/cancel`, {
        method: 'POST',
        headers: { 'Authorization': getAuthHeader() },
        credentials: 'include',
      });
      if (!res.ok) throw new Error('Ошибка отмены');
      setBookings(bookings => bookings.map(b => b.id === id ? { ...b, status: 'cancelled' } : b));
    } catch (e) {
      alert('Ошибка отмены бронирования');
    }
  };

  const handleMove = (id) => {
    setMoveId(id);
    setMoveStart('');
    setMoveStartTime('');
    setMoveEndTime('');
    setMoveError(null);
    setMoveSuccess(null);
  };

  const handleMoveSubmit = async (e) => {
    e.preventDefault();
    setMoveError(null);
    setMoveSuccess(null);
    const booking = bookings.find(b => b.id === moveId);
    if (!moveStart || !moveStartTime || !moveEndTime) {
      setMoveError('Укажите дату и время');
      return;
    }
    if (moveStartTime >= moveEndTime) {
      setMoveError('Время окончания должно быть позже времени начала');
      return;
    }
    // Формируем новые start_time и end_time
    const newStart = moveStart + 'T' + moveStartTime;
    const newEnd = moveStart + 'T' + moveEndTime;
    try {
      const res = await fetch(`/api/bookings/${moveId}/move`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': getAuthHeader(),
        },
        credentials: 'include',
        body: JSON.stringify({ start_time: newStart, end_time: newEnd })
      });
      if (res.status === 409) {
        setMoveError('Новое время уже занято другим бронированием. Пожалуйста, выберите другое время.');
        return;
      }
      if (!res.ok) throw new Error('Ошибка переноса');
      setMoveSuccess('Бронирование перенесено!');
      setBookings(bookings => bookings.map(b => b.id === moveId ? { ...b, start_time: newStart, end_time: newEnd } : b));
      setTimeout(() => setMoveId(null), 1000);
    } catch (e) {
      setMoveError('Ошибка переноса бронирования');
    }
  };

  if (authLoading || loading) return <div>Загрузка...</div>;
  if (error) return <div className="error-message">{error}</div>;

  // Вспомогательная функция для поиска места по id
  const getPlaceInfo = (place_id) => places.find(p => p.id === place_id);

  return (
    <div className="my-bookings-container">
      <h2>Мои бронирования</h2>
      {Array.isArray(bookings) && bookings.length === 0 ? (
        <div>У вас нет бронирований.</div>
      ) : (
        <ul className="bookings-list">
          {bookings.map(b => {
            const place = getPlaceInfo(b.place_id);
            return (
              <li key={b.id} className="booking-item">
                <div>
                  <strong>Место:</strong> {place ? place.name : b.place_id}
                  {place && <> — <em>{place.location}</em></>}
                  {place && place.description && <> | {place.description}</>}
                  <br />
                  <strong>Начало:</strong> {new Date(b.start_time).toLocaleString()}<br />
                  <strong>Окончание:</strong> {new Date(b.end_time).toLocaleString()}<br />
                  <strong>Статус:</strong> {b.status}
                </div>
                {b.status === 'active' && (
                  <div className="booking-actions">
                    <button onClick={() => handleCancel(b.id)}>Отменить</button>
                    <button onClick={() => handleMove(b.id)}>Перенести</button>
                  </div>
                )}
                {moveId === b.id && (
                  <form onSubmit={handleMoveSubmit} className="move-form">
                    <input type="date" value={moveStart} onChange={e => setMoveStart(e.target.value)} required />
                    <input type="time" value={moveStartTime} onChange={e => setMoveStartTime(e.target.value)} required />
                    <input type="time" value={moveEndTime} onChange={e => setMoveEndTime(e.target.value)} required />
                    <button type="submit">Сохранить</button>
                    <button type="button" onClick={() => setMoveId(null)}>Отмена</button>
                    {moveError && <div className="error-message">{moveError}</div>}
                    {moveSuccess && <div className="success-message">{moveSuccess}</div>}
                  </form>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}

export default MyBookingsPage;
import React, {useState} from 'react';
import {useAuth} from '../context/AuthContext';
import {useNavigate} from 'react-router-dom';

function AddPlacePage() {
    const [name, setName] = useState('');
    const [location, setLocation] = useState('');
    const [description, setDescription] = useState('');
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);
    const {getAuthHeader, isAdmin} = useAuth();
    const navigate = useNavigate();

    if (!isAdmin) {
        return <div className="form-container" style={{color: '#ef4444', background: '#2a2323', border: '2px solid #ef4444', borderRadius: '12px', padding: '2em', marginTop: '2em', textAlign: 'center'}}>Только администраторы могут добавлять места для бронирования.</div>;
    }

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setSuccess(null);
        if (!name) {
            setError('Название места обязательно');
            return;
        }
        try {
            const response = await fetch('/api/places', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': getAuthHeader(),
                },
                body: JSON.stringify({
                    name,
                    location,
                    description,
                    is_available: true
                })
            });
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Ошибка добавления места');
            }
            setSuccess('Место успешно добавлено!');
            setTimeout(() => navigate('/places'), 1200);
        } catch (err) {
            setError(err.message);
        }
    };

    return (
        <div className="form-container add-place-redesign">
            <h2 style={{color: '#ef4444', marginBottom: '1em'}}>Добавить новое место</h2>
            <form onSubmit={handleSubmit} className="add-form add-form-redesign">
                <div className="add-form-row">
                    <label>Название места:
                        <input type="text" value={name} onChange={e => setName(e.target.value)} required className="add-input"/>
                    </label>
                    <label>Локация/зона:
                        <input type="text" value={location} onChange={e => setLocation(e.target.value)} className="add-input"/>
                    </label>
                </div>
                <div className="add-form-row">
                    <label style={{flex: 1}}>Описание:
                        <textarea value={description} onChange={e => setDescription(e.target.value)} className="add-input"/>
                    </label>
                </div>
                <div className="add-form-row" style={{alignItems: 'center'}}>
                    <button type="submit" className="filter-button apply add-btn-red">Добавить место</button>
                </div>
                {error && <div className="error-message" style={{color: '#ef4444'}}>{error}</div>}
                {success && <div className="success-message" style={{color: '#22c55e'}}>{success}</div>}
            </form>
        </div>
    );
}

export default AddPlacePage;

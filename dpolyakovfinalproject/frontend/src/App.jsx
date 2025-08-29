import React from 'react';
import {Routes, Route} from 'react-router-dom';
import './App.css';

import Header from './components/Header';

import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import PlacesListPage from './pages/PlacesListPage';
import MyBookingsPage from './pages/MyBookingsPage';
import AddPlacePage from './pages/AddPlacePage';
import PlaceDetailPage from './pages/PlaceDetailPage';
import AdminPlacesPage from './pages/AdminPlacesPage';
import AdminUsersPage from './pages/AdminUsersPage';
import NotFoundPage from './pages/NotFoundPage';

import {ProtectedRoute, AdminProtectedRoute} from './components/ProtectedRoute';

function App() {
    return (
        <div className="app-container">
            <Header/>
            <main className="main-content">
                <Routes>
                    {/* Публичные маршруты (доступны всем)*/}
                    <Route path="/" element={<HomePage/>}/>
                    <Route path="/login" element={<LoginPage/>}/>
                    <Route path="/register" element={<RegisterPage/>}/>
                    <Route path="/places" element={<PlacesListPage/>}/>
                    <Route path="/places/:place_id" element={<PlaceDetailPage/>}/>

                    {/* Защищенные маршруты (надо авторизоваться) */}
                    <Route path="/my-bookings" element={
                        <ProtectedRoute>
                            <MyBookingsPage/>
                        </ProtectedRoute>
                    }/>
                     <Route path="/add-place" element={
                        <ProtectedRoute>
                            <AddPlacePage/>
                        </ProtectedRoute>
                    }/>

                    <Route path="/admin/places" element={
                         <AdminProtectedRoute>
                            <AdminPlacesPage/>
                        </AdminProtectedRoute>
                    }/>
                    <Route path="/admin/users" element={
                         <AdminProtectedRoute>
                            <AdminUsersPage/>
                        </AdminProtectedRoute>
                    }/>

                    <Route path="*" element={<NotFoundPage/>}/>
                </Routes>
            </main>
        </div>
    );
}

export default App;

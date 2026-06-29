import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore';
import { AppLayout } from './components/layout/AppLayout';

import { Dashboard } from './pages/Dashboard';
import { TtsStudio } from './pages/TtsStudio';
import { VoiceLibrary } from './pages/VoiceLibrary';
import { VoiceCloning } from './pages/VoiceCloning';
import { History } from './pages/History';

export const App = () => {
    return (
        <BrowserRouter>
            <Routes>
                {/* Main Application Routes (No Guards) */}
                <Route element={<AppLayout />}>
                    <Route path="/" element={<Navigate to="/dashboard" replace />} />
                    <Route path="/dashboard" element={<Dashboard />} />
                    <Route path="/studio" element={<TtsStudio />} />
                    <Route path="/voices" element={<VoiceLibrary />} />
                    <Route path="/clone" element={<VoiceCloning />} />
                    <Route path="/history" element={<History />} />
                </Route>
                
                {/* Fallback */}
                <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
        </BrowserRouter>
    );
};

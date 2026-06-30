import React, { createContext, useContext, useEffect, useState } from 'react';

const ThemeContext = createContext();

export const ThemeProvider = ({ children }) => {
    useEffect(() => {
        const root = window.document.documentElement;
        root.classList.add('dark');
        localStorage.setItem('theme', 'dark');
    }, []);

    const toggleTheme = () => {
        // Disabled by user request
    };

    return (
        <ThemeContext.Provider value={{ theme: 'dark', toggleTheme }}>
            {children}
        </ThemeContext.Provider>
    );
};

export const useTheme = () => useContext(ThemeContext);

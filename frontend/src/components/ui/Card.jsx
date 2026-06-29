import React from 'react';

export const Card = ({ children, className = '', ...props }) => {
    return (
        <div className={`bg-white dark:bg-slate-900/80 rounded-xl border border-slate-200/60 dark:border-slate-800 p-6 shadow-[0_4px_20px_-4px_rgba(0,0,0,0.05)] dark:shadow-none transition-all duration-300 ${className}`} {...props}>
            {children}
        </div>
    );
};

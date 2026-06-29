
import React from 'react';

export const Card = ({ children, className = '', ...props }) => {
    return (
        <div className={`bg-white/90 dark:bg-slate-900/50 backdrop-blur-sm border border-slate-200 dark:border-slate-800/80 rounded-xl p-6 shadow-xl ${className}`} {...props}>
            {children}
        </div>
    );
};

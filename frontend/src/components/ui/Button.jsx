
import React from 'react';

export const Button = ({ children, variant = 'primary', className = '', ...props }) => {
    const base = "inline-flex items-center justify-center font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-950 disabled:opacity-50 disabled:cursor-not-allowed";
    const variants = {
        primary: "bg-indigo-600 hover:bg-indigo-700 text-white focus:ring-indigo-500",
        secondary: "bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 focus:ring-slate-500",
        danger: "bg-red-600 hover:bg-red-700 text-white focus:ring-red-500",
        ghost: "bg-transparent hover:bg-slate-800 text-slate-300 hover:text-white focus:ring-slate-500"
    };
    return (
        <button type={props.type || 'button'} className={`${base} ${variants[variant]} px-4 py-2 ${className}`} {...props}>
            {children}
        </button>
    );
};

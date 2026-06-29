
import React from 'react';

export const Input = ({ label, ...props }) => {
    return (
        <div className="flex flex-col gap-1.5 w-full">
            {label && <label className="text-sm font-medium text-slate-300">{label}</label>}
            <input 
                className="w-full px-4 py-2.5 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-colors placeholder:text-slate-500"
                {...props} 
            />
        </div>
    );
};

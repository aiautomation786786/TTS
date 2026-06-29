
import { create } from 'zustand';
export const useAppStore = create((set) => ({
    sidebarCollapsed: false,
    toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
    pageTitle: '',
    setPageTitle: (title) => set({ pageTitle: title })
}));

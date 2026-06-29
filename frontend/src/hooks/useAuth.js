import useAuthStore from '../store/authStore';

const useAuth = () => {
  const { user, token, isAuthenticated, isLoading, login, register, logout, fetchUser, initialize } = useAuthStore();

  const isAdmin = user?.role === 'admin';
  const quotaPercent = user?.char_quota ? Math.min((user.chars_used / user.char_quota) * 100, 100) : 0;
  const quotaRemaining = user?.char_quota ? user.char_quota - (user.chars_used || 0) : 0;

  return {
    user,
    token,
    isAuthenticated,
    isLoading,
    isAdmin,
    quotaPercent,
    quotaRemaining,
    login,
    register,
    logout,
    fetchUser,
    initialize,
  };
};

export default useAuth;

import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface User {
    id: string
    username: string
    email?: string
    is_admin: boolean
    is_active: boolean
    quota_gb: number
    used_space_gb: number
}

interface AuthState {
    user: User | null
    accessToken: string | null
    refreshToken: string | null
    isAuthenticated: boolean

    setTokens: (accessToken: string, refreshToken: string) => void
    setUser: (user: User) => void
    logout: () => void
}

export const useAuthStore = create<AuthState>()(
    persist(
        (set) => ({
            user: null,
            accessToken: typeof window !== 'undefined' ? localStorage.getItem('access_token') : null,
            refreshToken: typeof window !== 'undefined' ? localStorage.getItem('refresh_token') : null,
            isAuthenticated: typeof window !== 'undefined' ? !!localStorage.getItem('access_token') : false,

            setTokens: (accessToken, refreshToken) => {
                if (typeof window !== 'undefined') {
                    localStorage.setItem('access_token', accessToken)
                    localStorage.setItem('refresh_token', refreshToken)
                }
                set({ accessToken, refreshToken, isAuthenticated: true })
            },

            setUser: (user) => set({ user }),

            logout: () => {
                if (typeof window !== 'undefined') {
                    localStorage.removeItem('access_token')
                    localStorage.removeItem('refresh_token')
                }
                set({
                    user: null,
                    accessToken: null,
                    refreshToken: null,
                    isAuthenticated: false,
                })
            },
        }),
        {
            name: 'auth-storage',
            partialize: (state) => ({
                user: state.user,
                isAuthenticated: state.isAuthenticated,
                accessToken: state.accessToken,
                refreshToken: state.refreshToken,
            }),
        }
    )
)

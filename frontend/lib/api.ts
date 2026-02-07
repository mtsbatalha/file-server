import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const api = axios.create({
    baseURL: `${API_URL}/api`,
    headers: {
        'Content-Type': 'application/json',
    },
})

// Request interceptor to add auth token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token')
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    },
    (error) => {
        return Promise.reject(error)
    }
)

// Response interceptor to handle 401 errors
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config

        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true

            try {
                const refreshToken = localStorage.getItem('refresh_token')
                if (refreshToken) {
                    const { data } = await axios.post(`${API_URL}/api/auth/refresh`, {
                        refresh_token: refreshToken,
                    })

                    localStorage.setItem('access_token', data.access_token)
                    localStorage.setItem('refresh_token', data.refresh_token)

                    originalRequest.headers.Authorization = `Bearer ${data.access_token}`
                    return api(originalRequest)
                }
            } catch (refreshError) {
                localStorage.removeItem('access_token')
                localStorage.removeItem('refresh_token')
                window.location.href = '/login'
                return Promise.reject(refreshError)
            }
        }

        return Promise.reject(error)
    }
)

// Auth API
export const authAPI = {
    login: (username: string, password: string) =>
        api.post('/auth/login', { username, password }),

    logout: () => api.post('/auth/logout'),

    me: () => api.get('/auth/me'),
}

// Users API
export const usersAPI = {
    list: (skip = 0, limit = 100) =>
        api.get('/users', { params: { skip, limit } }),

    create: (data: any) => api.post('/users', data),

    get: (id: string) => api.get(`/users/${id}`),

    update: (id: string, data: any) => api.put(`/users/${id}`, data),

    delete: (id: string) => api.delete(`/users/${id}`),

    getUsage: (id: string) => api.get(`/users/${id}/usage`),
}

// Protocols API
export const protocolsAPI = {
    list: () => api.get('/protocols'),

    get: (name: string) => api.get(`/protocols/${name}`),

    install: (name: string) => api.post(`/protocols/${name}/install`),

    start: (name: string) => api.post(`/protocols/${name}/start`),

    stop: (name: string) => api.post(`/protocols/${name}/stop`),

    getStatus: (name: string) => api.get(`/protocols/${name}/status`),

    updateConfig: (name: string, data: any) =>
        api.put(`/protocols/${name}/config`, data),
}

// Quotas API
export const quotasAPI = {
    getSummary: () => api.get('/quotas/summary'),
}

// Paths API
export const pathsAPI = {
    list: () => api.get('/paths'),
    create: (data: any) => api.post('/paths', data),
    get: (id: string) => api.get(`/paths/${id}`),
    update: (id: string, data: any) => api.put(`/paths/${id}`, data),
    delete: (id: string) => api.delete(`/paths/${id}`),
}

// Logs API
export const logsAPI = {
    getAccessLogs: (params?: any) => api.get('/logs/access', { params }),
}

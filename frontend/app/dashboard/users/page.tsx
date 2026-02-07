'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { usersAPI } from '@/lib/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '@/components/ui/table'
import {
    Plus,
    Trash2,
    RefreshCw,
    Loader2,
    UserCheck,
    UserX,
    Shield
} from 'lucide-react'
import { useAuthStore } from '@/lib/store'
import { formatBytes } from '@/lib/utils'

export default function UsersPage() {
    const queryClient = useQueryClient()
    const { user: currentUser } = useAuthStore()
    const [showCreateForm, setShowCreateForm] = useState(false)
    const [formData, setFormData] = useState({
        username: '',
        password: '',
        email: '',
        quota_gb: 50,
    })

    const { data: users, isLoading } = useQuery({
        queryKey: ['users'],
        queryFn: async () => {
            const { data } = await usersAPI.list()
            return data
        },
    })

    const createMutation = useMutation({
        mutationFn: (data: any) => usersAPI.create(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['users'] })
            setShowCreateForm(false)
            setFormData({ username: '', password: '', email: '', quota_gb: 50 })
        },
    })

    const deleteMutation = useMutation({
        mutationFn: (userId: string) => usersAPI.delete(userId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['users'] })
        },
    })

    const handleCreate = async (e: React.FormEvent) => {
        e.preventDefault()
        try {
            // Transform empty email to null for Pydantic validation
            const payload = {
                ...formData,
                email: formData.email.trim() || null
            }
            await createMutation.mutateAsync(payload)
        } catch (error: any) {
            alert(error.response?.data?.detail || 'Failed to create user')
        }
    }

    const handleDelete = async (userId: string, username: string) => {
        if (confirm(`Are you sure you want to delete user "${username}"?`)) {
            try {
                await deleteMutation.mutateAsync(userId)
            } catch (error: any) {
                alert(error.response?.data?.detail || 'Failed to delete user')
            }
        }
    }

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <Loader2 className="w-8 h-8 animate-spin text-primary" />
            </div>
        )
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">Users</h1>
                    <p className="text-muted-foreground mt-1">
                        Manage user accounts and permissions
                    </p>
                </div>
                <div className="flex gap-2">
                    <Button
                        variant="outline"
                        onClick={() => queryClient.invalidateQueries({ queryKey: ['users'] })}
                    >
                        <RefreshCw className="w-4 h-4 mr-2" />
                        Refresh
                    </Button>
                    {currentUser?.is_admin && (
                        <Button onClick={() => setShowCreateForm(!showCreateForm)}>
                            <Plus className="w-4 h-4 mr-2" />
                            Add User
                        </Button>
                    )}
                </div>
            </div>

            {/* Create User Form */}
            {showCreateForm && (
                <Card>
                    <CardHeader>
                        <CardTitle>Create New User</CardTitle>
                        <CardDescription>Add a new user account to the system</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <form onSubmit={handleCreate} className="space-y-4">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <label className="text-sm font-medium">Username *</label>
                                    <Input
                                        type="text"
                                        value={formData.username}
                                        onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                                        required
                                    />
                                </div>

                                <div className="space-y-2">
                                    <label className="text-sm font-medium">Email</label>
                                    <Input
                                        type="email"
                                        value={formData.email}
                                        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                    />
                                </div>

                                <div className="space-y-2">
                                    <label className="text-sm font-medium">Password *</label>
                                    <Input
                                        type="password"
                                        value={formData.password}
                                        onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                                        required
                                    />
                                </div>

                                <div className="space-y-2">
                                    <label className="text-sm font-medium">Quota (GB)</label>
                                    <Input
                                        type="number"
                                        value={formData.quota_gb}
                                        onChange={(e) => setFormData({ ...formData, quota_gb: parseInt(e.target.value) })}
                                        min={1}
                                    />
                                </div>
                            </div>

                            <div className="flex gap-2">
                                <Button type="submit" disabled={createMutation.isPending}>
                                    {createMutation.isPending ? (
                                        <>
                                            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                            Creating...
                                        </>
                                    ) : (
                                        'Create User'
                                    )}
                                </Button>
                                <Button
                                    type="button"
                                    variant="outline"
                                    onClick={() => setShowCreateForm(false)}
                                >
                                    Cancel
                                </Button>
                            </div>
                        </form>
                    </CardContent>
                </Card>
            )}

            {/* Users Table */}
            <Card>
                <CardHeader>
                    <CardTitle>User Accounts ({users?.length || 0})</CardTitle>
                    <CardDescription>
                        Manage system users and their access permissions
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>Username</TableHead>
                                <TableHead>Email</TableHead>
                                <TableHead>Role</TableHead>
                                <TableHead>Quota</TableHead>
                                <TableHead>Status</TableHead>
                                <TableHead className="text-right">Actions</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {users?.map((user: any) => (
                                <TableRow key={user.id}>
                                    <TableCell className="font-medium">
                                        <div className="flex items-center gap-2">
                                            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white text-xs font-semibold">
                                                {user.username[0].toUpperCase()}
                                            </div>
                                            {user.username}
                                        </div>
                                    </TableCell>
                                    <TableCell className="text-muted-foreground">
                                        {user.email || 'N/A'}
                                    </TableCell>
                                    <TableCell>
                                        {user.is_admin ? (
                                            <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-700 dark:bg-purple-900/20 dark:text-purple-400">
                                                <Shield className="w-3.5 h-3.5" />
                                                Admin
                                            </div>
                                        ) : (
                                            <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400">
                                                User
                                            </div>
                                        )}
                                    </TableCell>
                                    <TableCell>
                                        <div className="text-sm">
                                            <div className="font-medium">{formatBytes(user.used_space_gb * 1024 * 1024 * 1024)}</div>
                                            <div className="text-muted-foreground text-xs">
                                                of {user.quota_gb} GB
                                            </div>
                                        </div>
                                    </TableCell>
                                    <TableCell>
                                        {user.is_active ? (
                                            <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-400">
                                                <UserCheck className="w-3.5 h-3.5" />
                                                Active
                                            </div>
                                        ) : (
                                            <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400">
                                                <UserX className="w-3.5 h-3.5" />
                                                Inactive
                                            </div>
                                        )}
                                    </TableCell>
                                    <TableCell className="text-right">
                                        {currentUser?.is_admin && user.id !== currentUser?.id && (
                                            <Button
                                                size="sm"
                                                variant="outline"
                                                onClick={() => handleDelete(user.id, user.username)}
                                                disabled={deleteMutation.isPending}
                                            >
                                                <Trash2 className="w-4 h-4 mr-2" />
                                                Delete
                                            </Button>
                                        )}
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </CardContent>
            </Card>
        </div>
    )
}

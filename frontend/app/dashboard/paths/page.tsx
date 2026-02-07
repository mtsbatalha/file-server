'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { pathsAPI, protocolsAPI, usersAPI } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '@/components/ui/table'
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from '@/components/ui/dialog'
import { Checkbox } from '@/components/ui/checkbox'
import { FolderOpen, Plus, Pencil, Trash2, Loader2, Users, Shield, Eye, Edit2 } from 'lucide-react'
import { toast } from 'sonner'

interface UserAccess {
    user_id: string
    username: string
    permission: 'read' | 'write' | 'full'
}

interface SharedPath {
    id: string
    name: string
    path: string
    description: string | null
    protocols: string[]
    user_accesses: UserAccess[]
    created_at: string
    updated_at: string
}

interface Protocol {
    name: string
    display_name: string
    status: string
}

interface User {
    id: string
    username: string
    is_admin: boolean
}

const permissionLabels: Record<string, { label: string; icon: any; color: string }> = {
    read: { label: 'Read Only', icon: Eye, color: 'bg-blue-100 text-blue-700 dark:bg-blue-900/20 dark:text-blue-400' },
    write: { label: 'Read & Write', icon: Edit2, color: 'bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-400' },
    full: { label: 'Full Control', icon: Shield, color: 'bg-purple-100 text-purple-700 dark:bg-purple-900/20 dark:text-purple-400' },
}

export default function PathsPage() {
    const queryClient = useQueryClient()
    const [isCreateOpen, setIsCreateOpen] = useState(false)
    const [isEditOpen, setIsEditOpen] = useState(false)
    const [isDeleteOpen, setIsDeleteOpen] = useState(false)
    const [selectedPath, setSelectedPath] = useState<SharedPath | null>(null)
    const [formData, setFormData] = useState({
        name: '',
        path: '',
        description: '',
        protocols: [] as string[],
        user_accesses: [] as { user_id: string; permission: string }[]
    })

    const { data: paths, isLoading } = useQuery({
        queryKey: ['paths'],
        queryFn: async () => {
            const res = await pathsAPI.list()
            return res.data as SharedPath[]
        }
    })

    const { data: protocols } = useQuery({
        queryKey: ['protocols'],
        queryFn: async () => {
            const res = await protocolsAPI.list()
            return res.data as Protocol[]
        }
    })

    const { data: users } = useQuery({
        queryKey: ['users'],
        queryFn: async () => {
            const res = await usersAPI.list()
            return res.data as User[]
        }
    })

    const createMutation = useMutation({
        mutationFn: (data: any) => pathsAPI.create(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['paths'] })
            setIsCreateOpen(false)
            resetForm()
            toast.success('Shared path created successfully')
        },
        onError: (error: any) => {
            toast.error(error.response?.data?.detail || 'Failed to create path')
        }
    })

    const updateMutation = useMutation({
        mutationFn: ({ id, data }: { id: string, data: any }) => pathsAPI.update(id, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['paths'] })
            setIsEditOpen(false)
            setSelectedPath(null)
            resetForm()
            toast.success('Shared path updated successfully')
        },
        onError: (error: any) => {
            toast.error(error.response?.data?.detail || 'Failed to update path')
        }
    })

    const deleteMutation = useMutation({
        mutationFn: (id: string) => pathsAPI.delete(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['paths'] })
            setIsDeleteOpen(false)
            setSelectedPath(null)
            toast.success('Shared path deleted successfully')
        },
        onError: (error: any) => {
            toast.error(error.response?.data?.detail || 'Failed to delete path')
        }
    })

    const resetForm = () => {
        setFormData({ name: '', path: '', description: '', protocols: [], user_accesses: [] })
    }

    const openEditDialog = (path: SharedPath) => {
        setSelectedPath(path)
        setFormData({
            name: path.name,
            path: path.path,
            description: path.description || '',
            protocols: path.protocols || [],
            user_accesses: path.user_accesses?.map(ua => ({
                user_id: ua.user_id,
                permission: ua.permission
            })) || []
        })
        setIsEditOpen(true)
    }

    const openDeleteDialog = (path: SharedPath) => {
        setSelectedPath(path)
        setIsDeleteOpen(true)
    }

    const handleProtocolToggle = (protocolName: string) => {
        setFormData(prev => ({
            ...prev,
            protocols: prev.protocols.includes(protocolName)
                ? prev.protocols.filter(p => p !== protocolName)
                : [...prev.protocols, protocolName]
        }))
    }

    const handleUserPermissionChange = (userId: string, permission: string | null) => {
        setFormData(prev => {
            if (permission === null) {
                // Remove user access
                return {
                    ...prev,
                    user_accesses: prev.user_accesses.filter(ua => ua.user_id !== userId)
                }
            }

            const existing = prev.user_accesses.find(ua => ua.user_id === userId)
            if (existing) {
                return {
                    ...prev,
                    user_accesses: prev.user_accesses.map(ua =>
                        ua.user_id === userId ? { ...ua, permission } : ua
                    )
                }
            } else {
                return {
                    ...prev,
                    user_accesses: [...prev.user_accesses, { user_id: userId, permission }]
                }
            }
        })
    }

    const getUserPermission = (userId: string): string | null => {
        const access = formData.user_accesses.find(ua => ua.user_id === userId)
        return access?.permission || null
    }

    const handleCreate = () => {
        createMutation.mutate(formData)
    }

    const handleUpdate = () => {
        if (selectedPath) {
            updateMutation.mutate({ id: selectedPath.id, data: formData })
        }
    }

    const handleDelete = () => {
        if (selectedPath) {
            deleteMutation.mutate(selectedPath.id)
        }
    }

    const installedProtocols = protocols?.filter(p => p.status !== 'uninstalled') || []
    const nonAdminUsers = users?.filter(u => !u.is_admin) || []

    const renderUserAccessSection = () => (
        <div className="space-y-2">
            <label className="text-sm font-medium flex items-center gap-2">
                <Users className="w-4 h-4" />
                User Permissions
            </label>
            <div className="border rounded-lg divide-y max-h-48 overflow-y-auto">
                {nonAdminUsers.length > 0 ? nonAdminUsers.map(user => {
                    const currentPermission = getUserPermission(user.id)
                    return (
                        <div key={user.id} className="p-3 flex items-center justify-between">
                            <span className="text-sm font-medium">{user.username}</span>
                            <div className="flex items-center gap-1">
                                <Button
                                    type="button"
                                    size="sm"
                                    variant={currentPermission === 'read' ? 'default' : 'outline'}
                                    className="h-7 text-xs"
                                    onClick={() => handleUserPermissionChange(user.id, currentPermission === 'read' ? null : 'read')}
                                >
                                    <Eye className="w-3 h-3 mr-1" />
                                    Read
                                </Button>
                                <Button
                                    type="button"
                                    size="sm"
                                    variant={currentPermission === 'write' ? 'default' : 'outline'}
                                    className="h-7 text-xs"
                                    onClick={() => handleUserPermissionChange(user.id, currentPermission === 'write' ? null : 'write')}
                                >
                                    <Edit2 className="w-3 h-3 mr-1" />
                                    Write
                                </Button>
                                <Button
                                    type="button"
                                    size="sm"
                                    variant={currentPermission === 'full' ? 'default' : 'outline'}
                                    className="h-7 text-xs"
                                    onClick={() => handleUserPermissionChange(user.id, currentPermission === 'full' ? null : 'full')}
                                >
                                    <Shield className="w-3 h-3 mr-1" />
                                    Full
                                </Button>
                            </div>
                        </div>
                    )
                }) : (
                    <p className="p-3 text-sm text-muted-foreground">No non-admin users available. Create users first.</p>
                )}
            </div>
            <p className="text-xs text-muted-foreground">Admin users have full access to all paths automatically.</p>
        </div>
    )

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">Shared Paths</h1>
                    <p className="text-muted-foreground mt-1">
                        Configure shared directories and user access permissions
                    </p>
                </div>
                <Button onClick={() => { resetForm(); setIsCreateOpen(true) }}>
                    <Plus className="w-4 h-4 mr-2" />
                    Add Path
                </Button>
            </div>

            <Card>
                <CardHeader>
                    <div className="flex items-center gap-3">
                        <FolderOpen className="w-8 h-8 text-muted-foreground" />
                        <div>
                            <CardTitle>Configured Paths</CardTitle>
                            <CardDescription>
                                Directories shared via file transfer protocols
                            </CardDescription>
                        </div>
                    </div>
                </CardHeader>
                <CardContent>
                    {isLoading ? (
                        <div className="flex items-center justify-center py-8">
                            <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
                        </div>
                    ) : paths && paths.length > 0 ? (
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>Name</TableHead>
                                    <TableHead>Path</TableHead>
                                    <TableHead>Protocols</TableHead>
                                    <TableHead>User Access</TableHead>
                                    <TableHead className="text-right">Actions</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {paths.map((path) => (
                                    <TableRow key={path.id}>
                                        <TableCell className="font-medium">{path.name}</TableCell>
                                        <TableCell className="font-mono text-sm text-muted-foreground">
                                            {path.path}
                                        </TableCell>
                                        <TableCell>
                                            <div className="flex flex-wrap gap-1">
                                                {path.protocols?.map(p => (
                                                    <span key={p} className="px-2 py-0.5 bg-blue-100 text-blue-700 dark:bg-blue-900/20 dark:text-blue-400 rounded text-xs font-medium">
                                                        {p.toUpperCase()}
                                                    </span>
                                                ))}
                                            </div>
                                        </TableCell>
                                        <TableCell>
                                            <div className="flex flex-wrap gap-1">
                                                {path.user_accesses?.length > 0 ? path.user_accesses.map(ua => {
                                                    const permConfig = permissionLabels[ua.permission] || permissionLabels.read
                                                    return (
                                                        <span key={ua.user_id} className={`px-2 py-0.5 rounded text-xs font-medium ${permConfig.color}`}>
                                                            {ua.username}: {permConfig.label}
                                                        </span>
                                                    )
                                                }) : (
                                                    <span className="text-xs text-muted-foreground">No users</span>
                                                )}
                                            </div>
                                        </TableCell>
                                        <TableCell className="text-right">
                                            <div className="flex items-center justify-end gap-2">
                                                <Button
                                                    size="sm"
                                                    variant="ghost"
                                                    onClick={() => openEditDialog(path)}
                                                >
                                                    <Pencil className="w-4 h-4" />
                                                </Button>
                                                <Button
                                                    size="sm"
                                                    variant="ghost"
                                                    className="text-red-500 hover:text-red-700"
                                                    onClick={() => openDeleteDialog(path)}
                                                >
                                                    <Trash2 className="w-4 h-4" />
                                                </Button>
                                            </div>
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    ) : (
                        <div className="text-center py-12 text-muted-foreground">
                            <FolderOpen className="w-12 h-12 mx-auto mb-4 opacity-50" />
                            <p className="mb-2">No shared paths configured</p>
                            <p className="text-sm">Click "Add Path" to create your first shared directory</p>
                        </div>
                    )}
                </CardContent>
            </Card>

            {/* Create Dialog */}
            <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
                <DialogContent className="max-w-2xl">
                    <DialogHeader>
                        <DialogTitle>Add Shared Path</DialogTitle>
                        <DialogDescription>
                            Create a new shared directory with user access permissions
                        </DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4 py-4 max-h-[60vh] overflow-y-auto">
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <label className="text-sm font-medium">Name</label>
                                <Input
                                    placeholder="e.g., Public Files"
                                    value={formData.name}
                                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-sm font-medium">Path</label>
                                <Input
                                    placeholder="/opt/file-server/storage/public"
                                    value={formData.path}
                                    onChange={(e) => setFormData({ ...formData, path: e.target.value })}
                                />
                            </div>
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-medium">Description</label>
                            <Input
                                placeholder="Optional description"
                                value={formData.description}
                                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                            />
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-medium">Protocols</label>
                            <div className="grid grid-cols-3 gap-2">
                                {installedProtocols.length > 0 ? installedProtocols.map(protocol => (
                                    <div key={protocol.name} className="flex items-center space-x-2">
                                        <Checkbox
                                            id={`create-${protocol.name}`}
                                            checked={formData.protocols.includes(protocol.name)}
                                            onCheckedChange={() => handleProtocolToggle(protocol.name)}
                                        />
                                        <label htmlFor={`create-${protocol.name}`} className="text-sm">
                                            {protocol.display_name}
                                        </label>
                                    </div>
                                )) : (
                                    <p className="text-sm text-muted-foreground col-span-3">No protocols installed yet</p>
                                )}
                            </div>
                        </div>
                        {renderUserAccessSection()}
                    </div>
                    <DialogFooter>
                        <Button variant="outline" onClick={() => setIsCreateOpen(false)}>Cancel</Button>
                        <Button onClick={handleCreate} disabled={createMutation.isPending || !formData.name || !formData.path}>
                            {createMutation.isPending && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                            Create
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>

            {/* Edit Dialog */}
            <Dialog open={isEditOpen} onOpenChange={setIsEditOpen}>
                <DialogContent className="max-w-2xl">
                    <DialogHeader>
                        <DialogTitle>Edit Shared Path</DialogTitle>
                        <DialogDescription>
                            Update path configuration and user access permissions
                        </DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4 py-4 max-h-[60vh] overflow-y-auto">
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <label className="text-sm font-medium">Name</label>
                                <Input
                                    value={formData.name}
                                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-sm font-medium">Path</label>
                                <Input
                                    value={formData.path}
                                    onChange={(e) => setFormData({ ...formData, path: e.target.value })}
                                />
                            </div>
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-medium">Description</label>
                            <Input
                                value={formData.description}
                                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                            />
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-medium">Protocols</label>
                            <div className="grid grid-cols-3 gap-2">
                                {installedProtocols.map(protocol => (
                                    <div key={protocol.name} className="flex items-center space-x-2">
                                        <Checkbox
                                            id={`edit-${protocol.name}`}
                                            checked={formData.protocols.includes(protocol.name)}
                                            onCheckedChange={() => handleProtocolToggle(protocol.name)}
                                        />
                                        <label htmlFor={`edit-${protocol.name}`} className="text-sm">
                                            {protocol.display_name}
                                        </label>
                                    </div>
                                ))}
                            </div>
                        </div>
                        {renderUserAccessSection()}
                    </div>
                    <DialogFooter>
                        <Button variant="outline" onClick={() => setIsEditOpen(false)}>Cancel</Button>
                        <Button onClick={handleUpdate} disabled={updateMutation.isPending}>
                            {updateMutation.isPending && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                            Save Changes
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>

            {/* Delete Dialog */}
            <Dialog open={isDeleteOpen} onOpenChange={setIsDeleteOpen}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Delete Shared Path</DialogTitle>
                        <DialogDescription>
                            Are you sure you want to delete "{selectedPath?.name}"? This action cannot be undone.
                            <br /><br />
                            <strong>Note:</strong> This only removes the path configuration and user permissions. The actual directory and files will not be deleted.
                        </DialogDescription>
                    </DialogHeader>
                    <DialogFooter>
                        <Button variant="outline" onClick={() => setIsDeleteOpen(false)}>Cancel</Button>
                        <Button variant="destructive" onClick={handleDelete} disabled={deleteMutation.isPending}>
                            {deleteMutation.isPending && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                            Delete
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    )
}

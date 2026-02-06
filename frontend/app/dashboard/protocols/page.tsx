'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { protocolsAPI } from '@/lib/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '@/components/ui/table'
import {
    Play,
    Square,
    Download,
    Trash2,
    RefreshCw,
    CheckCircle2,
    XCircle,
    Loader2
} from 'lucide-react'

export default function ProtocolsPage() {
    const queryClient = useQueryClient()
    const [loadingAction, setLoadingAction] = useState<{ protocol: string, action: string } | null>(null)

    const { data: protocols, isLoading } = useQuery({
        queryKey: ['protocols'],
        queryFn: async () => {
            const { data } = await protocolsAPI.list()
            return data
        },
        refetchInterval: 5000, // Auto-refresh every 5s
    })

    const installMutation = useMutation({
        mutationFn: (protocolName: string) => protocolsAPI.install(protocolName),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['protocols'] })
        },
    })

    const startMutation = useMutation({
        mutationFn: (protocolName: string) => protocolsAPI.start(protocolName),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['protocols'] })
        },
    })

    const stopMutation = useMutation({
        mutationFn: (protocolName: string) => protocolsAPI.stop(protocolName),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['protocols'] })
        },
    })

    const handleAction = async (protocolName: string, action: 'install' | 'start' | 'stop') => {
        setLoadingAction({ protocol: protocolName, action })

        try {
            if (action === 'install') {
                await installMutation.mutateAsync(protocolName)
            } else if (action === 'start') {
                await startMutation.mutateAsync(protocolName)
            } else if (action === 'stop') {
                await stopMutation.mutateAsync(protocolName)
            }
        } catch (error: any) {
            alert(error.response?.data?.detail || `Failed to ${action} ${protocolName}`)
        } finally {
            setLoadingAction(null)
        }
    }

    const getStatusBadge = (status: string) => {
        const statusConfig = {
            running: { color: 'bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-400', icon: CheckCircle2 },
            stopped: { color: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/20 dark:text-yellow-400', icon: CheckCircle2 },
            installing: { color: 'bg-blue-100 text-blue-700 dark:bg-blue-900/20 dark:text-blue-400', icon: RefreshCw },
            uninstalled: { color: 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400', icon: XCircle },
            error: { color: 'bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-400', icon: XCircle },
        }

        const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.uninstalled
        const Icon = config.icon

        return (
            <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${config.color}`}>
                <Icon className="w-3.5 h-3.5" />
                <span className="capitalize">{status.replace('_', ' ')}</span>
            </div>
        )
    }

    const isActionLoading = (protocolName: string, action: string) => {
        return loadingAction?.protocol === protocolName && loadingAction?.action === action
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
                    <h1 className="text-3xl font-bold">Protocols</h1>
                    <p className="text-muted-foreground mt-1">
                        Install and manage file sharing protocols
                    </p>
                </div>
                <Button
                    variant="outline"
                    onClick={() => queryClient.invalidateQueries({ queryKey: ['protocols'] })}
                >
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Refresh
                </Button>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>Available Protocols</CardTitle>
                    <CardDescription>
                        Install, configure and manage multiple file server protocols
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>Protocol</TableHead>
                                <TableHead>Description</TableHead>
                                <TableHead>Port</TableHead>
                                <TableHead>Status</TableHead>
                                <TableHead className="text-right">Actions</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {protocols?.map((protocol: any) => (
                                <TableRow key={protocol.name}>
                                    <TableCell className="font-medium">
                                        {protocol.name.toUpperCase()}
                                    </TableCell>
                                    <TableCell className="text-muted-foreground max-w-xs truncate">
                                        {protocol.description}
                                    </TableCell>
                                    <TableCell>
                                        {protocol.default_port || 'N/A'}
                                    </TableCell>
                                    <TableCell>
                                        {getStatusBadge(protocol.status)}
                                    </TableCell>
                                    <TableCell className="text-right">
                                        <div className="flex items-center justify-end gap-2">
                                            {protocol.status === 'uninstalled' && (
                                                <Button
                                                    size="sm"
                                                    variant="outline"
                                                    onClick={() => handleAction(protocol.name, 'install')}
                                                    disabled={isActionLoading(protocol.name, 'install')}
                                                >
                                                    {isActionLoading(protocol.name, 'install') ? (
                                                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                                    ) : (
                                                        <Download className="w-4 h-4 mr-2" />
                                                    )}
                                                    Install
                                                </Button>
                                            )}

                                            {protocol.status === 'stopped' && (
                                                <Button
                                                    size="sm"
                                                    variant="outline"
                                                    onClick={() => handleAction(protocol.name, 'start')}
                                                    disabled={isActionLoading(protocol.name, 'start')}
                                                >
                                                    {isActionLoading(protocol.name, 'start') ? (
                                                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                                    ) : (
                                                        <Play className="w-4 h-4 mr-2" />
                                                    )}
                                                    Start
                                                </Button>
                                            )}

                                            {protocol.status === 'running' && (
                                                <Button
                                                    size="sm"
                                                    variant="outline"
                                                    onClick={() => handleAction(protocol.name, 'stop')}
                                                    disabled={isActionLoading(protocol.name, 'stop')}
                                                >
                                                    {isActionLoading(protocol.name, 'stop') ? (
                                                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                                    ) : (
                                                        <Square className="w-4 h-4 mr-2" />
                                                    )}
                                                    Stop
                                                </Button>
                                            )}
                                        </div>
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </CardContent>
            </Card>

            {/* Implementation Status Info */}
            <Card>
                <CardHeader>
                    <CardTitle>Implementation Status</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                        <div>
                            <p className="font-medium mb-2 text-green-600">✅ Fully Implemented:</p>
                            <ul className="space-y-1 text-muted-foreground">
                                <li>• FTP/FTPS (vsftpd / IIS)</li>
                                <li>• SFTP (OpenSSH)</li>
                                <li>• SMB/CIFS (Samba)</li>
                                <li>• S3 (MinIO)</li>
                            </ul>
                        </div>
                        <div>
                            <p className="font-medium mb-2 text-yellow-600">⚠️ Stub/Pending:</p>
                            <ul className="space-y-1 text-muted-foreground">
                                <li>• NFS</li>
                                <li>• WebDAV</li>
                                <li>• NextCloud</li>
                            </ul>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    )
}

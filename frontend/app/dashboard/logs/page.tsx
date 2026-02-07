'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { logsAPI, usersAPI, protocolsAPI } from '@/lib/api'
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
    Activity,
    Server,
    Loader2,
    RefreshCw,
    Filter,
    CheckCircle2,
    XCircle,
    AlertCircle,
    FileText,
    Download,
    Upload,
    LogIn,
    LogOut,
    Folder,
    Trash2
} from 'lucide-react'

interface AccessLog {
    id: string
    user_id: string | null
    username: string | null
    protocol: string
    action: string
    file_path: string | null
    ip_address: string | null
    status: string
    error_message: string | null
    file_size_bytes: number | null
    timestamp: string
}

const actionIcons: Record<string, any> = {
    login: LogIn,
    logout: LogOut,
    upload: Upload,
    download: Download,
    delete: Trash2,
    mkdir: Folder,
    rmdir: Folder,
    list: FileText,
}

const statusColors: Record<string, { bg: string; text: string; icon: any }> = {
    success: { bg: 'bg-green-100 dark:bg-green-900/20', text: 'text-green-700 dark:text-green-400', icon: CheckCircle2 },
    failed: { bg: 'bg-red-100 dark:bg-red-900/20', text: 'text-red-700 dark:text-red-400', icon: XCircle },
    denied: { bg: 'bg-yellow-100 dark:bg-yellow-900/20', text: 'text-yellow-700 dark:text-yellow-400', icon: AlertCircle },
}

export default function LogsPage() {
    const [activeTab, setActiveTab] = useState<'access' | 'services'>('access')
    const [selectedService, setSelectedService] = useState('api')
    const [filters, setFilters] = useState({
        protocol: '',
        action: '',
        status: ''
    })
    const [showFilters, setShowFilters] = useState(false)

    // Access logs query
    const { data: accessLogs, isLoading: logsLoading, refetch: refetchLogs } = useQuery({
        queryKey: ['accessLogs', filters],
        queryFn: async () => {
            const params: any = { limit: 100 }
            if (filters.protocol) params.protocol = filters.protocol
            if (filters.action) params.action = filters.action
            if (filters.status) params.status = filters.status
            const res = await logsAPI.getAccessLogs(params)
            return res.data as AccessLog[]
        },
        enabled: activeTab === 'access'
    })

    // Access stats query
    const { data: stats } = useQuery({
        queryKey: ['accessStats'],
        queryFn: async () => {
            const res = await logsAPI.getStats(7)
            return res.data
        },
        enabled: activeTab === 'access'
    })

    // Service logs query
    const { data: serviceLogs, isLoading: serviceLogsLoading, refetch: refetchServiceLogs } = useQuery({
        queryKey: ['serviceLogs', selectedService],
        queryFn: async () => {
            const res = await logsAPI.getServiceLogs(selectedService, 100)
            return res.data
        },
        enabled: activeTab === 'services'
    })

    // Services status query
    const { data: servicesStatus } = useQuery({
        queryKey: ['servicesStatus'],
        queryFn: async () => {
            const res = await logsAPI.getServicesStatus()
            return res.data
        },
        enabled: activeTab === 'services'
    })

    const services = [
        { id: 'api', name: 'File Server API', service: 'fileserver-api' },
        { id: 'ftp', name: 'FTP Server', service: 'vsftpd' },
        { id: 'sftp', name: 'SFTP Server', service: 'sshd' },
        { id: 'smb', name: 'SMB Server', service: 'smbd' },
        { id: 's3', name: 'S3 (MinIO)', service: 'minio' },
    ]

    const formatTimestamp = (ts: string) => {
        const date = new Date(ts)
        return date.toLocaleString()
    }

    const formatBytes = (bytes: number | null) => {
        if (bytes === null || bytes === 0) return '-'
        const k = 1024
        const sizes = ['B', 'KB', 'MB', 'GB']
        const i = Math.floor(Math.log(bytes) / Math.log(k))
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">Activity Logs</h1>
                    <p className="text-muted-foreground mt-1">
                        Monitor access logs and service status
                    </p>
                </div>
                <Button
                    variant="outline"
                    onClick={() => activeTab === 'access' ? refetchLogs() : refetchServiceLogs()}
                >
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Refresh
                </Button>
            </div>

            {/* Tab Navigation */}
            <div className="flex gap-2">
                <Button
                    variant={activeTab === 'access' ? 'default' : 'outline'}
                    onClick={() => setActiveTab('access')}
                >
                    <Activity className="w-4 h-4 mr-2" />
                    Access Logs
                </Button>
                <Button
                    variant={activeTab === 'services' ? 'default' : 'outline'}
                    onClick={() => setActiveTab('services')}
                >
                    <Server className="w-4 h-4 mr-2" />
                    Service Logs
                </Button>
            </div>

            {/* Access Logs Tab */}
            {activeTab === 'access' && (
                <>
                    {/* Stats Cards */}
                    {stats && (
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            <Card>
                                <CardContent className="pt-6">
                                    <div className="text-2xl font-bold">{stats.total}</div>
                                    <p className="text-xs text-muted-foreground">Total Events (7d)</p>
                                </CardContent>
                            </Card>
                            <Card>
                                <CardContent className="pt-6">
                                    <div className="text-2xl font-bold text-green-600">{stats.success}</div>
                                    <p className="text-xs text-muted-foreground">Successful</p>
                                </CardContent>
                            </Card>
                            <Card>
                                <CardContent className="pt-6">
                                    <div className="text-2xl font-bold text-red-600">{stats.failed}</div>
                                    <p className="text-xs text-muted-foreground">Failed</p>
                                </CardContent>
                            </Card>
                            <Card>
                                <CardContent className="pt-6">
                                    <div className="text-2xl font-bold text-yellow-600">{stats.denied}</div>
                                    <p className="text-xs text-muted-foreground">Denied</p>
                                </CardContent>
                            </Card>
                        </div>
                    )}

                    {/* Filters */}
                    <div className="flex gap-2">
                        <Button variant="outline" size="sm" onClick={() => setShowFilters(!showFilters)}>
                            <Filter className="w-4 h-4 mr-2" />
                            Filters
                        </Button>
                        {showFilters && (
                            <div className="flex gap-2">
                                <select
                                    className="border rounded px-2 py-1 text-sm bg-background"
                                    value={filters.protocol}
                                    onChange={(e) => setFilters({ ...filters, protocol: e.target.value })}
                                >
                                    <option value="">All Protocols</option>
                                    <option value="ftp">FTP</option>
                                    <option value="sftp">SFTP</option>
                                    <option value="smb">SMB</option>
                                    <option value="s3">S3</option>
                                    <option value="web">Web</option>
                                </select>
                                <select
                                    className="border rounded px-2 py-1 text-sm bg-background"
                                    value={filters.action}
                                    onChange={(e) => setFilters({ ...filters, action: e.target.value })}
                                >
                                    <option value="">All Actions</option>
                                    <option value="login">Login</option>
                                    <option value="logout">Logout</option>
                                    <option value="upload">Upload</option>
                                    <option value="download">Download</option>
                                    <option value="delete">Delete</option>
                                    <option value="list">List</option>
                                </select>
                                <select
                                    className="border rounded px-2 py-1 text-sm bg-background"
                                    value={filters.status}
                                    onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                                >
                                    <option value="">All Status</option>
                                    <option value="success">Success</option>
                                    <option value="failed">Failed</option>
                                    <option value="denied">Denied</option>
                                </select>
                                <Button variant="ghost" size="sm" onClick={() => setFilters({ protocol: '', action: '', status: '' })}>
                                    Clear
                                </Button>
                            </div>
                        )}
                    </div>

                    {/* Logs Table */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Recent Activity</CardTitle>
                            <CardDescription>User access and file operation logs</CardDescription>
                        </CardHeader>
                        <CardContent>
                            {logsLoading ? (
                                <div className="flex items-center justify-center py-8">
                                    <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
                                </div>
                            ) : accessLogs && accessLogs.length > 0 ? (
                                <Table>
                                    <TableHeader>
                                        <TableRow>
                                            <TableHead>Time</TableHead>
                                            <TableHead>User</TableHead>
                                            <TableHead>Protocol</TableHead>
                                            <TableHead>Action</TableHead>
                                            <TableHead>Path</TableHead>
                                            <TableHead>Size</TableHead>
                                            <TableHead>Status</TableHead>
                                            <TableHead>IP</TableHead>
                                        </TableRow>
                                    </TableHeader>
                                    <TableBody>
                                        {accessLogs.map((log) => {
                                            const ActionIcon = actionIcons[log.action] || Activity
                                            const statusConfig = statusColors[log.status] || statusColors.success
                                            const StatusIcon = statusConfig.icon
                                            return (
                                                <TableRow key={log.id}>
                                                    <TableCell className="text-xs text-muted-foreground whitespace-nowrap">
                                                        {formatTimestamp(log.timestamp)}
                                                    </TableCell>
                                                    <TableCell className="font-medium">
                                                        {log.username || '-'}
                                                    </TableCell>
                                                    <TableCell>
                                                        <span className="px-2 py-0.5 bg-blue-100 text-blue-700 dark:bg-blue-900/20 dark:text-blue-400 rounded text-xs font-medium">
                                                            {log.protocol.toUpperCase()}
                                                        </span>
                                                    </TableCell>
                                                    <TableCell>
                                                        <div className="flex items-center gap-1.5">
                                                            <ActionIcon className="w-3.5 h-3.5" />
                                                            <span className="capitalize">{log.action}</span>
                                                        </div>
                                                    </TableCell>
                                                    <TableCell className="max-w-xs truncate text-xs text-muted-foreground font-mono">
                                                        {log.file_path || '-'}
                                                    </TableCell>
                                                    <TableCell className="text-xs">
                                                        {formatBytes(log.file_size_bytes)}
                                                    </TableCell>
                                                    <TableCell>
                                                        <div className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium ${statusConfig.bg} ${statusConfig.text}`}>
                                                            <StatusIcon className="w-3 h-3" />
                                                            {log.status}
                                                        </div>
                                                    </TableCell>
                                                    <TableCell className="text-xs text-muted-foreground">
                                                        {log.ip_address || '-'}
                                                    </TableCell>
                                                </TableRow>
                                            )
                                        })}
                                    </TableBody>
                                </Table>
                            ) : (
                                <div className="text-center py-12 text-muted-foreground">
                                    <Activity className="w-12 h-12 mx-auto mb-4 opacity-50" />
                                    <p>No access logs yet</p>
                                    <p className="text-sm mt-1">Logs will appear here when users access files</p>
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </>
            )}

            {/* Service Logs Tab */}
            {activeTab === 'services' && (
                <>
                    {/* Service Selector */}
                    <div className="flex gap-2 flex-wrap">
                        {services.map((svc) => {
                            const status = servicesStatus?.[svc.service]
                            const isActive = status === 'active'
                            return (
                                <Button
                                    key={svc.id}
                                    variant={selectedService === svc.id ? 'default' : 'outline'}
                                    size="sm"
                                    onClick={() => setSelectedService(svc.id)}
                                    className="relative"
                                >
                                    <span className={`absolute -top-1 -right-1 w-2 h-2 rounded-full ${isActive ? 'bg-green-500' : status === 'inactive' ? 'bg-gray-400' : 'bg-yellow-500'}`} />
                                    {svc.name}
                                </Button>
                            )
                        })}
                    </div>

                    {/* Service Log Viewer */}
                    <Card>
                        <CardHeader>
                            <CardTitle>
                                {services.find(s => s.id === selectedService)?.name} Logs
                            </CardTitle>
                            <CardDescription>
                                System journal logs for {services.find(s => s.id === selectedService)?.service}
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            {serviceLogsLoading ? (
                                <div className="flex items-center justify-center py-8">
                                    <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
                                </div>
                            ) : serviceLogs?.lines ? (
                                <div className="bg-gray-900 text-gray-100 rounded-lg p-4 font-mono text-xs max-h-[500px] overflow-auto">
                                    {serviceLogs.lines.map((line: string, i: number) => (
                                        <div key={i} className="whitespace-pre-wrap hover:bg-gray-800 px-1">
                                            {line}
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <div className="text-center py-12 text-muted-foreground">
                                    <Server className="w-12 h-12 mx-auto mb-4 opacity-50" />
                                    <p>No logs available</p>
                                    <p className="text-sm mt-1">{serviceLogs?.error || 'Service may not be running'}</p>
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </>
            )}
        </div>
    )
}

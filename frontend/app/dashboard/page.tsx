'use client'

import { useQuery } from '@tanstack/react-query'
import { protocolsAPI, usersAPI } from '@/lib/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Server, Users, HardDrive, Activity } from 'lucide-react'
import { formatBytes, formatPercentage } from '@/lib/utils'

export default function DashboardPage() {
    const { data: protocols } = useQuery({
        queryKey: ['protocols'],
        queryFn: async () => {
            const { data } = await protocolsAPI.list()
            return data
        },
    })

    const { data: users } = useQuery({
        queryKey: ['users'],
        queryFn: async () => {
            const { data } = await usersAPI.list()
            return data
        },
    })

    const installedCount = protocols?.filter((p: any) => p.status === 'installed' || p.status === 'running')?.length || 0
    const runningCount = protocols?.filter((p: any) => p.status === 'running')?.length || 0
    const totalUsers = users?.length || 0
    const activeUsers = users?.filter((u: any) => u.is_active)?.length || 0

    const stats = [
        {
            title: 'Protocols Installed',
            value: installedCount,
            total: protocols?.length || 0,
            icon: Server,
            color: 'text-blue-600',
            bgColor: 'bg-blue-100 dark:bg-blue-900/20',
        },
        {
            title: 'Services Running',
            value: runningCount,
            total: installedCount,
            icon: Activity,
            color: 'text-green-600',
            bgColor: 'bg-green-100 dark:bg-green-900/20',
        },
        {
            title: 'Total Users',
            value: activeUsers,
            total: totalUsers,
            icon: Users,
            color: 'text-purple-600',
            bgColor: 'bg-purple-100 dark:bg-purple-900/20',
        },
        {
            title: 'Storage Used',
            value: '0 GB',
            total: '∞',
            icon: HardDrive,
            color: 'text-orange-600',
            bgColor: 'bg-orange-100 dark:bg-orange-900/20',
        },
    ]

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold">Dashboard</h1>
                <p className="text-muted-foreground mt-1">
                    Overview of your file server management system
                </p>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {stats.map((stat) => {
                    const Icon = stat.icon
                    return (
                        <Card key={stat.title}>
                            <CardHeader className="flex flex-row items-center justify-between pb-2">
                                <CardTitle className="text-sm font-medium text-muted-foreground">
                                    {stat.title}
                                </CardTitle>
                                <div className={`p-2 rounded-lg ${stat.bgColor}`}>
                                    <Icon className={`w-5 h-5 ${stat.color}`} />
                                </div>
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">
                                    {stat.value} <span className="text-sm text-muted-foreground">/ {stat.total}</span>
                                </div>
                            </CardContent>
                        </Card>
                    )
                })}
            </div>

            {/* Protocols Status */}
            <Card>
                <CardHeader>
                    <CardTitle>Protocol Status</CardTitle>
                    <CardDescription>Current state of all supported protocols</CardDescription>
                </CardHeader>
                <CardContent>
                    {protocols?.length > 0 ? (
                        <div className="space-y-3">
                            {protocols.map((protocol: any) => (
                                <div
                                    key={protocol.name}
                                    className="flex items-center justify-between p-3 rounded-lg border"
                                >
                                    <div className="flex items-center gap-3">
                                        <div
                                            className={`w-2 h-2 rounded-full ${protocol.status === 'running'
                                                    ? 'bg-green-500'
                                                    : protocol.status === 'installed'
                                                        ? 'bg-yellow-500'
                                                        : 'bg-gray-300'
                                                }`}
                                        />
                                        <div>
                                            <p className="font-medium">{protocol.name.toUpperCase()}</p>
                                            <p className="text-xs text-muted-foreground">
                                                {protocol.description}
                                            </p>
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-sm font-medium capitalize">{protocol.status}</p>
                                        {protocol.default_port && (
                                            <p className="text-xs text-muted-foreground">
                                                Port {protocol.default_port}
                                            </p>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="text-center py-8 text-muted-foreground">
                            No protocols available
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    )
}

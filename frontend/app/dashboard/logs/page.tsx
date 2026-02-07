'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ScrollText } from 'lucide-react'

export default function LogsPage() {
    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold">Logs & Audit Trail</h1>
                <p className="text-muted-foreground mt-1">
                    View access logs and system activity
                </p>
            </div>

            <Card>
                <CardHeader>
                    <div className="flex items-center gap-3">
                        <ScrollText className="w-8 h-8 text-muted-foreground" />
                        <div>
                            <CardTitle>Activity Logs</CardTitle>
                            <CardDescription>This feature is under development</CardDescription>
                        </div>
                    </div>
                </CardHeader>
                <CardContent>
                    <div className="text-center py-12 text-muted-foreground">
                        <p className="mb-2">Log viewing coming soon!</p>
                        <p className="text-sm">Track user access and system events.</p>
                    </div>
                </CardContent>
            </Card>
        </div>
    )
}

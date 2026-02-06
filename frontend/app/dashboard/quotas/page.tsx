'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Database } from 'lucide-react'

export default function QuotasPage() {
    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold">Quotas & Usage</h1>
                <p className="text-muted-foreground mt-1">
                    Monitor storage usage and manage user quotas
                </p>
            </div>

            <Card>
                <CardHeader>
                    <div className="flex items-center gap-3">
                        <Database className="w-8 h-8 text-muted-foreground" />
                        <div>
                            <CardTitle>Quota Management</CardTitle>
                            <CardDescription>This feature is under development</CardDescription>
                        </div>
                    </div>
                </CardHeader>
                <CardContent>
                    <div className="text-center py-12 text-muted-foreground">
                        <p className="mb-2">Quota tracking coming soon!</p>
                        <p className="text-sm">Monitor user storage usage and set limits.</p>
                    </div>
                </CardContent>
            </Card>
        </div>
    )
}

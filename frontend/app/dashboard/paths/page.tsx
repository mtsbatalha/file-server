'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { FolderOpen } from 'lucide-react'

export default function PathsPage() {
    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold">Shared Paths</h1>
                <p className="text-muted-foreground mt-1">
                    Configure shared directories and access permissions
                </p>
            </div>

            <Card>
                <CardHeader>
                    <div className="flex items-center gap-3">
                        <FolderOpen className="w-8 h-8 text-muted-foreground" />
                        <div>
                            <CardTitle>Path Management</CardTitle>
                            <CardDescription>This feature is under development</CardDescription>
                        </div>
                    </div>
                </CardHeader>
                <CardContent>
                    <div className="text-center py-12 text-muted-foreground">
                        <p className="mb-2">Shared paths management coming soon!</p>
                        <p className="text-sm">Configure which directories are shared via each protocol.</p>
                    </div>
                </CardContent>
            </Card>
        </div>
    )
}

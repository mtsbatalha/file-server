'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Settings } from 'lucide-react'

export default function SettingsPage() {
    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold">Settings</h1>
                <p className="text-muted-foreground mt-1">
                    Configure system settings and preferences
                </p>
            </div>

            <Card>
                <CardHeader>
                    <div className="flex items-center gap-3">
                        <Settings className="w-8 h-8 text-muted-foreground" />
                        <div>
                            <CardTitle>System Settings</CardTitle>
                            <CardDescription>This feature is under development</CardDescription>
                        </div>
                    </div>
                </CardHeader>
                <CardContent>
                    <div className="text-center py-12 text-muted-foreground">
                        <p className="mb-2">Settings page coming soon!</p>
                        <p className="text-sm">Configure SSL, firewall, and system preferences.</p>
                    </div>
                </CardContent>
            </Card>
        </div>
    )
}

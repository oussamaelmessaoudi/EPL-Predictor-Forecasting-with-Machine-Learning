"use client"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import useSWR from "swr"

const fetcher = (url: string) => fetch(url).then((res) => res.json())

interface TeamDetailsPanelProps {
  teamName: string
}

export function TeamDetailsPanel({ teamName }: TeamDetailsPanelProps) {
  const { data: teamData, isLoading } = useSWR(`/api/v1/teams/${teamName}`, fetcher)

  if (isLoading) {
    return (
      <Card>
        <CardContent className="pt-6">
          <p className="text-muted-foreground">Loading team details...</p>
        </CardContent>
      </Card>
    )
  }

  if (!teamData) {
    return (
      <Card>
        <CardContent className="pt-6">
          <p className="text-muted-foreground">Team data not available</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>{teamName}</CardTitle>
          <CardDescription>Detailed performance metrics and analysis</CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="stats" className="w-full">
            <TabsList>
              <TabsTrigger value="stats">Statistics</TabsTrigger>
              <TabsTrigger value="features">Features</TabsTrigger>
              <TabsTrigger value="history">History</TabsTrigger>
            </TabsList>

            <TabsContent value="stats" className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <p className="text-sm font-semibold text-muted-foreground">Avg XG</p>
                  <p className="text-2xl font-bold">{teamData.avg_xg?.toFixed(2) || "N/A"}</p>
                </div>
                <div className="space-y-2">
                  <p className="text-sm font-semibold text-muted-foreground">Avg Goals</p>
                  <p className="text-2xl font-bold">{teamData.avg_goals?.toFixed(2) || "N/A"}</p>
                </div>
                <div className="space-y-2">
                  <p className="text-sm font-semibold text-muted-foreground">Win Ratio</p>
                  <p className="text-2xl font-bold">{teamData.win_ratio?.toFixed(2) || "N/A"}</p>
                </div>
                <div className="space-y-2">
                  <p className="text-sm font-semibold text-muted-foreground">Squad Depth</p>
                  <p className="text-2xl font-bold">{teamData.squad_depth || "N/A"}</p>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="features">
              <p className="text-muted-foreground">Feature importance and model insights coming soon</p>
            </TabsContent>

            <TabsContent value="history">
              <p className="text-muted-foreground">Historical predictions and seasonal trends coming soon</p>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  )
}

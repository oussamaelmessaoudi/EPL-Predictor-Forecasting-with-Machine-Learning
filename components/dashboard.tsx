"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { PredictionsTable } from "./predictions-table"
import { PredictionsChart } from "./predictions-chart"
import { TeamDetailsPanel } from "./team-details-panel"
import { RealTimeMetrics } from "./real-time-metrics"
import { ModelPerformance } from "./model-performance"
import useSWR from "swr"

const fetcher = (url: string) => fetch(url).then((res) => res.json())

export function Dashboard() {
  const [selectedTeam, setSelectedTeam] = useState<string | null>(null)
  const { data: predictions, isLoading: predictionsLoading } = useSWR("/api/v1/predictions/current-season", fetcher, {
    refreshInterval: 30000,
  })
  const { data: metrics } = useSWR("/api/v1/analytics/metrics", fetcher, { refreshInterval: 60000 })

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-4xl font-bold text-foreground mb-2">Premier League Top 6 Predictions</h1>
          <p className="text-muted-foreground">Real-time ML predictions powered by big data analytics</p>
        </div>

        {/* Real-time metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <RealTimeMetrics metrics={metrics} />
        </div>

        {/* Main content tabs */}
        <Tabs defaultValue="predictions" className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="predictions">Predictions</TabsTrigger>
            <TabsTrigger value="analysis">Analysis</TabsTrigger>
            <TabsTrigger value="team-details">Team Details</TabsTrigger>
            <TabsTrigger value="model">Model Performance</TabsTrigger>
          </TabsList>

          <TabsContent value="predictions" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Current Season Predictions</CardTitle>
                <CardDescription>Top 6 predictions with confidence scores</CardDescription>
              </CardHeader>
              <CardContent>
                <PredictionsTable
                  data={predictions?.predictions || []}
                  isLoading={predictionsLoading}
                  onTeamSelect={setSelectedTeam}
                />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="analysis" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Predictions Analysis</CardTitle>
                <CardDescription>Visualization of prediction probabilities</CardDescription>
              </CardHeader>
              <CardContent>
                <PredictionsChart data={predictions?.predictions || []} />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="team-details" className="space-y-4">
            {selectedTeam ? (
              <TeamDetailsPanel teamName={selectedTeam} />
            ) : (
              <Card>
                <CardContent className="pt-6">
                  <p className="text-muted-foreground">Select a team from the predictions table</p>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="model" className="space-y-4">
            <ModelPerformance />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}

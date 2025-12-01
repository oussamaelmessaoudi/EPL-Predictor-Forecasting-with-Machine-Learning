"use client"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface Metrics {
  total_predictions?: number
  active_teams?: number
  avg_accuracy?: number
  last_updated?: string
}

interface RealTimeMetricsProps {
  metrics?: Metrics
}

export function RealTimeMetrics({ metrics }: RealTimeMetricsProps) {
  const metricCards = [
    {
      title: "Total Predictions",
      value: metrics?.total_predictions || 0,
      description: "Current season",
    },
    {
      title: "Active Teams",
      value: metrics?.active_teams || 20,
      description: "In analysis",
    },
    {
      title: "Model Accuracy",
      value: `${(metrics?.avg_accuracy || 0.75 * 100).toFixed(1)}%`,
      description: "Last evaluation",
    },
    {
      title: "Last Updated",
      value: metrics?.last_updated ? new Date(metrics.last_updated).toLocaleTimeString() : "N/A",
      description: "Real-time sync",
    },
  ]

  return (
    <>
      {metricCards.map((card, index) => (
        <Card key={index}>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">{card.title}</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{card.value}</p>
            <p className="text-xs text-muted-foreground mt-1">{card.description}</p>
          </CardContent>
        </Card>
      ))}
    </>
  )
}

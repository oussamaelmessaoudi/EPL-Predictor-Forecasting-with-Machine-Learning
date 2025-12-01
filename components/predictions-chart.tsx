"use client"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts"
import { ChartContainer } from "@/components/ui/chart"

interface Prediction {
  team: string
  probability: number
}

interface PredictionsChartProps {
  data: Prediction[]
}

export function PredictionsChart({ data }: PredictionsChartProps) {
  const chartData = data.map((item) => ({
    name: item.team,
    probability: Math.round(item.probability * 100),
  }))

  const colors = [
    "hsl(var(--chart-1))",
    "hsl(var(--chart-2))",
    "hsl(var(--chart-3))",
    "hsl(var(--chart-4))",
    "hsl(var(--chart-5))",
  ]

  return (
    <ChartContainer
      config={{
        probability: {
          label: "Prediction Probability (%)",
          color: "hsl(var(--chart-1))",
        },
      }}
      className="h-80"
    >
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
          <YAxis domain={[0, 100]} />
          <Tooltip
            formatter={(value) => `${value}%`}
            contentStyle={{ backgroundColor: "hsl(var(--background))", border: "1px solid hsl(var(--border))" }}
          />
          <Bar dataKey="probability" radius={[8, 8, 0, 0]}>
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </ChartContainer>
  )
}

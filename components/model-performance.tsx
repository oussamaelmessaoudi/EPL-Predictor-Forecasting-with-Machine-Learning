"use client"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts"
import { ChartContainer } from "@/components/ui/chart"

export function ModelPerformance() {
  // Mock data for model performance over time
  const performanceData = [
    { epoch: 1, accuracy: 0.72, auc: 0.68, loss: 0.55 },
    { epoch: 2, accuracy: 0.74, auc: 0.71, loss: 0.48 },
    { epoch: 3, accuracy: 0.76, auc: 0.74, loss: 0.42 },
    { epoch: 4, accuracy: 0.78, auc: 0.77, loss: 0.38 },
    { epoch: 5, accuracy: 0.79, auc: 0.79, loss: 0.35 },
  ]

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Model Training Performance</CardTitle>
          <CardDescription>Metrics across training epochs</CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="metrics" className="w-full">
            <TabsList>
              <TabsTrigger value="metrics">Training Metrics</TabsTrigger>
              <TabsTrigger value="comparison">Model Comparison</TabsTrigger>
              <TabsTrigger value="logs">Training Logs</TabsTrigger>
            </TabsList>

            <TabsContent value="metrics" className="pt-4">
              <ChartContainer
                config={{
                  accuracy: {
                    label: "Accuracy",
                    color: "hsl(var(--chart-1))",
                  },
                  auc: {
                    label: "AUC",
                    color: "hsl(var(--chart-2))",
                  },
                  loss: {
                    label: "Loss",
                    color: "hsl(var(--chart-3))",
                  },
                }}
                className="h-80"
              >
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={performanceData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="epoch" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="accuracy" stroke="var(--color-accuracy)" />
                    <Line type="monotone" dataKey="auc" stroke="var(--color-auc)" />
                    <Line type="monotone" dataKey="loss" stroke="var(--color-loss)" />
                  </LineChart>
                </ResponsiveContainer>
              </ChartContainer>
            </TabsContent>

            <TabsContent value="comparison">
              <div className="space-y-4">
                <div className="grid grid-cols-3 gap-4">
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm">Random Forest</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-2xl font-bold">0.79</p>
                      <p className="text-xs text-muted-foreground">Accuracy</p>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm">XGBoost</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-2xl font-bold">0.77</p>
                      <p className="text-xs text-muted-foreground">Accuracy</p>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm">Neural Network</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-2xl font-bold">0.75</p>
                      <p className="text-xs text-muted-foreground">Accuracy</p>
                    </CardContent>
                  </Card>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="logs">
              <div className="bg-muted p-4 rounded-lg font-mono text-sm space-y-2 max-h-64 overflow-y-auto">
                <p className="text-muted-foreground">[2024-01-15 10:30:00] Training started...</p>
                <p className="text-muted-foreground">[2024-01-15 10:30:15] Loaded 800 training samples</p>
                <p className="text-muted-foreground">[2024-01-15 10:30:20] Epoch 1/5 - Accuracy: 0.72</p>
                <p className="text-muted-foreground">[2024-01-15 10:30:25] Epoch 2/5 - Accuracy: 0.74</p>
                <p className="text-muted-foreground">[2024-01-15 10:30:30] Epoch 3/5 - Accuracy: 0.76</p>
                <p className="text-muted-foreground">[2024-01-15 10:30:35] Epoch 4/5 - Accuracy: 0.78</p>
                <p className="text-muted-foreground">[2024-01-15 10:30:40] Epoch 5/5 - Accuracy: 0.79</p>
                <p className="text-muted-foreground">[2024-01-15 10:30:45] Model saved and registered</p>
                <p className="text-muted-foreground">[2024-01-15 10:30:50] Training completed!</p>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  )
}

"use client"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Button } from "@/components/ui/button"

interface Prediction {
  rank: number
  team: string
  probability: number
  confidence: string
}

interface PredictionsTableProps {
  data: Prediction[]
  isLoading: boolean
  onTeamSelect: (team: string) => void
}

export function PredictionsTable({ data, isLoading, onTeamSelect }: PredictionsTableProps) {
  if (isLoading) {
    return <div className="text-center py-8">Loading predictions...</div>
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead className="w-12">Rank</TableHead>
          <TableHead>Team</TableHead>
          <TableHead>Probability</TableHead>
          <TableHead className="w-32">Actions</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {data.length === 0 ? (
          <TableRow>
            <TableCell colSpan={4} className="text-center py-8 text-muted-foreground">
              No predictions available
            </TableCell>
          </TableRow>
        ) : (
          data.map((prediction) => (
            <TableRow key={prediction.team}>
              <TableCell>
                <Badge variant="outline" className="text-lg font-bold">
                  {prediction.rank}
                </Badge>
              </TableCell>
              <TableCell className="font-semibold">{prediction.team}</TableCell>
              <TableCell>
                <div className="w-32">
                  <Progress value={prediction.probability * 100} className="mb-2" />
                  <span className="text-sm text-muted-foreground">{prediction.confidence}</span>
                </div>
              </TableCell>
              <TableCell>
                <Button variant="outline" size="sm" onClick={() => onTeamSelect(prediction.team)}>
                  Details
                </Button>
              </TableCell>
            </TableRow>
          ))
        )}
      </TableBody>
    </Table>
  )
}

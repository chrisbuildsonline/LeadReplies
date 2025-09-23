import { Skeleton } from "@/components/ui/skeleton";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

interface PerformanceChartProps {
  isLoading: boolean;
}

export default function PerformanceChart({ isLoading }: PerformanceChartProps) {
  // Sample data for the chart visualization
  const chartData = [40, 65, 35, 80, 55, 90, 70];
  const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900" data-testid="reply-activity-title">
          Reply Activity
        </h2>
        <Select defaultValue="7days">
          <SelectTrigger className="w-40" data-testid="select-time-period">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="7days">Last 7 days</SelectItem>
            <SelectItem value="30days">Last 30 days</SelectItem>
            <SelectItem value="90days">Last 90 days</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {isLoading ? (
        <Skeleton className="h-64" />
      ) : (
        <>
          <div className="h-64 flex items-end space-x-2 px-4 py-4 bg-gray-50 rounded-lg" data-testid="performance-chart">
            {chartData.map((height, index) => (
              <div
                key={index}
                className="flex-1 bg-gradient-to-t from-blue-600 to-blue-400 rounded-t transition-all hover:from-blue-700 hover:to-blue-500"
                style={{ height: `${height}%` }}
                title={`${days[index]}: ${height}% activity`}
              />
            ))}
          </div>
          <div className="flex justify-between text-sm text-gray-500 mt-2">
            {days.map((day) => (
              <span key={day}>{day}</span>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

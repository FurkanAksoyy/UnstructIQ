import { useEffect, useRef } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Chart } from 'react-chartjs-2';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface ChartDisplayProps {
  chartConfig: any;
}

export default function ChartDisplay({ chartConfig }: ChartDisplayProps) {
  const chartRef = useRef<ChartJS>(null);

  useEffect(() => {
    return () => {
      if (chartRef.current) {
        chartRef.current.destroy();
      }
    };
  }, []);

  return (
    <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-white">{chartConfig.title}</h3>
        <p className="text-sm text-gray-400">{chartConfig.description}</p>
      </div>

      <div className="relative h-80">
        <Chart
          ref={chartRef}
          type={chartConfig.type}
          data={chartConfig.data}
          options={{
            ...chartConfig.options,
            maintainAspectRatio: false,
          }}
        />
      </div>
    </div>
  );
}
import React from 'react';
import { Box, Paper, Typography } from '@mui/material';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import { EvaluationTest } from '../types';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface EvaluationTrendsProps {
  tests: EvaluationTest[];
}

interface ChartDataset {
  label: string;
  data: (number | null)[];
  borderColor: string;
  backgroundColor: string;
  tension: number;
  pointRadius: number;
  pointHoverRadius: number;
  yAxisID: string;
  borderDash?: number[];
}

const EvaluationTrends: React.FC<EvaluationTrendsProps> = ({ tests }) => {
  // Process the data for the line chart
  const processData = () => {
    // Sort tests by date
    const sortedTests = [...tests].sort((a, b) => 
      new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
    );

    // Get unique model identifiers across all tests
    const modelSet = new Set<string>();
    sortedTests.forEach(test => {
      test.results.forEach(result => {
        modelSet.add(`${result.provider}/${result.modelId}`);
      });
    });

    // Create datasets for each model (rank and cost)
    const datasets: ChartDataset[] = [];
    const modelIds = Array.from(modelSet);
    
    // First, add rank datasets
    modelIds.forEach((modelId, index) => {
      const data = sortedTests.map(test => {
        const modelResults = test.results.filter(r => `${r.provider}/${r.modelId}` === modelId);
        if (modelResults.length === 0) return null;
        
        // Calculate average rank for this model in this test
        const avgRank = modelResults.reduce((sum, r) => sum + (r.rank || 0), 0) / modelResults.length;
        return avgRank;
      });

      // Generate a consistent color based on the model name
      const hash = modelId.split('').reduce((acc, char) => char.charCodeAt(0) + acc, 0);
      const hue = hash % 360;

      datasets.push({
        label: `${modelId} (Rank)`,
        data: data,
        borderColor: `hsl(${hue}, 70%, 50%)`,
        backgroundColor: `hsl(${hue}, 70%, 50%, 0.5)`,
        tension: 0.3,
        pointRadius: 4,
        pointHoverRadius: 6,
        yAxisID: 'y'  // Use primary y-axis for ranks
      });
    });

    // Then, add cost datasets
    modelIds.forEach((modelId, index) => {
      const data = sortedTests.map(test => {
        const modelResults = test.results.filter(r => `${r.provider}/${r.modelId}` === modelId);
        if (modelResults.length === 0) return null;
        
        // Calculate total cost for this model in this test
        const totalCost = modelResults.reduce((sum, r) => sum + (r.cost || 0), 0);
        return totalCost;
      });

      // Generate a consistent color but darker for cost lines
      const hash = modelId.split('').reduce((acc, char) => char.charCodeAt(0) + acc, 0);
      const hue = hash % 360;

      datasets.push({
        label: `${modelId} (Cost)`,
        data: data,
        borderColor: `hsl(${hue}, 70%, 30%)`,
        backgroundColor: `hsl(${hue}, 70%, 30%, 0.5)`,
        borderDash: [5, 5],  // Make cost lines dashed
        tension: 0.3,
        pointRadius: 4,
        pointHoverRadius: 6,
        yAxisID: 'y1'  // Use secondary y-axis for costs
      });
    });

    return {
      labels: sortedTests.map(test => new Date(test.created_at).toLocaleDateString()),
      datasets: datasets,
    };
  };

  const options = {
    responsive: true,
    interaction: {
      mode: 'index' as const,
      intersect: false,
    },
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Model Performance and Cost Trends Over Time',
      },
      tooltip: {
        callbacks: {
          label: (context: any) => {
            const label = context.dataset.label || '';
            const value = context.parsed.y;
            if (label.includes('Cost')) {
              return `${label}: $${value.toFixed(6)}`;
            }
            return `${label}: ${value.toFixed(2)}`;
          },
        },
      },
    },
    scales: {
      y: {
        type: 'linear' as const,
        display: true,
        position: 'left' as const,
        reverse: true,  // Lower rank is better
        title: {
          display: true,
          text: 'Average Rank (lower is better)',
        },
      },
      y1: {
        type: 'linear' as const,
        display: true,
        position: 'right' as const,
        grid: {
          drawOnChartArea: false,  // Only show grid lines for primary y-axis
        },
        title: {
          display: true,
          text: 'Cost ($)',
        },
        min: 0,  // Start cost axis at 0
      },
    },
  };

  if (!tests.length) {
    return null;
  }

  return (
    <Paper sx={{ p: 3, mb: 3 }}>
      <Typography variant="h6" gutterBottom>
        Performance and Cost Trends
      </Typography>
      <Box sx={{ height: 400 }}>
        <Line options={options} data={processData()} />
      </Box>
    </Paper>
  );
};

export default EvaluationTrends; 
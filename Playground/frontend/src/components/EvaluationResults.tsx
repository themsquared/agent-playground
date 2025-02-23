import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import { EvaluationTest } from '../types';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface EvaluationResultsProps {
  test: EvaluationTest;
}

const EvaluationResults: React.FC<EvaluationResultsProps> = ({ test }) => {
  const [expanded, setExpanded] = useState(false);

  // Calculate the best performing model based on average rank
  const getBestModel = () => {
    const modelPerformance = new Map();
    test.results.forEach(result => {
      const modelKey = `${result.provider}/${result.modelId}`;
      if (!modelPerformance.has(modelKey)) {
        modelPerformance.set(modelKey, { totalRank: 0, count: 0 });
      }
      const current = modelPerformance.get(modelKey);
      current.totalRank += result.rank || 0;
      current.count += 1;
    });

    let bestModel = '';
    let bestAvgRank = Infinity;
    modelPerformance.forEach((perf, model) => {
      const avgRank = perf.totalRank / perf.count;
      if (avgRank < bestAvgRank) {
        bestAvgRank = avgRank;
        bestModel = model;
      }
    });

    return bestModel;
  };

  // Prepare data for chart
  const chartData = {
    labels: Array.from(new Set(test.results.map(r => `${r.provider}/${r.modelId}`))),
    datasets: [
      {
        label: 'Average Rank',
        data: Array.from(new Set(test.results.map(r => `${r.provider}/${r.modelId}`))).map(model => {
          const modelResults = test.results.filter(r => `${r.provider}/${r.modelId}` === model);
          const avgRank = modelResults.reduce((sum, r) => sum + (r.rank || 0), 0) / modelResults.length;
          return avgRank;
        }),
        backgroundColor: 'rgba(53, 162, 235, 0.5)',
      },
      {
        label: 'Cost ($)',
        data: Array.from(new Set(test.results.map(r => `${r.provider}/${r.modelId}`))).map(model => {
          const modelResults = test.results.filter(r => `${r.provider}/${r.modelId}` === model);
          const totalCost = modelResults.reduce((sum, r) => sum + r.cost, 0);
          return totalCost;
        }),
        backgroundColor: 'rgba(255, 99, 132, 0.5)',
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Model Performance and Cost Comparison',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  };

  const handleExportCSV = () => {
    window.open(`http://localhost:5000/api/evaluation/csv/${test.id}`, '_blank');
  };

  return (
    <Accordion 
      expanded={expanded} 
      onChange={() => setExpanded(!expanded)}
      sx={{ mb: 2 }}
    >
      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
        <Box sx={{ display: 'flex', flexDirection: 'column', width: '100%' }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', width: '100%', alignItems: 'center' }}>
            <Typography variant="h6">{test.name}</Typography>
            <Typography variant="body2" color="text.secondary">
              {new Date(test.created_at).toLocaleDateString()}
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', gap: 4, mt: 1 }}>
            <Typography variant="body2" color="text.secondary">
              Questions: {test.questions.length}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Best Model: {getBestModel()}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Total Cost: ${test.total_cost.toFixed(6)}
            </Typography>
          </Box>
        </Box>
      </AccordionSummary>
      
      <AccordionDetails>
        <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
          <Button
            variant="contained"
            onClick={handleExportCSV}
            size="small"
          >
            Export CSV
          </Button>
        </Box>

        <Box sx={{ height: 400, mb: 4 }}>
          <Bar options={chartOptions} data={chartData} />
        </Box>

        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Question</TableCell>
                <TableCell>Model</TableCell>
                <TableCell>Response</TableCell>
                <TableCell align="right">Rank</TableCell>
                <TableCell align="right">Cost ($)</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {test.results.map((result, index) => (
                <TableRow key={result.id || index}>
                  <TableCell>{test.questions[result.questionIndex]}</TableCell>
                  <TableCell>{`${result.provider}/${result.modelId}`}</TableCell>
                  <TableCell>{result.response}</TableCell>
                  <TableCell align="right">{result.rank}</TableCell>
                  <TableCell align="right">{result.cost.toFixed(6)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </AccordionDetails>
    </Accordion>
  );
};

export default EvaluationResults; 
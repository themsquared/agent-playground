import React from 'react';
import { Box, Typography, Paper } from '@mui/material';
import { ActionResult } from '../types';

interface ActionResultsProps {
  results: ActionResult[];
}

const ActionResults: React.FC<ActionResultsProps> = ({ results }) => {
  if (!results || results.length === 0) return null;

  return (
    <Box sx={{ mt: 2 }}>
      <Typography variant="h6" gutterBottom>
        Action Results
      </Typography>
      {results.map((result, index) => (
        <Paper
          key={index}
          sx={{
            p: 2,
            mb: 2,
            backgroundColor: result.success ? 'success.light' : 'error.light',
            color: '#000000',
            border: 1,
            borderColor: result.success ? 'success.main' : 'error.main'
          }}
        >
          <Typography
            variant="subtitle1"
            gutterBottom
            sx={{
              color: result.success ? 'success.dark' : 'error.dark',
              fontWeight: 'bold'
            }}
          >
            {result.success ? '✓ Success' : '✗ Error'}
          </Typography>
          <Typography
            variant="body1"
            gutterBottom
            sx={{ color: '#000000' }}
          >
            {result.message}
          </Typography>
          {result.error && (
            <Typography
              variant="body2"
              sx={{
                mt: 1,
                color: 'error.dark',
                fontWeight: 'medium'
              }}
            >
              Error: {result.error}
            </Typography>
          )}
          {result.data && (
            <Box sx={{ mt: 2 }}>
              <Typography
                variant="subtitle2"
                gutterBottom
                sx={{ color: '#000000' }}
              >
                Details:
              </Typography>
              <pre style={{
                margin: 0,
                padding: '8px',
                backgroundColor: 'rgba(0, 0, 0, 0.04)',
                borderRadius: '4px',
                overflow: 'auto',
                color: '#000000'
              }}>
                {JSON.stringify(result.data, null, 2)}
              </pre>
            </Box>
          )}
        </Paper>
      ))}
    </Box>
  );
};

export default ActionResults; 
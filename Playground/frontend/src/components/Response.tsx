import React from 'react';
import { Box, Typography, Chip, Stack, Paper } from '@mui/material';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';

interface ResponseProps {
  content: string;
  cost?: {
    input_cost: number;
    output_cost: number;
    total_cost: number;
  };
}

export const Response: React.FC<ResponseProps> = ({ content, cost }) => {
  console.log('Response component received cost:', cost);  // Debug log
  
  return (
    <Box sx={{ mt: 2 }}>
      {cost && cost.total_cost > 0 && (  // Only show if cost exists and is greater than 0
        <Paper 
          elevation={0} 
          sx={{ 
            p: 2, 
            mb: 2, 
            bgcolor: 'background.paper',
            border: 1,
            borderColor: 'divider',
            borderRadius: 1
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <AccountBalanceIcon sx={{ mr: 1 }} />
            <Typography variant="h6" sx={{ flexGrow: 1 }}>
              Query Cost Breakdown
            </Typography>
          </Box>
          <Stack direction="row" spacing={2} sx={{ mb: 1 }}>
            <Chip
              icon={<AttachMoneyIcon />}
              label={`Input Cost: $${cost.input_cost.toFixed(6)}`}
              size="medium"
              color="info"
              variant="outlined"
              sx={{ flexGrow: 1 }}
            />
            <Chip
              icon={<AttachMoneyIcon />}
              label={`Output Cost: $${cost.output_cost.toFixed(6)}`}
              size="medium"
              color="info"
              variant="outlined"
              sx={{ flexGrow: 1 }}
            />
          </Stack>
          <Chip
            icon={<AttachMoneyIcon />}
            label={`Total Cost: $${cost.total_cost.toFixed(6)}`}
            size="medium"
            color="primary"
            sx={{ width: '100%' }}
          />
        </Paper>
      )}

      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
        <Typography variant="h6">
          LLM Response
        </Typography>
      </Box>
      
      <Typography
        component="pre"
        sx={{
          whiteSpace: 'pre-wrap',
          wordWrap: 'break-word',
          fontFamily: 'monospace',
          bgcolor: 'background.paper',
          p: 2,
          borderRadius: 1,
          border: 1,
          borderColor: 'divider',
          maxHeight: '400px',
          overflow: 'auto'
        }}
      >
        {content}
      </Typography>
    </Box>
  );
}; 
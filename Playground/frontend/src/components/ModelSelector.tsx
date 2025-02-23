import React from 'react';
import {
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent,
  Box,
  CircularProgress,
  Typography,
  Tooltip,
} from '@mui/material';
import { useModels } from '../hooks/useModels';

interface ModelSelectorProps {
  provider: string;
  model: string;
  onProviderChange: (provider: string) => void;
  onModelChange: (model: string) => void;
}

export const ModelSelector: React.FC<ModelSelectorProps> = ({
  provider,
  model,
  onProviderChange,
  onModelChange,
}) => {
  const { models, loading, error } = useModels();

  if (loading) {
    return (
      <Box display="flex" alignItems="center" gap={2}>
        <CircularProgress size={20} />
        <Typography>Loading models...</Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Typography color="error">
        Error loading models: {error}
      </Typography>
    );
  }

  const providers = Object.keys(models);
  const currentProviderModels = models[provider] || {};

  const handleProviderChange = (event: SelectChangeEvent) => {
    const newProvider = event.target.value;
    onProviderChange(newProvider);
    onModelChange('');
  };

  const handleModelChange = (event: SelectChangeEvent) => {
    onModelChange(event.target.value);
  };

  return (
    <Box display="flex" gap={2}>
      <FormControl fullWidth>
        <InputLabel>Provider</InputLabel>
        <Select
          value={provider}
          label="Provider"
          onChange={handleProviderChange}
        >
          {providers.map((p) => (
            <MenuItem key={p} value={p}>
              {p.charAt(0).toUpperCase() + p.slice(1)}
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      <FormControl fullWidth>
        <InputLabel>Model</InputLabel>
        <Select
          value={model || ''}
          label="Model"
          onChange={handleModelChange}
          renderValue={(selected) => {
            const modelInfo = currentProviderModels[selected];
            return (
              <Box sx={{ display: 'flex', flexDirection: 'column' }}>
                <Typography variant="body1">{selected}</Typography>
                {modelInfo && (
                  <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.75rem' }}>
                    {modelInfo}
                  </Typography>
                )}
              </Box>
            );
          }}
        >
          {Object.entries(currentProviderModels).map(([modelId, description]) => (
            <MenuItem key={modelId} value={modelId}>
              <Box sx={{ display: 'flex', flexDirection: 'column' }}>
                <Typography variant="body1">{modelId}</Typography>
                <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.75rem' }}>
                  {description}
                </Typography>
              </Box>
            </MenuItem>
          ))}
        </Select>
      </FormControl>
    </Box>
  );
}; 
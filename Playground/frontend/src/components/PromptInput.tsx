import React from 'react';
import {
  Box,
  TextField,
  Button,
  IconButton,
  Tooltip,
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';

interface PromptInputProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  onClear?: () => void;
  disabled?: boolean;
}

export const PromptInput: React.FC<PromptInputProps> = ({
  value,
  onChange,
  onSubmit,
  onClear,
  disabled = false,
}) => {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
      <Box sx={{ display: 'flex', gap: 1 }}>
        <TextField
          fullWidth
          multiline
          rows={4}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          label="Prompt"
          variant="outlined"
          disabled={disabled}
        />
        {onClear && (
          <Tooltip title="Clear conversation history">
            <IconButton
              onClick={onClear}
              sx={{ alignSelf: 'flex-start' }}
              disabled={disabled}
            >
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        )}
      </Box>

      <Button
        variant="contained"
        onClick={onSubmit}
        disabled={disabled || !value.trim()}
        fullWidth
      >
        Generate
      </Button>
    </Box>
  );
}; 
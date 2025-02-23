import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  TextField,
  Button,
  FormControl,
  FormControlLabel,
  RadioGroup,
  Radio,
  Alert,
  CircularProgress,
  Divider,
} from '@mui/material';
import { useTheme } from '../hooks/useTheme';

interface Settings {
  api_keys: {
    [key: string]: string | null;
  };
  theme: string;
}

const SettingsTab: React.FC = () => {
  const [settings, setSettings] = useState<Settings>({ api_keys: {}, theme: 'dark' });
  const [apiKeys, setApiKeys] = useState<{ [key: string]: string }>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const { theme, setTheme } = useTheme();

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/settings', {
        credentials: 'include',
      });
      if (!response.ok) throw new Error('Failed to fetch settings');
      const data = await response.json();
      setSettings(data);
      // Initialize API key form fields with empty strings
      const initialApiKeys: { [key: string]: string } = {};
      Object.keys(data.api_keys).forEach(provider => {
        if (provider !== 'ollama') {  // Skip Ollama
          initialApiKeys[provider] = '';
        }
      });
      setApiKeys(initialApiKeys);
      setLoading(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      setLoading(false);
    }
  };

  const handleApiKeyChange = (provider: string, value: string) => {
    setApiKeys(prev => ({
      ...prev,
      [provider]: value
    }));
  };

  const handleThemeChange = async (newTheme: string) => {
    try {
      const response = await fetch('http://localhost:5000/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          theme: newTheme
        })
      });
      
      if (!response.ok) throw new Error('Failed to update theme');
      setTheme(newTheme);
      setSuccess('Theme updated successfully');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update theme');
      setTimeout(() => setError(null), 3000);
    }
  };

  const handleSubmit = async () => {
    setError(null);
    setSuccess(null);
    
    // Filter out empty API keys and Ollama
    const updatedKeys: { [key: string]: string } = {};
    Object.entries(apiKeys).forEach(([provider, key]) => {
      if (provider !== 'ollama' && key.trim()) {  // Skip Ollama and empty keys
        updatedKeys[provider] = key.trim();
      }
    });
    
    try {
      const response = await fetch('http://localhost:5000/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          api_keys: updatedKeys
        })
      });
      
      if (!response.ok) throw new Error('Failed to update settings');
      
      setSuccess('API keys updated successfully');
      // Clear the form
      setApiKeys(prev => {
        const newKeys: { [key: string]: string } = {};
        Object.keys(prev).forEach(provider => {
          if (provider !== 'ollama') {  // Skip Ollama
            newKeys[provider] = '';
          }
        });
        return newKeys;
      });
      // Refresh settings to show updated masked keys
      await fetchSettings();
      
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update settings');
      setTimeout(() => setError(null), 3000);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Paper sx={{ p: 3, maxWidth: 600, mx: 'auto', mt: 2 }}>
      <Typography variant="h5" gutterBottom>
        Settings
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      {success && (
        <Alert severity="success" sx={{ mb: 2 }}>
          {success}
        </Alert>
      )}

      <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
        Theme
      </Typography>
      <FormControl component="fieldset">
        <RadioGroup
          value={theme}
          onChange={(e) => handleThemeChange(e.target.value)}
        >
          <FormControlLabel value="dark" control={<Radio />} label="Dark" />
          <FormControlLabel value="light" control={<Radio />} label="Light" />
        </RadioGroup>
      </FormControl>

      <Divider sx={{ my: 3 }} />
      
      <Typography variant="h6" gutterBottom>
        API Keys
      </Typography>
      
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        {Object.entries(settings.api_keys).map(([provider, maskedKey]) => (
          provider !== 'ollama' && (  // Skip Ollama
            <TextField
              key={provider}
              label={`${provider.charAt(0).toUpperCase() + provider.slice(1)} API Key`}
              type="password"
              value={apiKeys[provider]}
              onChange={(e) => handleApiKeyChange(provider, e.target.value)}
              placeholder={maskedKey || 'Enter API key'}
              fullWidth
              helperText={maskedKey ? `Current: ${maskedKey}` : 'No API key set'}
            />
          )
        ))}
        
        <Button
          variant="contained"
          onClick={handleSubmit}
          disabled={Object.values(apiKeys).every(key => !key.trim())}
          sx={{ mt: 2 }}
        >
          Save API Keys
        </Button>
      </Box>
    </Paper>
  );
};

export default SettingsTab; 
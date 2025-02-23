import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  CircularProgress,
  Divider,
} from '@mui/material';
import { ModelSelector } from './ModelSelector';
import { PromptInput } from './PromptInput';
import { Response } from './Response';
import ActionResults from './ActionResults';
import { AvailableActions } from './AvailableActions';
import { ActionResult, GenerateResponse, Actions } from '../types';

const PlaygroundTab: React.FC = () => {
  const [selectedProvider, setSelectedProvider] = useState('ollama');
  const [selectedModel, setSelectedModel] = useState('');
  const [prompt, setPrompt] = useState('');
  const [response, setResponse] = useState<string>('');
  const [actionResults, setActionResults] = useState<ActionResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [actions, setActions] = useState<Actions>({});
  const [responseCost, setResponseCost] = useState<{
    input_cost: number;
    output_cost: number;
    total_cost: number;
  } | undefined>(undefined);

  useEffect(() => {
    // Fetch available actions
    fetch('http://localhost:5000/api/actions')
      .then(res => res.json())
      .then(data => setActions(data))
      .catch(err => console.error('Failed to fetch actions:', err));
  }, []);

  const handleProviderChange = (provider: string) => {
    setSelectedProvider(provider);
    setSelectedModel('');
  };

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);
    setResponse('');
    setActionResults([]);
    setResponseCost(undefined);

    try {
      const res = await fetch('http://localhost:5000/api/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          provider: selectedProvider,
          model: selectedModel,
          prompt,
        }),
        credentials: 'include',
      });

      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }

      const data: GenerateResponse = await res.json();
      console.log('API Response:', data);  // Debug log
      
      // Try to parse the content as JSON to format it nicely
      try {
        const contentObj = JSON.parse(data.content);
        setResponse(JSON.stringify(contentObj, null, 2));
      } catch {
        // If it's not valid JSON, use the content as is
        setResponse(data.content);
      }

      // Set cost information
      console.log('Setting cost:', data.cost);  // Debug log
      setResponseCost(data.cost);

      // Set action results if any
      if (data.action_results && data.action_results.length > 0) {
        setActionResults(data.action_results);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleClearHistory = async () => {
    try {
      await fetch('http://localhost:5000/api/history/clear', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          provider: selectedProvider,
        }),
        credentials: 'include',
      });
      setPrompt('');
      setResponse('');
      setActionResults([]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to clear history');
    }
  };

  return (
    <>
      <Paper sx={{ p: 2, mb: 2 }}>
        <ModelSelector
          provider={selectedProvider}
          model={selectedModel}
          onProviderChange={handleProviderChange}
          onModelChange={setSelectedModel}
        />
      </Paper>

      <Paper sx={{ p: 2, mb: 2 }}>
        <AvailableActions actions={actions} />
      </Paper>

      <Paper sx={{ p: 2 }}>
        <PromptInput
          value={prompt}
          onChange={setPrompt}
          onSubmit={handleSubmit}
          onClear={handleClearHistory}
          disabled={loading}
        />

        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 2 }}>
            <CircularProgress />
          </Box>
        )}

        {error && (
          <Typography color="error" sx={{ mt: 2 }}>
            Error: {error}
          </Typography>
        )}

        {response && (
          <>
            <Response
              content={response}
              cost={responseCost}
            />
            {actionResults.length > 0 && (
              <>
                <Divider sx={{ my: 2 }} />
                <ActionResults results={actionResults} />
              </>
            )}
          </>
        )}
      </Paper>
    </>
  );
};

export default PlaygroundTab; 
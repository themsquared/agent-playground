import { useState, useEffect } from 'react';
import { ModelsResponse } from '../types';

const API_BASE_URL = 'http://localhost:5000';

export const useModels = () => {
  const [models, setModels] = useState<ModelsResponse>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchModels = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${API_BASE_URL}/api/models`, {
          credentials: 'include',  // Include cookies in the request
          headers: {
            'Accept': 'application/json'
          }
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        setModels(data);
      } catch (err) {
        console.error('Error fetching models:', err);
        setError(err instanceof Error ? err.message : 'Failed to fetch models');
      } finally {
        setLoading(false);
      }
    };

    fetchModels();
  }, []);

  return { models, loading, error };
}; 
import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  TextField,
  Button,
  FormGroup,
  FormControlLabel,
  Checkbox,
  CircularProgress,
  Stepper,
  Step,
  StepLabel,
  Card,
  CardContent,
  Radio,
  RadioGroup,
  FormControl,
  FormLabel,
  Alert,
  Divider,
  List,
  ListItem,
  ListItemText,
  Collapse,
} from '@mui/material';
import { useModels } from '../hooks/useModels';
import { v4 as uuidv4 } from 'uuid';
import EvaluationResults from './EvaluationResults';
import { EvaluationTest } from '../types';
import EvaluationTrends from './EvaluationTrends';

interface ModelInfo {
  provider: string;
  modelId: string;
  description: string;
}

interface EvaluationResponse {
  provider: string;
  modelId: string;
  response: string;
  rank?: number;
  questionIndex: number;
  cost: number;
}

interface EvaluationResult {
  question: string;
  responses: {
    provider: string;
    modelId: string;
    response: string;
    rank?: number;
    cost: number;
  }[];
}

interface FinalResults {
  provider: string;
  modelId: string;
  averageRank: number;
  totalScore: number;
}

const EvaluationTab: React.FC = () => {
  const { models, loading: loadingModels } = useModels();
  const [selectedModels, setSelectedModels] = useState<{ [key: string]: boolean }>({});
  const [questions, setQuestions] = useState<string>('');
  const [testName, setTestName] = useState<string>('');
  const [currentStep, setCurrentStep] = useState(0);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [evaluationResults, setEvaluationResults] = useState<EvaluationResult[]>([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [finalResults, setFinalResults] = useState<FinalResults[]>([]);
  const [evaluationComplete, setEvaluationComplete] = useState(false);
  const [expandedProvider, setExpandedProvider] = useState<string | null>(null);
  const [currentTest, setCurrentTest] = useState<EvaluationTest | null>(null);
  const [previousTests, setPreviousTests] = useState<EvaluationTest[]>([]);

  // Initialize available models when models are loaded
  useEffect(() => {
    if (models) {
      const initialSelectedModels: { [key: string]: boolean } = {};
      Object.entries(models).forEach(([provider, modelList]) => {
        Object.keys(modelList).forEach(modelId => {
          initialSelectedModels[`${provider}:${modelId}`] = false;
        });
      });
      setSelectedModels(initialSelectedModels);
    }
  }, [models]);

  useEffect(() => {
    // Load previous tests on component mount
    fetchPreviousTests();
  }, []);

  const fetchPreviousTests = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/evaluation/results');
      const data = await response.json();
      setPreviousTests(data);
    } catch (err) {
      console.error('Failed to fetch previous tests:', err);
    }
  };

  const steps = ['Select Models', 'Enter Questions', 'Evaluate Responses', 'View Results'];

  const handleModelSelection = (provider: string, modelId: string) => {
    const key = `${provider}:${modelId}`;
    setSelectedModels(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  const handleProviderExpand = (provider: string) => {
    setExpandedProvider(expandedProvider === provider ? null : provider);
  };

  const handleQuestionsChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    setQuestions(event.target.value);
  };

  const handleSubmit = async () => {
    if (!questions.trim()) {
      setError('Please enter at least one question');
      return;
    }
    if (!testName.trim()) {
      setError('Please enter a test name');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const questionList = questions.split('\n').filter(q => q.trim());
      const testId = uuidv4();
      
      // Get list of selected models
      const selectedModelsList = Object.entries(selectedModels)
        .filter(([_, selected]) => selected)
        .map(([key]) => {
          const [provider, modelId] = key.split(':');
          console.log('Processing model selection:', { key, provider, modelId });
          return { provider, modelId };
        });

      if (selectedModelsList.length === 0) {
        setError('Please select at least one model');
        setLoading(false);
        return;
      }

      console.log('Selected models for evaluation:', selectedModelsList);
      
      const response = await fetch('http://localhost:5000/api/evaluation/evaluate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          id: testId,
          name: testName,
          questions: questionList,
          models: selectedModelsList
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Evaluation failed');
      }

      const result = await response.json();
      console.log('Raw evaluation results:', result);
      
      // Group responses by question for ranking
      const evaluationResults: EvaluationResult[] = [];
      for (let i = 0; i < questionList.length; i++) {
        const questionResponses = result.results
          .filter((r: EvaluationResponse) => r.questionIndex === i)
          .map((r: EvaluationResponse) => {
            console.log('Processing response:', r);
            return {
              provider: r.provider,
              modelId: r.modelId,
              response: r.response,
              rank: r.rank,
              cost: r.cost
            };
          });

        if (questionResponses.length > 0) {
          evaluationResults.push({
            question: questionList[i],
            responses: questionResponses
          });
        }
      }
      
      console.log('Processed evaluation results:', evaluationResults);
      
      if (evaluationResults.length === 0) {
        throw new Error('No valid responses received from any model');
      }
      
      setEvaluationResults(evaluationResults);
      setCurrentQuestionIndex(0);
      setCurrentStep(2); // Move to ranking step
    } catch (err) {
      console.error('Evaluation error:', err);
      setError(err instanceof Error ? err.message : 'An error occurred during evaluation');
    } finally {
      setLoading(false);
    }
  };

  const handleRankChange = (responseIndex: number, newRank: number) => {
    setEvaluationResults(prevResults => {
      const updatedResults = [...prevResults];
      const currentQuestion = updatedResults[currentQuestionIndex];
      const responses = [...currentQuestion.responses];

      // Get the old rank of the response being changed
      const oldRank = responses[responseIndex].rank;

      // Find if any other response already has the new rank
      const existingResponseWithRank = responses.findIndex(r => r.rank === newRank);

      if (existingResponseWithRank !== -1) {
        // If the new rank is already taken, swap ranks
        responses[existingResponseWithRank].rank = oldRank;
      }

      // Set the new rank for the selected response
      responses[responseIndex].rank = newRank;

      // Update the responses in the current question
      currentQuestion.responses = responses;
      updatedResults[currentQuestionIndex] = currentQuestion;

      return updatedResults;
    });
  };

  // Helper function to check if a rank is already taken
  const isRankTaken = (rank: number, responseIndex: number): boolean => {
    const currentQuestion = evaluationResults[currentQuestionIndex];
    return currentQuestion.responses.some((r, index) => index !== responseIndex && r.rank === rank);
  };

  // Render radio buttons for ranking
  const renderRankingRadios = (responseIndex: number) => {
    const response = evaluationResults[currentQuestionIndex].responses[responseIndex];
    const numResponses = evaluationResults[currentQuestionIndex].responses.length;
    
    return (
      <RadioGroup
        row
        value={response.rank || ''}
        onChange={(e) => handleRankChange(responseIndex, Number(e.target.value))}
      >
        {Array.from({ length: numResponses }, (_, i) => i + 1).map((rank) => (
          <FormControlLabel
            key={rank}
            value={rank}
            control={<Radio />}
            label={rank.toString()}
            disabled={response.rank !== rank && isRankTaken(rank, responseIndex)}
          />
        ))}
      </RadioGroup>
    );
  };

  const nextQuestion = () => {
    // Validate that all responses for current question are ranked
    const currentResponses = evaluationResults[currentQuestionIndex].responses;
    if (!currentResponses.every(r => r.rank !== undefined)) {
      setError('Please rank all responses before proceeding');
      return;
    }
    setError(null);

    if (currentQuestionIndex < evaluationResults.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
    } else {
      // All questions have been ranked, prepare final results
      const finalResults: FinalResults[] = [];
      const modelResults = new Map<string, { ranks: number[], scores: number[], costs: number[] }>();

      // Calculate average ranks and total scores
      evaluationResults.forEach(result => {
        result.responses.forEach(response => {
          const key = `${response.provider}/${response.modelId}`;
          if (!modelResults.has(key)) {
            modelResults.set(key, { ranks: [], scores: [], costs: [] });
          }
          const modelResult = modelResults.get(key)!;
          modelResult.ranks.push(response.rank || 0);
          modelResult.costs.push(response.cost || 0);
          // Calculate score based on rank (higher rank = lower score)
          modelResult.scores.push(response.rank ? result.responses.length - response.rank + 1 : 0);
        });
      });

      modelResults.forEach((value, key) => {
        const [provider, modelId] = key.split('/');
        finalResults.push({
          provider,
          modelId,
          averageRank: value.ranks.reduce((a, b) => a + b, 0) / value.ranks.length,
          totalScore: value.scores.reduce((a, b) => a + b, 0)
        });
      });

      // Save the evaluation results
      const saveResults = async () => {
        try {
          // Calculate total cost
          const totalCost = evaluationResults.reduce(
            (total, result) => total + result.responses.reduce(
              (questionTotal, response) => questionTotal + (response.cost || 0), 
              0
            ), 
            0
          );

          // Get the list of questions
          const questionList = evaluationResults.map(r => r.question);
          console.log('Saving questions:', questionList);

          // Flatten results into the format expected by the backend
          const flatResults = evaluationResults.flatMap((result, questionIndex) =>
            result.responses.map(response => ({
              provider: response.provider,
              modelId: response.modelId,
              questionIndex,
              response: response.response,
              rank: response.rank,
              cost: response.cost || 0 // Use the actual cost from the response
            }))
          );

          const saveData = {
            name: testName,
            questions: questionList,
            total_cost: totalCost,
            results: flatResults
          };
          console.log('Saving evaluation data:', saveData);

          const response = await fetch('http://localhost:5000/api/evaluation/save', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(saveData)
          });

          if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to save evaluation results');
          }

          const data = await response.json();
          console.log('Saved evaluation results:', data);

          // Set current test data
          setCurrentTest({
            id: data.test_id,
            name: testName,
            created_at: new Date().toISOString(),
            questions: questionList,
            total_cost: totalCost,
            results: flatResults
          });

          // Refresh the list of previous tests
          fetchPreviousTests();
        } catch (err) {
          console.error('Error saving results:', err);
          setError(err instanceof Error ? err.message : 'Failed to save evaluation results');
        }
      };

      // Save results and update state
      saveResults().then(() => {
        setFinalResults(finalResults);
        setEvaluationComplete(true);
        setCurrentStep(3); // Move to results step
      });
    }
  };

  const canProceed = () => {
    switch (currentStep) {
      case 0:
        return Object.values(selectedModels).some(selected => selected);
      case 1:
        return questions.trim().split('\n').filter(q => q.trim()).length > 0;
      case 2:
        if (!evaluationResults[currentQuestionIndex]) return false;
        return evaluationResults[currentQuestionIndex].responses.every(r => r.rank);
      default:
        return true;
    }
  };

  const renderStep = () => {
    switch (currentStep) {
      case 0:
        return (
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Select Models to Evaluate
            </Typography>
            <List>
              {Object.entries(models || {}).map(([provider, modelList]) => (
                <React.Fragment key={provider}>
                  <ListItem button onClick={() => handleProviderExpand(provider)}>
                    <ListItemText 
                      primary={provider.charAt(0).toUpperCase() + provider.slice(1)}
                      secondary={`${Object.keys(modelList).length} models available`}
                    />
                  </ListItem>
                  <Collapse in={expandedProvider === provider}>
                    <List component="div" disablePadding>
                      {Object.entries(modelList).map(([modelId, description]) => (
                        <ListItem key={modelId} sx={{ pl: 4 }}>
                          <FormControlLabel
                            control={
                              <Checkbox
                                checked={selectedModels[`${provider}:${modelId}`] || false}
                                onChange={() => handleModelSelection(provider, modelId)}
                              />
                            }
                            label={
                              <Box>
                                <Typography variant="body1">{modelId}</Typography>
                                <Typography variant="caption" color="text.secondary">
                                  {description}
                                </Typography>
                              </Box>
                            }
                          />
                        </ListItem>
                      ))}
                    </List>
                  </Collapse>
                  <Divider />
                </React.Fragment>
              ))}
            </List>
            <Button
              variant="contained"
              onClick={() => setCurrentStep(1)}
              disabled={!canProceed()}
              sx={{ mt: 2 }}
            >
              Next
            </Button>
          </Paper>
        );

      case 1:
        return (
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Enter Questions
            </Typography>
            <TextField
              fullWidth
              multiline
              rows={6}
              value={questions}
              onChange={handleQuestionsChange}
              placeholder="Enter one question per line..."
              variant="outlined"
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Test Name"
              value={testName}
              onChange={(e) => setTestName(e.target.value)}
              margin="normal"
              required
            />
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Button
                variant="outlined"
                onClick={() => setCurrentStep(0)}
              >
                Back
              </Button>
              <Button
                variant="contained"
                onClick={handleSubmit}
                disabled={!canProceed() || loading}
              >
                {loading ? <CircularProgress size={24} /> : 'Start Evaluation'}
              </Button>
            </Box>
          </Paper>
        );

      case 2:
        const currentQuestion = evaluationResults[currentQuestionIndex];
        if (!currentQuestion) return null;

        return (
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Evaluate Responses
            </Typography>
            <Typography variant="subtitle1" gutterBottom>
              Question {currentQuestionIndex + 1} of {evaluationResults.length}:
            </Typography>
            <Typography variant="body1" sx={{ mb: 2, fontWeight: 'bold' }}>
              {currentQuestion.question}
            </Typography>

            <FormControl component="fieldset">
              <FormLabel component="legend">
                Rank responses from 1 (best) to {currentQuestion.responses.length} (worst)
              </FormLabel>
              {currentQuestion.responses.map((response, index) => (
                <Card key={index} sx={{ mb: 2, mt: 2 }}>
                  <CardContent>
                    <Typography variant="body1" sx={{ mb: 2 }}>
                      {response.response}
                    </Typography>
                    {renderRankingRadios(index)}
                  </CardContent>
                </Card>
              ))}
            </FormControl>

            <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
              <Button
                variant="contained"
                onClick={nextQuestion}
                disabled={!canProceed()}
              >
                {currentQuestionIndex < evaluationResults.length - 1 ? 'Next Question' : 'View Results'}
              </Button>
            </Box>
          </Paper>
        );

      case 3:
        return (
          <Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h5">
                Final Results
              </Typography>
              <Button
                variant="contained"
                onClick={() => {
                  setCurrentStep(0);
                  setSelectedModels({});
                  setQuestions('');
                  setTestName('');
                  setEvaluationResults([]);
                  setCurrentQuestionIndex(0);
                  setFinalResults([]);
                  setEvaluationComplete(false);
                  setCurrentTest(null);
                  setError(null);
                }}
              >
                Start New Test
              </Button>
            </Box>

            {currentTest && (
              <>
                <Typography variant="h6" gutterBottom>
                  Current Test Results
                </Typography>
                <EvaluationResults test={currentTest} />
              </>
            )}

            <Box sx={{ my: 4 }}>
              {finalResults.map((result, index) => (
                <Box key={`${result.provider}:${result.modelId}`} sx={{ mb: 2 }}>
                  <Typography variant="h6" color={index === 0 ? 'primary' : 'textPrimary'}>
                    #{index + 1}: {result.provider}/{result.modelId}
                  </Typography>
                  <Typography variant="body1">
                    Average Rank: {result.averageRank.toFixed(2)}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Total Score: {result.totalScore}
                  </Typography>
                  {index < finalResults.length - 1 && <Divider sx={{ my: 1 }} />}
                </Box>
              ))}
            </Box>
            
            <Typography variant="h5" gutterBottom sx={{ mt: 4 }}>
              Previous Tests
            </Typography>
            
            {previousTests.length > 0 ? (
              <>
                <EvaluationTrends tests={previousTests} />
                {previousTests.map((test) => (
                  <EvaluationResults key={test.id} test={test} />
                ))}
              </>
            ) : (
              <Typography color="text.secondary">
                No previous tests found
              </Typography>
            )}
          </Box>
        );
    }
  };

  if (loadingModels) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Stepper activeStep={currentStep} sx={{ mb: 4 }}>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {renderStep()}

      {currentTest && (
        <>
          <Typography variant="h6" gutterBottom>
            Current Test Results
          </Typography>
          <EvaluationResults test={currentTest} />
        </>
      )}
    </Box>
  );
};

export default EvaluationTab; 
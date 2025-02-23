import React from 'react';
import { Box, Tabs, Tab, ThemeProvider, createTheme, CssBaseline } from '@mui/material';
import PlaygroundTab from './components/PlaygroundTab';
import EvaluationTab from './components/EvaluationTab';
import SettingsTab from './components/SettingsTab';
import { useTheme } from './hooks/useTheme';

const App: React.FC = () => {
  const [currentTab, setCurrentTab] = React.useState(0);
  const { theme } = useTheme();

  const muiTheme = React.useMemo(
    () =>
      createTheme({
        palette: {
          mode: theme === 'dark' ? 'dark' : 'light',
        },
      }),
    [theme]
  );

  const handleTabChange = (_: React.SyntheticEvent, newValue: number) => {
    setCurrentTab(newValue);
  };

  return (
    <ThemeProvider theme={muiTheme}>
      <CssBaseline />
      <Box sx={{ width: '100%', height: '100vh', display: 'flex', flexDirection: 'column' }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={currentTab} onChange={handleTabChange} aria-label="basic tabs example">
            <Tab label="Playground" />
            <Tab label="Evaluation" />
            <Tab label="Settings" />
          </Tabs>
        </Box>
        <Box sx={{ flexGrow: 1, overflow: 'auto', p: 2 }}>
          {currentTab === 0 && <PlaygroundTab />}
          {currentTab === 1 && <EvaluationTab />}
          {currentTab === 2 && <SettingsTab />}
        </Box>
      </Box>
    </ThemeProvider>
  );
};

export default App; 
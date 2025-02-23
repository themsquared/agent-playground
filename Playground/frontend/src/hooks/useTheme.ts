import { useState, useEffect } from 'react';

export const useTheme = () => {
  const [theme, setTheme] = useState<string>(() => {
    // Try to get theme from localStorage first
    const savedTheme = localStorage.getItem('theme');
    return savedTheme || 'dark';  // Default to dark theme
  });

  useEffect(() => {
    // Update localStorage when theme changes
    localStorage.setItem('theme', theme);
    // Update body class for global theme styling
    document.body.className = theme === 'dark' ? 'dark-theme' : 'light-theme';
  }, [theme]);

  return { theme, setTheme };
}; 
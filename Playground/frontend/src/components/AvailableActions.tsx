import React from 'react';
import {
  Paper,
  Typography,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  Box
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { Actions } from '../types';

interface AvailableActionsProps {
  actions: Actions;
}

export const AvailableActions: React.FC<AvailableActionsProps> = ({ actions }) => {
  if (!actions || Object.keys(actions).length === 0) {
    return null;
  }

  return (
    <Paper sx={{ p: 2, mb: 3 }}>
      <Typography variant="h6" gutterBottom>
        Available Actions
      </Typography>
      {Object.entries(actions).map(([actionName, info]) => (
        <Accordion key={actionName}>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography sx={{ fontWeight: 'bold' }}>
              {actionName}
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Box>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                {info.description}
              </Typography>
              <Typography variant="subtitle2" sx={{ mt: 1 }}>
                Required Parameters:
              </Typography>
              <List dense>
                {Object.entries(info.required_parameters).map(([param, desc]) => (
                  <ListItem key={param}>
                    <ListItemText
                      primary={param}
                      secondary={desc}
                      primaryTypographyProps={{
                        fontFamily: 'monospace',
                        fontWeight: 'bold'
                      }}
                    />
                  </ListItem>
                ))}
              </List>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Example usage:
              </Typography>
              <Box
                component="pre"
                sx={{
                  bgcolor: 'background.paper',
                  p: 1,
                  borderRadius: 1,
                  overflow: 'auto'
                }}
              >
                {JSON.stringify({
                  action: actionName,
                  parameters: Object.fromEntries(
                    Object.keys(info.required_parameters).map(param => [param, `<${param}>`])
                  )
                }, null, 2)}
              </Box>
            </Box>
          </AccordionDetails>
        </Accordion>
      ))}
    </Paper>
  );
}; 
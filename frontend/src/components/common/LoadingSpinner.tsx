import React from 'react';
import { CircularProgress, Box, Typography } from '@mui/material';

interface LoadingSpinnerProps {
  size?: 'small' | 'medium' | 'large';
  message?: string;
  backdrop?: boolean;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  size = 'medium', 
  message, 
  backdrop = false 
}) => {
  const sizeMap = {
    small: 20,
    medium: 40,
    large: 60
  };

  const content = (
    <Box display="flex" flexDirection="column" alignItems="center" gap={2}>
      <CircularProgress size={sizeMap[size]} />
      {message && (
        <Typography variant="body2" color="text.secondary">
          {message}
        </Typography>
      )}
    </Box>
  );

  if (backdrop) {
    return (
      <Box
        position="fixed"
        top={0}
        left={0}
        right={0}
        bottom={0}
        display="flex"
        alignItems="center"
        justifyContent="center"
        bgcolor="rgba(0, 0, 0, 0.5)"
        zIndex={9999}
      >
        {content}
      </Box>
    );
  }

  return content;
};

export default LoadingSpinner;
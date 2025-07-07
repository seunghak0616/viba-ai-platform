import React from 'react';
import { Container, Typography, Box } from '@mui/material';

const Profile: React.FC = () => {
  return (
    <Container maxWidth="md">
      <Box sx={{ textAlign: 'center', py: 8 }}>
        <Typography variant="h4" sx={{ fontWeight: 800, mb: 2 }}>
          사용자 프로필
        </Typography>
        <Typography variant="body1" color="textSecondary">
          프로필 페이지는 추후 구현 예정입니다.
        </Typography>
      </Box>
    </Container>
  );
};

export default Profile;
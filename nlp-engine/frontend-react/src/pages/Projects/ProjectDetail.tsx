import React from 'react';
import { Container, Typography, Box } from '@mui/material';
import { useParams } from 'react-router-dom';

const ProjectDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();

  return (
    <Container maxWidth="xl">
      <Box sx={{ textAlign: 'center', py: 8 }}>
        <Typography variant="h4" sx={{ fontWeight: 800, mb: 2 }}>
          프로젝트 상세 페이지
        </Typography>
        <Typography variant="h6" color="textSecondary">
          프로젝트 ID: {id}
        </Typography>
        <Typography variant="body1" color="textSecondary" sx={{ mt: 2 }}>
          상세 페이지는 추후 구현 예정입니다.
        </Typography>
      </Box>
    </Container>
  );
};

export default ProjectDetail;
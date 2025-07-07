import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  LinearProgress,
  Chip
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  TrendingFlat as TrendingFlatIcon
} from '@mui/icons-material';

interface ChartData {
  label: string;
  value: number;
  change: number;
  color: string;
}

interface ActivityChartProps {
  title?: string;
  data?: ChartData[];
}

const ActivityChart: React.FC<ActivityChartProps> = ({ 
  title = "프로젝트 활동 통계",
  data = [
    { label: "이번 주 작업시간", value: 85, change: 12, color: "#2196F3" },
    { label: "완료된 태스크", value: 92, change: 8, color: "#4CAF50" },
    { label: "팀 협업 점수", value: 78, change: -3, color: "#FF9800" },
    { label: "코드 품질", value: 95, change: 5, color: "#9C27B0" },
    { label: "고객 만족도", value: 88, change: 0, color: "#F44336" }
  ]
}) => {
  
  const getTrendIcon = (change: number) => {
    if (change > 0) return <TrendingUpIcon sx={{ fontSize: 16, color: 'success.main' }} />;
    if (change < 0) return <TrendingDownIcon sx={{ fontSize: 16, color: 'error.main' }} />;
    return <TrendingFlatIcon sx={{ fontSize: 16, color: 'text.secondary' }} />;
  };

  const getTrendColor = (change: number) => {
    if (change > 0) return 'success.main';
    if (change < 0) return 'error.main';
    return 'text.secondary';
  };

  return (
    <Paper elevation={2} sx={{ p: 3 }}>
      <Typography variant="h6" component="h2" gutterBottom>
        {title}
      </Typography>
      
      <Grid container spacing={3}>
        {data.map((item, index) => (
          <Grid item xs={12} key={index}>
            <Box mb={2}>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                <Typography variant="body2" color="text.secondary">
                  {item.label}
                </Typography>
                <Box display="flex" alignItems="center" gap={0.5}>
                  {getTrendIcon(item.change)}
                  <Typography 
                    variant="caption" 
                    color={getTrendColor(item.change)}
                    fontWeight="medium"
                  >
                    {Math.abs(item.change)}%
                  </Typography>
                </Box>
              </Box>
              
              <Box display="flex" alignItems="center" gap={2}>
                <Box flex={1}>
                  <LinearProgress
                    variant="determinate"
                    value={item.value}
                    sx={{
                      height: 8,
                      borderRadius: 4,
                      backgroundColor: 'grey.200',
                      '& .MuiLinearProgress-bar': {
                        backgroundColor: item.color,
                        borderRadius: 4,
                      },
                    }}
                  />
                </Box>
                <Typography variant="body2" fontWeight="medium" minWidth={40}>
                  {item.value}%
                </Typography>
              </Box>
            </Box>
          </Grid>
        ))}
      </Grid>

      {/* 시간별 활동 간단한 바 차트 시뮬레이션 */}
      <Box mt={4}>
        <Typography variant="subtitle2" gutterBottom>
          오늘의 활동 패턴
        </Typography>
        <Grid container spacing={1} alignItems="end" sx={{ height: 60 }}>
          {Array.from({ length: 24 }, (_, hour) => {
            const activity = Math.random() * 100;
            const isActiveHour = hour >= 9 && hour <= 18;
            const heightPercentage = isActiveHour ? activity : activity * 0.3;
            
            return (
              <Grid item xs={0.5} key={hour}>
                <Box
                  sx={{
                    height: `${heightPercentage}%`,
                    minHeight: '4px',
                    backgroundColor: isActiveHour ? '#2196F3' : '#E0E0E0',
                    borderRadius: '2px 2px 0 0',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      backgroundColor: isActiveHour ? '#1976D2' : '#BDBDBD',
                    }
                  }}
                  title={`${hour}:00 - ${Math.round(heightPercentage)}% 활동`}
                />
              </Grid>
            );
          })}
        </Grid>
        <Box display="flex" justifyContent="space-between" mt={1}>
          <Typography variant="caption" color="text.secondary">0시</Typography>
          <Typography variant="caption" color="text.secondary">12시</Typography>
          <Typography variant="caption" color="text.secondary">24시</Typography>
        </Box>
      </Box>
    </Paper>
  );
};

export default ActivityChart;
import React, { useState } from 'react';
import {
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  Avatar,
  Chip,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
  Alert,
  Tab,
  Tabs,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Divider,
} from '@mui/material';
import {
  Architecture,
  Engineering,
  Palette,
  Analytics,
  AccountBalance,
  Schedule,
  Smart,
  Send,
  AutoAwesome,
  Psychology,
  Science,
} from '@mui/icons-material';
import { useAuth } from '../../contexts/AuthContext';
import { aiAPI, wsManager } from '../../services/api';

interface AIAgent {
  id: string;
  name: string;
  description: string;
  capabilities: string[];
  icon: React.ReactNode;
  color: string;
  status: 'active' | 'busy' | 'offline';
  specialty: string;
  experience: string;
}

interface ChatMessage {
  id: string;
  sender: 'user' | 'agent';
  content: string;
  timestamp: Date;
  agentId?: string;
}

const AIAgents: React.FC = () => {
  const { state } = useAuth();
  const [selectedTab, setSelectedTab] = useState(0);
  const [selectedAgent, setSelectedAgent] = useState<AIAgent | null>(null);
  const [chatOpen, setChatOpen] = useState(false);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);

  // VIBA AI 에이전트들
  const aiAgents: AIAgent[] = [
    {
      id: 'materials_specialist',
      name: '재료 전문가 AI',
      description: '건축 재료 선택과 친환경 솔루션을 제안하는 전문 AI입니다.',
      capabilities: ['친환경 재료 추천', '비용 최적화', '성능 분석', '지속가능성 평가'],
      icon: <Science />,
      color: '#10b981',
      status: 'active',
      specialty: '재료 공학',
      experience: '10,000+ 프로젝트 경험',
    },
    {
      id: 'design_theorist',
      name: '설계 이론가 AI',
      description: '건축 설계 이론과 공간 구성을 전문으로 하는 AI입니다.',
      capabilities: ['공간 설계', '비례 시스템', '동선 계획', '기능성 분석'],
      icon: <Architecture />,
      color: '#2563eb',
      status: 'active',
      specialty: '설계 이론',
      experience: '5,000+ 설계 분석',
    },
    {
      id: 'bim_specialist',
      name: 'BIM 전문가 AI',
      description: 'BIM 모델링과 3D 설계를 담당하는 전문 AI입니다.',
      capabilities: ['3D 모델링', 'IFC 변환', '충돌 검사', '시공성 검토'],
      icon: <Smart />,
      color: '#8b5cf6',
      status: 'active',
      specialty: 'BIM 모델링',
      experience: '2,000+ BIM 모델',
    },
    {
      id: 'structural_engineer',
      name: '구조 엔지니어 AI',
      description: '구조 계산과 안전성 검토를 수행하는 AI입니다.',
      capabilities: ['구조 계산', '안전성 검토', '내진 설계', '하중 분석'],
      icon: <Engineering />,
      color: '#f59e0b',
      status: 'busy',
      specialty: '구조 공학',
      experience: '15,000+ 구조 해석',
    },
    {
      id: 'mep_specialist',
      name: 'MEP 전문가 AI',
      description: '기계/전기/배관 시스템을 설계하는 전문 AI입니다.',
      capabilities: ['HVAC 설계', '전기 시스템', '배관 계획', '에너지 분석'],
      icon: <AccountBalance />,
      color: '#ef4444',
      status: 'active',
      specialty: 'MEP 시스템',
      experience: '8,000+ MEP 설계',
    },
    {
      id: 'cost_estimator',
      name: '비용 추정 AI',
      description: '정확한 공사비 산출과 예산 관리를 담당하는 AI입니다.',
      capabilities: ['공사비 산출', '예산 관리', '가치 공학', '시장 분석'],
      icon: <Analytics />,
      color: '#06b6d4',
      status: 'active',
      specialty: '건설 경제',
      experience: '20,000+ 견적 분석',
    },
    {
      id: 'schedule_manager',
      name: '일정 관리 AI',
      description: '프로젝트 일정과 리소스를 최적화하는 AI입니다.',
      capabilities: ['일정 계획', '리소스 배분', '공정 관리', '위험 분석'],
      icon: <Schedule />,
      color: '#84cc16',
      status: 'active',
      specialty: '프로젝트 관리',
      experience: '5,000+ 프로젝트 관리',
    },
    {
      id: 'interior_designer',
      name: '인테리어 디자인 AI',
      description: '공간 디자인과 인테리어 계획을 담당하는 AI입니다.',
      capabilities: ['공간 계획', '색채 설계', '조명 계획', '가구 배치'],
      icon: <Palette />,
      color: '#ec4899',
      status: 'active',
      specialty: '인테리어 디자인',
      experience: '3,000+ 인테리어 설계',
    },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return '#10b981';
      case 'busy':
        return '#f59e0b';
      case 'offline':
        return '#6b7280';
      default:
        return '#6b7280';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active':
        return '활성';
      case 'busy':
        return '작업중';
      case 'offline':
        return '오프라인';
      default:
        return '알수없음';
    }
  };

  const handleAgentChat = (agent: AIAgent) => {
    setSelectedAgent(agent);
    setChatOpen(true);
    // 환영 메시지 추가
    const welcomeMessage: ChatMessage = {
      id: Date.now().toString(),
      sender: 'agent',
      content: `안녕하세요! 저는 ${agent.name}입니다. ${agent.description} 어떤 도움이 필요하신가요?`,
      timestamp: new Date(),
      agentId: agent.id,
    };
    setChatMessages([welcomeMessage]);
  };

  const handleSendMessage = async () => {
    if (!newMessage.trim() || !selectedAgent) return;

    // 사용자 메시지 추가
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      sender: 'user',
      content: newMessage,
      timestamp: new Date(),
    };

    setChatMessages(prev => [...prev, userMessage]);
    setNewMessage('');
    setIsProcessing(true);

    try {
      // 실제 API 호출 - 세션이 없으면 새로 시작
      let sessionId = localStorage.getItem(`ai_session_${selectedAgent.id}`);
      
      if (!sessionId) {
        const sessionResponse = await aiAPI.startChatSession(selectedAgent.id);
        sessionId = sessionResponse.session_id;
        localStorage.setItem(`ai_session_${selectedAgent.id}`, sessionId);
      }

      // 메시지 전송
      const response = await aiAPI.sendMessage(sessionId, newMessage);

      // AI 응답 추가
      const agentResponse: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: 'agent',
        content: response.response,
        timestamp: new Date(response.timestamp),
        agentId: selectedAgent.id,
      };

      setChatMessages(prev => [...prev, agentResponse]);
    } catch (error) {
      console.error('메시지 전송 실패:', error);
      
      // 에러 메시지 추가
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: 'agent',
        content: '죄송합니다. 현재 AI 에이전트에 연결할 수 없습니다. 잠시 후 다시 시도해주세요.',
        timestamp: new Date(),
        agentId: selectedAgent.id,
      };
      setChatMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsProcessing(false);
    }
  };

  const TabPanel: React.FC<{ children: React.ReactNode; value: number; index: number }> = ({
    children,
    value,
    index,
  }) => {
    return (
      <div role="tabpanel" hidden={value !== index}>
        {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
      </div>
    );
  };

  return (
    <Container maxWidth="xl">
      {/* 헤더 */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 800, mb: 1 }}>
          VIBA AI 에이전트 센터 🤖
        </Typography>
        <Typography variant="h6" color="textSecondary">
          전문 AI 에이전트들과 협업하여 완벽한 건축 설계를 완성하세요
        </Typography>
      </Box>

      {/* 탭 네비게이션 */}
      <Paper sx={{ mb: 3, borderRadius: 2 }}>
        <Tabs
          value={selectedTab}
          onChange={(_, newValue) => setSelectedTab(newValue)}
          sx={{ px: 2 }}
        >
          <Tab label="모든 에이전트" />
          <Tab label="활성 에이전트" />
          <Tab label="최근 대화" />
        </Tabs>
      </Paper>

      {/* 탭 컨텐츠 */}
      <TabPanel value={selectedTab} index={0}>
        {/* 모든 에이전트 */}
        <Grid container spacing={3}>
          {aiAgents.map((agent) => (
            <Grid item xs={12} sm={6} lg={4} key={agent.id}>
              <Card
                sx={{
                  height: '100%',
                  border: 'none',
                  borderRadius: 3,
                  boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
                  '&:hover': {
                    boxShadow: '0 8px 25px rgba(0,0,0,0.15)',
                    transform: 'translateY(-4px)',
                  },
                  transition: 'all 0.3s ease',
                }}
              >
                <CardContent sx={{ p: 3 }}>
                  {/* 에이전트 헤더 */}
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Avatar
                      sx={{
                        width: 56,
                        height: 56,
                        bgcolor: `${agent.color}15`,
                        color: agent.color,
                        mr: 2,
                      }}
                    >
                      {agent.icon}
                    </Avatar>
                    <Box sx={{ flexGrow: 1 }}>
                      <Typography variant="h6" sx={{ fontWeight: 700, mb: 0.5 }}>
                        {agent.name}
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Box
                          sx={{
                            width: 8,
                            height: 8,
                            borderRadius: '50%',
                            bgcolor: getStatusColor(agent.status),
                          }}
                        />
                        <Typography variant="caption" color="textSecondary">
                          {getStatusText(agent.status)}
                        </Typography>
                      </Box>
                    </Box>
                  </Box>

                  {/* 설명 */}
                  <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                    {agent.description}
                  </Typography>

                  {/* 전문 분야 */}
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 600 }}>
                      전문 분야
                    </Typography>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>
                      {agent.specialty}
                    </Typography>
                  </Box>

                  {/* 경험 */}
                  <Box sx={{ mb: 3 }}>
                    <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 600 }}>
                      경험
                    </Typography>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>
                      {agent.experience}
                    </Typography>
                  </Box>

                  {/* 능력 태그들 */}
                  <Box sx={{ mb: 3 }}>
                    <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 600, mb: 1, display: 'block' }}>
                      주요 능력
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {agent.capabilities.slice(0, 3).map((capability, index) => (
                        <Chip
                          key={index}
                          label={capability}
                          size="small"
                          sx={{
                            bgcolor: `${agent.color}10`,
                            color: agent.color,
                            fontWeight: 500,
                            fontSize: '0.75rem',
                          }}
                        />
                      ))}
                      {agent.capabilities.length > 3 && (
                        <Chip
                          label={`+${agent.capabilities.length - 3}개`}
                          size="small"
                          variant="outlined"
                          sx={{ fontSize: '0.75rem' }}
                        />
                      )}
                    </Box>
                  </Box>

                  {/* 액션 버튼 */}
                  <Button
                    fullWidth
                    variant="contained"
                    startIcon={<Psychology />}
                    onClick={() => handleAgentChat(agent)}
                    disabled={agent.status === 'offline'}
                    sx={{
                      background: `linear-gradient(135deg, ${agent.color} 0%, ${agent.color}dd 100%)`,
                      fontWeight: 600,
                      borderRadius: 2,
                      '&:hover': {
                        background: `linear-gradient(135deg, ${agent.color}dd 0%, ${agent.color}bb 100%)`,
                      },
                    }}
                  >
                    AI와 대화하기
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </TabPanel>

      <TabPanel value={selectedTab} index={1}>
        {/* 활성 에이전트만 */}
        <Grid container spacing={3}>
          {aiAgents
            .filter((agent) => agent.status === 'active')
            .map((agent) => (
              <Grid item xs={12} sm={6} lg={4} key={agent.id}>
                <Card
                  sx={{
                    height: '100%',
                    border: `2px solid ${agent.color}20`,
                    borderRadius: 3,
                    boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
                  }}
                >
                  <CardContent sx={{ p: 3, textAlign: 'center' }}>
                    <Avatar
                      sx={{
                        width: 80,
                        height: 80,
                        bgcolor: `${agent.color}15`,
                        color: agent.color,
                        mx: 'auto',
                        mb: 2,
                      }}
                    >
                      {agent.icon}
                    </Avatar>
                    <Typography variant="h6" sx={{ fontWeight: 700, mb: 1 }}>
                      {agent.name}
                    </Typography>
                    <Chip
                      label="활성"
                      color="success"
                      size="small"
                      sx={{ mb: 2, fontWeight: 600 }}
                    />
                    <Button
                      fullWidth
                      variant="contained"
                      onClick={() => handleAgentChat(agent)}
                      sx={{
                        background: `linear-gradient(135deg, ${agent.color} 0%, ${agent.color}dd 100%)`,
                        fontWeight: 600,
                        borderRadius: 2,
                      }}
                    >
                      즉시 상담
                    </Button>
                  </CardContent>
                </Card>
              </Grid>
            ))}
        </Grid>
      </TabPanel>

      <TabPanel value={selectedTab} index={2}>
        {/* 최근 대화 */}
        <Card sx={{ borderRadius: 3 }}>
          <CardContent sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ fontWeight: 700, mb: 3 }}>
              최근 AI 에이전트 대화
            </Typography>
            <List>
              {aiAgents.slice(0, 5).map((agent, index) => (
                <React.Fragment key={agent.id}>
                  <ListItem>
                    <ListItemAvatar>
                      <Avatar sx={{ bgcolor: `${agent.color}15`, color: agent.color }}>
                        {agent.icon}
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={agent.name}
                      secondary={`마지막 대화: ${Math.floor(Math.random() * 60)}분 전`}
                    />
                    <Button
                      variant="outlined"
                      size="small"
                      onClick={() => handleAgentChat(agent)}
                      sx={{ borderRadius: 2, fontWeight: 500 }}
                    >
                      계속 대화
                    </Button>
                  </ListItem>
                  {index < 4 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          </CardContent>
        </Card>
      </TabPanel>

      {/* AI 채팅 다이얼로그 */}
      <Dialog
        open={chatOpen}
        onClose={() => setChatOpen(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: { borderRadius: 3, height: '80vh' },
        }}
      >
        <DialogTitle sx={{ pb: 2, borderBottom: '1px solid #e2e8f0' }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            {selectedAgent && (
              <>
                <Avatar
                  sx={{
                    width: 40,
                    height: 40,
                    bgcolor: `${selectedAgent.color}15`,
                    color: selectedAgent.color,
                    mr: 2,
                  }}
                >
                  {selectedAgent.icon}
                </Avatar>
                <Box>
                  <Typography variant="h6" sx={{ fontWeight: 700 }}>
                    {selectedAgent.name}
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    {selectedAgent.specialty} • {getStatusText(selectedAgent.status)}
                  </Typography>
                </Box>
              </>
            )}
          </Box>
        </DialogTitle>

        <DialogContent sx={{ p: 0, display: 'flex', flexDirection: 'column', height: '100%' }}>
          {/* 메시지 영역 */}
          <Box sx={{ flexGrow: 1, p: 2, overflowY: 'auto' }}>
            {chatMessages.map((message) => (
              <Box
                key={message.id}
                sx={{
                  display: 'flex',
                  justifyContent: message.sender === 'user' ? 'flex-end' : 'flex-start',
                  mb: 2,
                }}
              >
                <Paper
                  sx={{
                    p: 2,
                    maxWidth: '70%',
                    bgcolor: message.sender === 'user' ? '#2563eb' : '#f8fafc',
                    color: message.sender === 'user' ? 'white' : 'inherit',
                    borderRadius: 3,
                  }}
                >
                  <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                    {message.content}
                  </Typography>
                  <Typography
                    variant="caption"
                    sx={{
                      display: 'block',
                      mt: 1,
                      opacity: 0.7,
                    }}
                  >
                    {message.timestamp.toLocaleTimeString('ko-KR', {
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </Typography>
                </Paper>
              </Box>
            ))}
            {isProcessing && (
              <Box sx={{ display: 'flex', justifyContent: 'flex-start', mb: 2 }}>
                <Paper sx={{ p: 2, bgcolor: '#f8fafc', borderRadius: 3 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <CircularProgress size={16} />
                    <Typography variant="body2">
                      {selectedAgent?.name}이(가) 응답을 준비 중입니다...
                    </Typography>
                  </Box>
                </Paper>
              </Box>
            )}
          </Box>

          {/* 입력 영역 */}
          <Box sx={{ p: 2, borderTop: '1px solid #e2e8f0' }}>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <TextField
                fullWidth
                placeholder="AI 에이전트에게 질문하세요..."
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSendMessage();
                  }
                }}
                multiline
                maxRows={3}
                disabled={isProcessing}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: 3,
                  },
                }}
              />
              <Button
                variant="contained"
                onClick={handleSendMessage}
                disabled={!newMessage.trim() || isProcessing}
                sx={{
                  minWidth: 56,
                  height: 56,
                  borderRadius: 3,
                  background: selectedAgent
                    ? `linear-gradient(135deg, ${selectedAgent.color} 0%, ${selectedAgent.color}dd 100%)`
                    : undefined,
                }}
              >
                <Send />
              </Button>
            </Box>
          </Box>
        </DialogContent>
      </Dialog>
    </Container>
  );
};

export default AIAgents;
import React, { useState, useCallback } from 'react';
import {
  Box,
  Paper,
  Typography,
  LinearProgress,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Chip,
  Alert,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  CloudUpload,
  InsertDriveFile,
  CheckCircle,
  Error,
  Delete,
  Visibility,
  GetApp,
  Architecture,
  Image,
  PictureAsPdf,
  TableChart,
  Archive,
  Description,
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';

interface FileUploadProps {
  projectId: string;
  onUploadComplete?: (files: UploadedFile[]) => void;
  maxFiles?: number;
  acceptedFormats?: string[];
}

interface UploadedFile {
  file_id: string;
  filename: string;
  file_type: string;
  file_size: number;
  status: 'uploading' | 'processing' | 'completed' | 'failed';
  progress: number;
  error?: string;
}

const FileUpload: React.FC<FileUploadProps> = ({
  projectId,
  onUploadComplete,
  maxFiles = 10,
  acceptedFormats = [
    '.ifc', '.ifcxml',
    '.dwg', '.dxf',
    '.pdf',
    '.jpg', '.jpeg', '.png', '.gif', '.bmp',
    '.xlsx', '.xls', '.csv',
    '.doc', '.docx', '.txt',
    '.zip', '.rar', '.7z'
  ],
}) => {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [detailsDialog, setDetailsDialog] = useState<{open: boolean; file?: UploadedFile}>({open: false});

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;
    
    setIsUploading(true);

    // 파일 업로드 준비
    const newFiles: UploadedFile[] = acceptedFiles.map(file => ({
      file_id: `temp-${Date.now()}-${Math.random()}`,
      filename: file.name,
      file_type: getFileType(file.name),
      file_size: file.size,
      status: 'uploading' as const,
      progress: 0,
    }));

    setUploadedFiles(prev => [...prev, ...newFiles]);

    // 각 파일 업로드
    for (let i = 0; i < acceptedFiles.length; i++) {
      const file = acceptedFiles[i];
      const tempId = newFiles[i].file_id;

      try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await axios.post(
          `/api/files/upload/${projectId}`,
          formData,
          {
            headers: {
              'Content-Type': 'multipart/form-data',
              'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
            },
            onUploadProgress: (progressEvent) => {
              const progress = Math.round((progressEvent.loaded * 100) / (progressEvent.total || 1));
              updateFileProgress(tempId, progress);
            },
          }
        );

        // 업로드 성공
        const { file_id, status } = response.data;
        updateFileStatus(tempId, {
          file_id,
          status: 'processing',
          progress: 100,
        });

        // 처리 상태 모니터링
        monitorFileProcessing(file_id);

      } catch (error: any) {
        console.error('파일 업로드 실패:', error);
        updateFileStatus(tempId, {
          status: 'failed',
          error: error.response?.data?.detail || '업로드 실패',
        });
      }
    }

    setIsUploading(false);
  }, [projectId]);

  const updateFileProgress = (fileId: string, progress: number) => {
    setUploadedFiles(prev => prev.map(file => 
      file.file_id === fileId ? { ...file, progress } : file
    ));
  };

  const updateFileStatus = (fileId: string, updates: Partial<UploadedFile>) => {
    setUploadedFiles(prev => prev.map(file => 
      file.file_id === fileId ? { ...file, ...updates } : file
    ));
  };

  const monitorFileProcessing = async (fileId: string) => {
    const checkInterval = setInterval(async () => {
      try {
        const response = await axios.get(`/api/files/status/${fileId}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
          },
        });

        const { status, processing_details } = response.data;

        if (status === 'completed' || status === 'failed') {
          clearInterval(checkInterval);
          updateFileStatus(fileId, {
            status,
            ...(processing_details && { processing_details }),
          });

          if (onUploadComplete) {
            onUploadComplete(uploadedFiles.filter(f => f.file_id === fileId));
          }
        }
      } catch (error) {
        console.error('파일 상태 확인 실패:', error);
        clearInterval(checkInterval);
      }
    }, 2000); // 2초마다 확인
  };

  const getFileType = (filename: string): string => {
    const ext = filename.split('.').pop()?.toLowerCase() || '';
    if (['ifc', 'ifcxml'].includes(ext)) return 'bim';
    if (['dwg', 'dxf'].includes(ext)) return 'cad';
    if (ext === 'pdf') return 'pdf';
    if (['jpg', 'jpeg', 'png', 'gif', 'bmp'].includes(ext)) return 'image';
    if (['xlsx', 'xls', 'csv'].includes(ext)) return 'spreadsheet';
    if (['doc', 'docx', 'txt'].includes(ext)) return 'document';
    if (['zip', 'rar', '7z'].includes(ext)) return 'archive';
    return 'other';
  };

  const getFileIcon = (fileType: string) => {
    switch (fileType) {
      case 'bim':
        return <Architecture sx={{ color: '#2563eb' }} />;
      case 'cad':
        return <Architecture sx={{ color: '#8b5cf6' }} />;
      case 'pdf':
        return <PictureAsPdf sx={{ color: '#ef4444' }} />;
      case 'image':
        return <Image sx={{ color: '#10b981' }} />;
      case 'spreadsheet':
        return <TableChart sx={{ color: '#06b6d4' }} />;
      case 'document':
        return <Description sx={{ color: '#f59e0b' }} />;
      case 'archive':
        return <Archive sx={{ color: '#6b7280' }} />;
      default:
        return <InsertDriveFile sx={{ color: '#6b7280' }} />;
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const handleDelete = async (fileId: string) => {
    try {
      await axios.delete(`/api/files/${fileId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      });
      setUploadedFiles(prev => prev.filter(file => file.file_id !== fileId));
    } catch (error) {
      console.error('파일 삭제 실패:', error);
    }
  };

  const handleDownload = async (fileId: string, filename: string) => {
    try {
      const response = await axios.get(`/api/files/download/${fileId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        responseType: 'blob',
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('파일 다운로드 실패:', error);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: acceptedFormats.reduce((acc, format) => ({
      ...acc,
      [`application/${format.slice(1)}`]: [format],
    }), {}),
    maxFiles,
  });

  return (
    <Box>
      {/* 드롭존 */}
      <Paper
        {...getRootProps()}
        sx={{
          p: 4,
          mb: 3,
          border: '2px dashed',
          borderColor: isDragActive ? 'primary.main' : 'grey.300',
          borderRadius: 2,
          bgcolor: isDragActive ? 'primary.50' : 'background.paper',
          cursor: 'pointer',
          textAlign: 'center',
          transition: 'all 0.3s ease',
          '&:hover': {
            borderColor: 'primary.main',
            bgcolor: 'grey.50',
          },
        }}
      >
        <input {...getInputProps()} />
        <CloudUpload sx={{ fontSize: 48, color: 'grey.500', mb: 2 }} />
        <Typography variant="h6" sx={{ mb: 1 }}>
          {isDragActive ? '파일을 놓으세요' : '파일을 드래그하거나 클릭하여 업로드'}
        </Typography>
        <Typography variant="body2" color="textSecondary">
          최대 {maxFiles}개 파일 • 지원 형식: IFC, DWG, PDF, 이미지 등
        </Typography>
      </Paper>

      {/* 업로드된 파일 목록 */}
      {uploadedFiles.length > 0 && (
        <Paper sx={{ p: 2, borderRadius: 2 }}>
          <Typography variant="h6" sx={{ mb: 2 }}>
            업로드된 파일
          </Typography>
          <List>
            {uploadedFiles.map((file, index) => (
              <React.Fragment key={file.file_id}>
                <ListItem>
                  <ListItemIcon>
                    {getFileIcon(file.file_type)}
                  </ListItemIcon>
                  <ListItemText
                    primary={file.filename}
                    secondary={
                      <Box sx={{ mt: 1 }}>
                        <Typography variant="caption" color="textSecondary">
                          {formatFileSize(file.file_size)}
                        </Typography>
                        {file.status === 'uploading' && (
                          <LinearProgress
                            variant="determinate"
                            value={file.progress}
                            sx={{ mt: 1, height: 4, borderRadius: 2 }}
                          />
                        )}
                        {file.status === 'processing' && (
                          <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                            <LinearProgress sx={{ flexGrow: 1, height: 4, borderRadius: 2 }} />
                            <Typography variant="caption" sx={{ ml: 1 }}>
                              처리 중...
                            </Typography>
                          </Box>
                        )}
                      </Box>
                    }
                  />
                  <ListItemSecondaryAction>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      {file.status === 'completed' && (
                        <Chip
                          icon={<CheckCircle />}
                          label="완료"
                          color="success"
                          size="small"
                        />
                      )}
                      {file.status === 'failed' && (
                        <Chip
                          icon={<Error />}
                          label="실패"
                          color="error"
                          size="small"
                        />
                      )}
                      {file.status === 'completed' && (
                        <>
                          <IconButton
                            size="small"
                            onClick={() => setDetailsDialog({ open: true, file })}
                          >
                            <Visibility />
                          </IconButton>
                          <IconButton
                            size="small"
                            onClick={() => handleDownload(file.file_id, file.filename)}
                          >
                            <GetApp />
                          </IconButton>
                        </>
                      )}
                      <IconButton
                        size="small"
                        onClick={() => handleDelete(file.file_id)}
                        disabled={file.status === 'uploading'}
                      >
                        <Delete />
                      </IconButton>
                    </Box>
                  </ListItemSecondaryAction>
                </ListItem>
                {index < uploadedFiles.length - 1 && <Box sx={{ borderBottom: '1px solid #e2e8f0', mx: 2 }} />}
              </React.Fragment>
            ))}
          </List>
        </Paper>
      )}

      {/* 파일 상세 정보 다이얼로그 */}
      <Dialog
        open={detailsDialog.open}
        onClose={() => setDetailsDialog({ open: false })}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>파일 상세 정보</DialogTitle>
        <DialogContent>
          {detailsDialog.file && (
            <Box>
              <Typography variant="subtitle2" gutterBottom>
                파일명: {detailsDialog.file.filename}
              </Typography>
              <Typography variant="body2" color="textSecondary" gutterBottom>
                타입: {detailsDialog.file.file_type} • 크기: {formatFileSize(detailsDialog.file.file_size)}
              </Typography>
              {detailsDialog.file.error && (
                <Alert severity="error" sx={{ mt: 2 }}>
                  {detailsDialog.file.error}
                </Alert>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailsDialog({ open: false })}>
            닫기
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default FileUpload;
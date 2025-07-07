/**
 * BIM 객체 인스펙터 컴포넌트
 * 선택된 3D 객체의 속성 및 정보 표시
 */
import React, { useMemo } from 'react';
import {
  Paper,
  Typography,
  IconButton,
  Box,
  Divider,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  ListItemIcon
} from '@mui/material';
import {
  Close as CloseIcon,
  ExpandMore as ExpandMoreIcon,
  Info as InfoIcon,
  Architecture as ArchitectureIcon,
  Straighten as StraightenIcon,
  Palette as PaletteIcon,
  Category as CategoryIcon
} from '@mui/icons-material';

interface BimObject {
  id: string;
  name: string;
  type: string;
  mesh: any; // Babylon.js Mesh
  properties: Record<string, any>;
  metadata: Record<string, any>;
}

interface BimObjectInspectorProps {
  bimObject: BimObject;
  onClose: () => void;
  className?: string;
}

interface PropertyGroup {
  title: string;
  icon: React.ReactNode;
  properties: Array<{
    key: string;
    label: string;
    value: any;
    unit?: string;
    type?: 'text' | 'number' | 'boolean' | 'area' | 'length' | 'volume';
  }>;
}

/**
 * BIM 객체 인스펙터 컴포넌트
 */
const BimObjectInspector: React.FC<BimObjectInspectorProps> = ({
  bimObject,
  onClose,
  className
}) => {
  /**
   * 속성 그룹 생성
   */
  const propertyGroups = useMemo((): PropertyGroup[] => {
    const groups: PropertyGroup[] = [];

    // 기본 정보
    groups.push({
      title: '기본 정보',
      icon: <InfoIcon />,
      properties: [
        {
          key: 'id',
          label: 'ID',
          value: bimObject.id,
          type: 'text'
        },
        {
          key: 'name',
          label: '이름',
          value: bimObject.name,
          type: 'text'
        },
        {
          key: 'type',
          label: '타입',
          value: bimObject.type,
          type: 'text'
        }
      ]
    });

    // 치수 정보
    if (bimObject.properties.width || bimObject.properties.height || bimObject.properties.area) {
      groups.push({
        title: '치수 정보',
        icon: <StraightenIcon />,
        properties: [
          ...(bimObject.properties.width ? [{
            key: 'width',
            label: '너비',
            value: bimObject.properties.width,
            unit: 'm',
            type: 'length' as const
          }] : []),
          ...(bimObject.properties.depth ? [{
            key: 'depth',
            label: '깊이',
            value: bimObject.properties.depth,
            unit: 'm',
            type: 'length' as const
          }] : []),
          ...(bimObject.properties.height ? [{
            key: 'height',
            label: '높이',
            value: bimObject.properties.height,
            unit: 'm',
            type: 'length' as const
          }] : []),
          ...(bimObject.properties.area ? [{
            key: 'area',
            label: '면적',
            value: bimObject.properties.area,
            unit: '㎡',
            type: 'area' as const
          }] : [])
        ]
      });
    }

    // 건축 정보
    const architecturalProps = [];
    if (bimObject.properties.orientation) {
      architecturalProps.push({
        key: 'orientation',
        label: '방향',
        value: bimObject.properties.orientation,
        type: 'text' as const
      });
    }

    if (architecturalProps.length > 0) {
      groups.push({
        title: '건축 정보',
        icon: <ArchitectureIcon />,
        properties: architecturalProps
      });
    }

    // 재료 정보 (추후 확장)
    if (bimObject.mesh?.material) {
      groups.push({
        title: '재료 정보',
        icon: <PaletteIcon />,
        properties: [
          {
            key: 'material',
            label: '재료',
            value: bimObject.mesh.material.name || 'Standard Material',
            type: 'text'
          }
        ]
      });
    }

    return groups.filter(group => group.properties.length > 0);
  }, [bimObject]);

  /**
   * 값 포맷팅
   */
  const formatValue = (value: any, type?: string, unit?: string): string => {
    if (value === null || value === undefined) return 'N/A';

    switch (type) {
      case 'number':
      case 'length':
      case 'area':
      case 'volume':
        const numValue = typeof value === 'number' ? value : parseFloat(value);
        if (isNaN(numValue)) return 'N/A';
        
        const formatted = numValue.toFixed(2);
        return unit ? `${formatted} ${unit}` : formatted;

      case 'boolean':
        return value ? '예' : '아니오';

      case 'text':
      default:
        return String(value);
    }
  };

  /**
   * 타입별 칩 색상
   */
  const getTypeChipColor = (type: string): 'primary' | 'secondary' | 'default' | 'error' | 'info' | 'success' | 'warning' => {
    switch (type.toLowerCase()) {
      case 'room':
        return 'primary';
      case 'wall':
        return 'secondary';
      case 'door':
        return 'success';
      case 'window':
        return 'info';
      case 'floor':
        return 'warning';
      default:
        return 'default';
    }
  };

  return (
    <Paper
      elevation={4}
      className={className}
      sx={{
        width: 320,
        maxHeight: '80vh',
        overflow: 'auto',
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        backdropFilter: 'blur(10px)'
      }}
    >
      {/* 헤더 */}
      <Box sx={{ p: 2, pb: 1, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <CategoryIcon color="primary" />
          <Typography variant="h6" component="div">
            객체 정보
          </Typography>
        </Box>
        <IconButton size="small" onClick={onClose}>
          <CloseIcon />
        </IconButton>
      </Box>

      {/* 객체 타입 칩 */}
      <Box sx={{ px: 2, pb: 1 }}>
        <Chip
          label={bimObject.type}
          color={getTypeChipColor(bimObject.type)}
          size="small"
          variant="outlined"
        />
      </Box>

      <Divider />

      {/* 속성 그룹들 */}
      <Box sx={{ p: 0 }}>
        {propertyGroups.map((group, groupIndex) => (
          <Accordion key={groupIndex} defaultExpanded>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                {group.icon}
                <Typography variant="subtitle2">
                  {group.title}
                </Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails sx={{ pt: 0 }}>
              <TableContainer>
                <Table size="small">
                  <TableBody>
                    {group.properties.map((property, propIndex) => (
                      <TableRow key={propIndex}>
                        <TableCell 
                          component="th" 
                          scope="row"
                          sx={{ 
                            border: 'none',
                            py: 0.5,
                            width: '40%',
                            fontSize: '0.8rem'
                          }}
                        >
                          {property.label}
                        </TableCell>
                        <TableCell 
                          sx={{ 
                            border: 'none',
                            py: 0.5,
                            fontSize: '0.8rem',
                            fontWeight: 'medium'
                          }}
                        >
                          {formatValue(property.value, property.type, property.unit)}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </AccordionDetails>
          </Accordion>
        ))}
      </Box>

      {/* 메타데이터 (개발 모드에서만 표시) */}
      {import.meta.env.DEV && Object.keys(bimObject.metadata).length > 0 && (
        <>
          <Divider />
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="subtitle2" color="text.secondary">
                메타데이터 (개발용)
              </Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Box sx={{ maxHeight: 200, overflow: 'auto' }}>
                <Typography 
                  variant="caption" 
                  component="pre"
                  sx={{ 
                    whiteSpace: 'pre-wrap',
                    wordBreak: 'break-all',
                    fontSize: '0.7rem',
                    fontFamily: 'monospace'
                  }}
                >
                  {JSON.stringify(bimObject.metadata, null, 2)}
                </Typography>
              </Box>
            </AccordionDetails>
          </Accordion>
        </>
      )}

      {/* 푸터 */}
      <Box sx={{ p: 1, borderTop: 1, borderColor: 'divider' }}>
        <Typography variant="caption" color="text.secondary" align="center" display="block">
          클릭하여 다른 객체 선택
        </Typography>
      </Box>
    </Paper>
  );
};

export default BimObjectInspector;
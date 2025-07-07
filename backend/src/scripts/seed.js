import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcryptjs';

const prisma = new PrismaClient();

async function main() {
  console.log('🌱 시드 데이터 생성 시작...');

  // 1. 관리자 사용자 생성
  const adminPassword = await bcrypt.hash('Admin123!', 12);
  const admin = await prisma.user.upsert({
    where: { email: 'admin@bim-platform.com' },
    update: {},
    create: {
      email: 'admin@bim-platform.com',
      password: adminPassword,
      name: '관리자',
      company: 'BIM 플랫폼',
      role: 'ADMIN',
      isActive: true
    }
  });
  console.log('✅ 관리자 사용자 생성:', admin.email);

  // 2. 건축가 사용자 생성
  const architectPassword = await bcrypt.hash('Architect123!', 12);
  const architect = await prisma.user.upsert({
    where: { email: 'architect@example.com' },
    update: {},
    create: {
      email: 'architect@example.com',
      password: architectPassword,
      name: '김건축',
      company: '건축사사무소 ABC',
      role: 'ARCHITECT',
      isActive: true
    }
  });
  console.log('✅ 건축가 사용자 생성:', architect.email);

  // 3. 프리미엄 사용자 생성
  const premiumPassword = await bcrypt.hash('Premium123!', 12);
  const premium = await prisma.user.upsert({
    where: { email: 'premium@example.com' },
    update: {},
    create: {
      email: 'premium@example.com',
      password: premiumPassword,
      name: '이프리',
      company: '프리미엄 건설',
      role: 'PREMIUM',
      isActive: true
    }
  });
  console.log('✅ 프리미엄 사용자 생성:', premium.email);

  // 4. 샘플 프로젝트 생성
  const existingProject1 = await prisma.project.findFirst({
    where: { 
      name: '강남 오피스 빌딩',
      userId: architect.id
    }
  });

  const sampleProject1 = existingProject1 || await prisma.project.create({
    data: {
      name: '강남 오피스 빌딩',
      description: '강남구에 위치한 20층 규모의 오피스 빌딩 프로젝트입니다. 지상 20층, 지하 3층으로 구성되며, 연면적은 25,000㎡입니다.',
      status: 'ACTIVE',
      settings: JSON.stringify({
        units: 'metric',
        precision: 3,
        autoSave: true,
        collaborationEnabled: true
      }),
      userId: architect.id
    }
  });
  console.log('✅ 샘플 프로젝트 1 생성:', sampleProject1.name);

  const existingProject2 = await prisma.project.findFirst({
    where: { 
      name: '판교 주상복합',
      userId: premium.id
    }
  });

  const sampleProject2 = existingProject2 || await prisma.project.create({
    data: {
      name: '판교 주상복합',
      description: '판교신도시 내 주상복합 건물로, 주거와 상업시설이 복합된 35층 규모의 프로젝트입니다.',
      status: 'PLANNING',
      settings: JSON.stringify({
        units: 'metric',
        precision: 2,
        autoSave: true,
        collaborationEnabled: false
      }),
      userId: premium.id
    }
  });
  console.log('✅ 샘플 프로젝트 2 생성:', sampleProject2.name);

  // 5. 샘플 BIM 모델 생성
  const existingModel1 = await prisma.bimModel.findFirst({
    where: {
      projectId: sampleProject1.id,
      name: '구조 모델'
    }
  });

  const sampleModel1 = existingModel1 || await prisma.bimModel.create({
    data: {
      name: '구조 모델',
      description: '오피스 빌딩의 주요 구조체 (기둥, 보, 슬래브) 모델',
      type: 'OFFICE',
      naturalLanguageInput: '강남구에 20층 오피스 빌딩 구조체 모델을 만들어주세요.',
      geometryData: JSON.stringify({
        type: 'building',
        floors: 20,
        basement: 3,
        totalHeight: 85.5,
        floorHeight: 3.5,
        components: [
          { type: 'column', count: 120, material: 'concrete' },
          { type: 'beam', count: 480, material: 'steel' },
          { type: 'slab', count: 23, material: 'concrete' }
        ]
      }),
      properties: JSON.stringify({
        buildingUse: 'office',
        structuralSystem: 'concrete_steel_composite',
        seismicZone: 'I',
        windLoad: '1.2kN/m2',
        liveLoad: '3.0kN/m2',
        deadLoad: '5.5kN/m2'
      }),
      materials: JSON.stringify([
        { id: 'C30', type: 'concrete', strength: '30MPa', density: '2400kg/m3' },
        { id: 'S355', type: 'steel', strength: '355MPa', density: '7850kg/m3' }
      ]),
      metadata: JSON.stringify({
        schema: 'IFC4',
        entities: 1250,
        relationships: 3400,
        propertySet: 89
      }),
      projectId: sampleProject1.id,
      userId: architect.id
    }
  });
  console.log('✅ 샘플 BIM 모델 1 생성:', sampleModel1.name);

  const existingModel2 = await prisma.bimModel.findFirst({
    where: {
      projectId: sampleProject2.id,
      name: '건축 모델'
    }
  });

  const sampleModel2 = existingModel2 || await prisma.bimModel.create({
    data: {
      name: '건축 모델',
      description: '주상복합 건물의 건축 설계 모델 (벽체, 개구부, 마감재)',
      type: 'APARTMENT',
      naturalLanguageInput: '판교에 35층 주상복합 건물 건축 모델을 설계해주세요.',
      geometryData: JSON.stringify({
        type: 'mixed_use',
        floors: 35,
        basement: 4,
        totalHeight: 125.0,
        floorHeight: 3.2,
        components: [
          { type: 'wall', count: 2850, material: 'concrete_block' },
          { type: 'window', count: 420, material: 'aluminum_glass' },
          { type: 'door', count: 185, material: 'steel_wood' }
        ]
      }),
      properties: JSON.stringify({
        buildingUse: 'mixed_residential_commercial',
        wallSystem: 'load_bearing_masonry',
        insulationType: 'external',
        windowToWallRatio: 0.35,
        energyRating: 'A+'
      }),
      materials: JSON.stringify([
        { id: 'CB200', type: 'concrete_block', strength: '20MPa', density: '1800kg/m3' },
        { id: 'ALU6063', type: 'aluminum', strength: '240MPa', density: '2700kg/m3' },
        { id: 'GLASS_6mm', type: 'glass', strength: '50MPa', density: '2500kg/m3' }
      ]),
      metadata: JSON.stringify({
        schema: 'IFC4',
        entities: 2890,
        relationships: 5200,
        propertySet: 156
      }),
      projectId: sampleProject2.id,
      userId: premium.id
    }
  });
  console.log('✅ 샘플 BIM 모델 2 생성:', sampleModel2.name);

  // 6. 활동 로그 생성
  const activities = [
    {
      action: 'PROJECT_CREATED',
      details: `프로젝트 '${sampleProject1.name}'가 생성되었습니다.`,
      userId: architect.id,
      projectId: sampleProject1.id
    },
    {
      action: 'MODEL_CREATED',
      details: `BIM 모델 '${sampleModel1.name}'가 생성되었습니다.`,
      userId: architect.id,
      projectId: sampleProject1.id,
      bimModelId: sampleModel1.id
    },
    {
      action: 'PROJECT_CREATED',
      details: `프로젝트 '${sampleProject2.name}'가 생성되었습니다.`,
      userId: premium.id,
      projectId: sampleProject2.id
    },
    {
      action: 'MODEL_CREATED',
      details: `BIM 모델 '${sampleModel2.name}'가 생성되었습니다.`,
      userId: premium.id,
      projectId: sampleProject2.id,
      bimModelId: sampleModel2.id
    },
    {
      action: 'USER_LOGIN',
      details: '사용자가 로그인했습니다.',
      userId: architect.id,
      ipAddress: '192.168.1.100',
      userAgent: 'Mozilla/5.0'
    }
  ];

  for (const activity of activities) {
    await prisma.activityLog.create({
      data: activity
    });
  }
  console.log('✅ 활동 로그 생성 완료:', activities.length, '개');

  console.log('\n🎉 시드 데이터 생성이 완료되었습니다!');
  console.log('\n📊 생성된 데이터:');
  console.log(`   👥 사용자: 3명 (관리자, 건축가, 프리미엄)`);
  console.log(`   📁 프로젝트: 2개`);
  console.log(`   🏗️  BIM 모델: 2개`);
  console.log(`   📋 활동 로그: ${activities.length}개`);
  
  console.log('\n🔑 테스트 계정:');
  console.log(`   관리자: admin@bim-platform.com / Admin123!`);
  console.log(`   건축가: architect@example.com / Architect123!`);
  console.log(`   프리미엄: premium@example.com / Premium123!`);
}

main()
  .catch((e) => {
    console.error('❌ 시드 데이터 생성 중 오류 발생:', e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
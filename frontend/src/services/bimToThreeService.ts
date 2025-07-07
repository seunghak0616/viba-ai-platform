/**
 * BIM 데이터를 3D 객체로 변환하는 서비스
 * Babylon.js와 함께 사용
 */
import {
  Scene,
  Mesh,
  MeshBuilder,
  StandardMaterial,
  Color3,
  Vector3,
  CSG,
  Vector4,
  Animation,
  AnimationGroup
} from '@babylonjs/core';

export interface Room {
  type: string;
  count: number;
  area: number;
  orientation?: string;
  position?: { x: number; y: number; z: number };
  dimensions?: { width: number; height: number; depth: number };
}

export interface BIMData {
  id?: string;
  name?: string;
  description?: string;
  buildingType: string;
  totalArea: { value: number; unit: string };
  rooms: Room[];
  style?: {
    architectural: string;
    interior: string;
    keywords: string[];
  };
  location?: {
    address: string;
    region: string;
    climate: string;
  };
  naturalLanguageInput?: string;
}

export interface BuildingLayout {
  foundation: Mesh;
  walls: Mesh[];
  rooms: { mesh: Mesh; room: Room }[];
  windows: Mesh[];
  doors: Mesh[];
  roof?: Mesh;
}

/**
 * BIM 데이터를 3D 건물로 변환하는 클래스
 */
export class BIMToThreeService {
  private scene: Scene;
  private buildingHeight: number = 3; // 기본 높이 3m
  private wallThickness: number = 0.2; // 벽 두께 20cm
  private windowHeight: number = 1.5;
  private doorHeight: number = 2.1;
  private doorWidth: number = 0.9;

  constructor(scene: Scene) {
    this.scene = scene;
  }

  /**
   * BIM 데이터를 완전한 3D 건물로 변환
   */
  public createBuilding(bimData: BIMData): BuildingLayout {
    // 전체 건물 크기 계산
    const { width, depth } = this.calculateBuildingDimensions(bimData);
    
    // 방 배치 계산
    const roomLayouts = this.calculateRoomLayouts(bimData.rooms, width, depth);
    
    // 건물 요소들 생성
    const foundation = this.createFoundation(width, depth);
    const walls = this.createWalls(roomLayouts, width, depth);
    const rooms = this.createRooms(roomLayouts, bimData);
    const windows = this.createWindows(roomLayouts);
    const doors = this.createDoors(roomLayouts);
    const roof = this.createRoof(width, depth);

    // 재질 적용
    this.applyMaterials({ foundation, walls, rooms, windows, doors, roof }, bimData);

    return {
      foundation,
      walls,
      rooms,
      windows,
      doors,
      roof
    };
  }

  /**
   * 건물 전체 크기 계산
   */
  private calculateBuildingDimensions(bimData: BIMData): { width: number; depth: number } {
    const totalArea = bimData.totalArea.value;
    const areaInSqm = bimData.totalArea.unit === '평' ? totalArea * 3.3 : totalArea;
    
    // 건물 유형별 비율 조정
    let ratio = 4 / 3; // 기본 비율
    
    switch (bimData.buildingType) {
      case 'COMMERCIAL':
      case 'OFFICE':
        ratio = 3 / 2; // 상업/사무 건물은 더 넓은 형태
        break;
      case 'INDUSTRIAL':
        ratio = 5 / 2; // 산업 건물은 매우 넓은 형태
        break;
      case 'RESIDENTIAL':
        ratio = 3 / 4; // 주거 건물은 더 깊은 형태
        break;
      case 'PUBLIC':
        ratio = 2 / 1; // 공공 건물은 넓은 형태
        break;
    }
    
    const width = Math.sqrt(areaInSqm * ratio);
    const depth = Math.sqrt(areaInSqm / ratio);
    
    return {
      width: Math.max(width, 6), // 최소 6m
      depth: Math.max(depth, 4)  // 최소 4m
    };
  }

  /**
   * 방 배치 계산
   */
  private calculateRoomLayouts(rooms: Room[], buildingWidth: number, buildingDepth: number) {
    const layouts: Array<Room & { 
      position: Vector3; 
      dimensions: { width: number; height: number; depth: number };
      wallPositions: Vector3[];
    }> = [];

    let currentX = 0;
    let currentZ = 0;
    let rowHeight = 0;

    rooms.forEach((room, index) => {
      // 방 크기 계산
      const roomArea = room.area || 10;
      const roomWidth = Math.sqrt(roomArea * 1.2); // 가로가 조금 더 긴 형태
      const roomDepth = roomArea / roomWidth;

      // 다음 행으로 넘어가야 하는 경우
      if (currentX + roomWidth > buildingWidth) {
        currentX = 0;
        currentZ += rowHeight + this.wallThickness;
        rowHeight = 0;
      }

      // 방 위치 설정
      const position = new Vector3(
        currentX + roomWidth / 2 - buildingWidth / 2,
        this.buildingHeight / 2,
        currentZ + roomDepth / 2 - buildingDepth / 2
      );

      // 벽 위치 계산
      const wallPositions = this.calculateWallPositions(
        currentX - buildingWidth / 2,
        currentZ - buildingDepth / 2,
        roomWidth,
        roomDepth
      );

      layouts.push({
        ...room,
        position,
        dimensions: {
          width: roomWidth,
          height: this.buildingHeight,
          depth: roomDepth
        },
        wallPositions
      });

      currentX += roomWidth + this.wallThickness;
      rowHeight = Math.max(rowHeight, roomDepth);
    });

    return layouts;
  }

  /**
   * 벽 위치 계산
   */
  private calculateWallPositions(x: number, z: number, width: number, depth: number): Vector3[] {
    const positions: Vector3[] = [];
    const halfWall = this.wallThickness / 2;

    // 4면의 벽
    positions.push(
      new Vector3(x + width / 2, this.buildingHeight / 2, z - halfWall), // 북쪽 벽
      new Vector3(x + width / 2, this.buildingHeight / 2, z + depth + halfWall), // 남쪽 벽
      new Vector3(x - halfWall, this.buildingHeight / 2, z + depth / 2), // 서쪽 벽
      new Vector3(x + width + halfWall, this.buildingHeight / 2, z + depth / 2) // 동쪽 벽
    );

    return positions;
  }

  /**
   * 기초 생성
   */
  private createFoundation(width: number, depth: number): Mesh {
    const foundation = MeshBuilder.CreateBox(
      'foundation',
      { 
        width: width + 1, 
        height: 0.5, 
        depth: depth + 1 
      },
      this.scene
    );
    foundation.position.y = -0.25;
    return foundation;
  }

  /**
   * 벽 생성
   */
  private createWalls(roomLayouts: any[], buildingWidth: number, buildingDepth: number): Mesh[] {
    const walls: Mesh[] = [];

    // 외벽 생성
    const outerWalls = this.createOuterWalls(buildingWidth, buildingDepth);
    walls.push(...outerWalls);

    // 내벽 생성
    roomLayouts.forEach((room, index) => {
      const innerWalls = this.createInnerWalls(room);
      walls.push(...innerWalls);
    });

    return walls;
  }

  /**
   * 외벽 생성
   */
  private createOuterWalls(width: number, depth: number): Mesh[] {
    const walls: Mesh[] = [];
    const halfWidth = width / 2;
    const halfDepth = depth / 2;

    // 북쪽 벽
    const northWall = MeshBuilder.CreateBox(
      'north_wall',
      { 
        width: width + this.wallThickness, 
        height: this.buildingHeight, 
        depth: this.wallThickness 
      },
      this.scene
    );
    northWall.position = new Vector3(0, this.buildingHeight / 2, -halfDepth - this.wallThickness / 2);
    walls.push(northWall);

    // 남쪽 벽
    const southWall = MeshBuilder.CreateBox(
      'south_wall',
      { 
        width: width + this.wallThickness, 
        height: this.buildingHeight, 
        depth: this.wallThickness 
      },
      this.scene
    );
    southWall.position = new Vector3(0, this.buildingHeight / 2, halfDepth + this.wallThickness / 2);
    walls.push(southWall);

    // 서쪽 벽
    const westWall = MeshBuilder.CreateBox(
      'west_wall',
      { 
        width: this.wallThickness, 
        height: this.buildingHeight, 
        depth: depth 
      },
      this.scene
    );
    westWall.position = new Vector3(-halfWidth - this.wallThickness / 2, this.buildingHeight / 2, 0);
    walls.push(westWall);

    // 동쪽 벽
    const eastWall = MeshBuilder.CreateBox(
      'east_wall',
      { 
        width: this.wallThickness, 
        height: this.buildingHeight, 
        depth: depth 
      },
      this.scene
    );
    eastWall.position = new Vector3(halfWidth + this.wallThickness / 2, this.buildingHeight / 2, 0);
    walls.push(eastWall);

    return walls;
  }

  /**
   * 내벽 생성
   */
  private createInnerWalls(room: any): Mesh[] {
    // 간단한 구현: 방 사이의 벽은 생략하고 방 내부만 표현
    return [];
  }

  /**
   * 방 생성
   */
  private createRooms(roomLayouts: any[], bimData: BIMData): Array<{ mesh: Mesh; room: Room }> {
    return roomLayouts.map((layout, index) => {
      const roomMesh = MeshBuilder.CreateBox(
        `room_${layout.type}_${index}`,
        {
          width: layout.dimensions.width - this.wallThickness,
          height: layout.dimensions.height,
          depth: layout.dimensions.depth - this.wallThickness
        },
        this.scene
      );

      roomMesh.position = layout.position.clone();
      roomMesh.position.y = layout.dimensions.height / 2;

      return {
        mesh: roomMesh,
        room: layout
      };
    });
  }

  /**
   * 창문 생성
   */
  private createWindows(roomLayouts: any[]): Mesh[] {
    const windows: Mesh[] = [];

    roomLayouts.forEach((room, index) => {
      // 남향 또는 동향에 창문 배치
      if (room.orientation === '남향' || index % 2 === 0) {
        const window = MeshBuilder.CreateBox(
          `window_${index}`,
          {
            width: room.dimensions.width * 0.6,
            height: this.windowHeight,
            depth: 0.05
          },
          this.scene
        );

        window.position = new Vector3(
          room.position.x,
          this.windowHeight / 2 + 0.8, // 바닥에서 80cm 위
          room.position.z + room.dimensions.depth / 2
        );

        windows.push(window);
      }
    });

    return windows;
  }

  /**
   * 문 생성
   */
  private createDoors(roomLayouts: any[]): Mesh[] {
    const doors: Mesh[] = [];

    roomLayouts.forEach((room, index) => {
      // 각 방에 입구 문 생성
      const door = MeshBuilder.CreateBox(
        `door_${index}`,
        {
          width: this.doorWidth,
          height: this.doorHeight,
          depth: 0.05
        },
        this.scene
      );

      // 문 위치 (방 입구)
      door.position = new Vector3(
        room.position.x - room.dimensions.width / 2,
        this.doorHeight / 2,
        room.position.z
      );

      doors.push(door);
    });

    return doors;
  }

  /**
   * 지붕 생성
   */
  private createRoof(width: number, depth: number): Mesh {
    const roof = MeshBuilder.CreateBox(
      'roof',
      { 
        width: width + 0.5, 
        height: 0.3, 
        depth: depth + 0.5 
      },
      this.scene
    );
    roof.position.y = this.buildingHeight + 0.15;
    return roof;
  }

  /**
   * 재질 적용
   */
  private applyMaterials(building: BuildingLayout, bimData: BIMData): void {
    // 건물 유형별 색상 팔레트
    const colorPalettes = {
      RESIDENTIAL: {
        foundation: new Color3(0.6, 0.6, 0.6),
        wall: new Color3(0.9, 0.9, 0.85),
        roof: new Color3(0.5, 0.3, 0.2),
        window: new Color3(0.6, 0.8, 1.0),
        door: new Color3(0.4, 0.3, 0.2)
      },
      COMMERCIAL: {
        foundation: new Color3(0.5, 0.5, 0.5),
        wall: new Color3(0.8, 0.85, 0.9),
        roof: new Color3(0.3, 0.3, 0.3),
        window: new Color3(0.7, 0.9, 1.0),
        door: new Color3(0.2, 0.4, 0.6)
      },
      OFFICE: {
        foundation: new Color3(0.6, 0.6, 0.6),
        wall: new Color3(0.95, 0.95, 0.9),
        roof: new Color3(0.4, 0.4, 0.4),
        window: new Color3(0.8, 0.9, 1.0),
        door: new Color3(0.3, 0.3, 0.3)
      },
      INDUSTRIAL: {
        foundation: new Color3(0.5, 0.5, 0.5),
        wall: new Color3(0.7, 0.7, 0.7),
        roof: new Color3(0.6, 0.6, 0.6),
        window: new Color3(0.5, 0.7, 0.9),
        door: new Color3(0.4, 0.4, 0.4)
      },
      PUBLIC: {
        foundation: new Color3(0.6, 0.6, 0.6),
        wall: new Color3(0.9, 0.85, 0.8),
        roof: new Color3(0.4, 0.5, 0.3),
        window: new Color3(0.6, 0.8, 1.0),
        door: new Color3(0.3, 0.5, 0.3)
      }
    };

    const palette = colorPalettes[bimData.buildingType as keyof typeof colorPalettes] || 
                   colorPalettes.RESIDENTIAL;

    // 기초 재질
    const foundationMaterial = new StandardMaterial('foundationMaterial', this.scene);
    foundationMaterial.diffuseColor = palette.foundation;
    building.foundation.material = foundationMaterial;

    // 벽 재질
    const wallMaterial = new StandardMaterial('wallMaterial', this.scene);
    wallMaterial.diffuseColor = palette.wall;
    building.walls.forEach(wall => {
      wall.material = wallMaterial;
    });

    // 지붕 재질
    if (building.roof) {
      const roofMaterial = new StandardMaterial('roofMaterial', this.scene);
      roofMaterial.diffuseColor = palette.roof;
      building.roof.material = roofMaterial;
    }

    // 창문 재질
    const windowMaterial = new StandardMaterial('windowMaterial', this.scene);
    windowMaterial.diffuseColor = palette.window;
    windowMaterial.alpha = 0.7;
    building.windows.forEach(window => {
      window.material = windowMaterial;
    });

    // 문 재질
    const doorMaterial = new StandardMaterial('doorMaterial', this.scene);
    doorMaterial.diffuseColor = palette.door;
    building.doors.forEach(door => {
      door.material = doorMaterial;
    });

    // 방별 재질
    const roomColors = {
      '거실': new Color3(0.9, 0.85, 0.7),
      '침실': new Color3(0.8, 0.9, 0.8),
      '주방': new Color3(0.9, 0.8, 0.7),
      '화장실': new Color3(0.7, 0.8, 0.9),
      '욕실': new Color3(0.7, 0.8, 0.9),
      '서재': new Color3(0.8, 0.8, 0.9),
      '다이닝': new Color3(0.9, 0.8, 0.7),
      '사무실': new Color3(0.9, 0.9, 0.8),
      '회의실': new Color3(0.8, 0.8, 0.9),
      '휴게실': new Color3(0.8, 0.9, 0.8),
      '홀': new Color3(0.9, 0.9, 0.8)
    };

    building.rooms.forEach((roomObj, index) => {
      const roomMaterial = new StandardMaterial(`room_${index}_material`, this.scene);
      roomMaterial.diffuseColor = roomColors[roomObj.room.type as keyof typeof roomColors] || 
                                 new Color3(0.8, 0.8, 0.8);
      roomMaterial.alpha = 0.6;
      roomObj.mesh.material = roomMaterial;
    });
  }

  /**
   * 애니메이션 추가
   */
  public addBuildingAnimation(building: BuildingLayout): AnimationGroup {
    const animationGroup = new AnimationGroup('buildingAnimation', this.scene);

    // 건물 등장 애니메이션
    building.rooms.forEach((roomObj, index) => {
      // 애니메이션 키 생성
      const scaleKeys = [
        { frame: 0, value: Vector3.Zero() },
        { frame: 30, value: Vector3.One() }
      ];

      // 애니메이션 생성
      const scaleAnimation = new Animation(
        `scale_${index}`,
        'scaling',
        30,
        Animation.ANIMATIONTYPE_VECTOR3,
        Animation.ANIMATIONLOOPMODE_CONSTANT
      );
      
      scaleAnimation.setKeys(scaleKeys);
      
      // 애니메이션 그룹에 추가
      animationGroup.addTargetedAnimation(scaleAnimation, roomObj.mesh);
    });

    return animationGroup;
  }

  /**
   * 건물 레이아웃 최적화
   */
  public optimizeLayout(bimData: BIMData): BIMData {
    // 방 배치 최적화 알고리즘
    const optimizedRooms = [...bimData.rooms];

    // 거실을 중앙에, 침실을 조용한 곳에 배치 등의 로직
    optimizedRooms.sort((a, b) => {
      const priority = {
        '거실': 1,
        '다이닝': 2,
        '주방': 3,
        '침실': 4,
        '서재': 5,
        '화장실': 6,
        '욕실': 6
      };

      const aPriority = priority[a.type as keyof typeof priority] || 10;
      const bPriority = priority[b.type as keyof typeof priority] || 10;

      return aPriority - bPriority;
    });

    return {
      ...bimData,
      rooms: optimizedRooms
    };
  }
}

export default BIMToThreeService;
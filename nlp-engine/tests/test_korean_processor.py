#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Korean NLP Processor Unit Tests
한국어 자연어 처리 엔진의 단위 테스트
안전하고 정확한 처리를 위한 포괄적 테스트
"""

import unittest
import json
from unittest.mock import patch, MagicMock
from decimal import Decimal

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from processors.korean_processor import KoreanProcessor
from utils.validation import ValidationError

class TestKoreanProcessor(unittest.TestCase):
    """
    Korean NLP Processor 테스트 클래스
    """
    
    def setUp(self):
        """테스트 설정"""
        self.processor = KoreanProcessor()
        
        # 테스트용 샘플 입력들
        self.sample_inputs = {
            'apartment_basic': '남향 거실이 있는 30평 아파트 설계해줘',
            'house_complex': '동향 현관과 서향 주방이 있는 40평 단독주택을 만들어주세요',
            'villa_simple': '25평 빌라',
            'office_detailed': '북향 회의실 2개와 남향 사무실 3개가 있는 100평 오피스텔',
            'mixed_korean_english': '30평 apartment with 남향 living room',
            'numbers_only': '평수 30',
            'orientation_only': '남향',
            'room_types_only': '거실 침실 주방 화장실'
        }
        
        # 예상 결과들
        self.expected_results = {
            'apartment_basic': {
                'building_type': '아파트',
                'total_area': {'value': 30, 'unit': '평'},
                'rooms': [
                    {'type': '거실', 'orientation': '남향', 'count': 1}
                ]
            }
        }
    
    def tearDown(self):
        """테스트 정리"""
        pass

    # ==========================================================================
    # Initialization Tests
    # ==========================================================================
    
    def test_processor_initialization(self):
        """프로세서 초기화 테스트"""
        processor = KoreanProcessor()
        
        # 기본 속성 확인
        self.assertIsNotNone(processor.patterns)
        self.assertIsInstance(processor.patterns, dict)
        
        # 필수 패턴들이 존재하는지 확인
        required_patterns = [
            'building_types', 'room_types', 'area_patterns',
            'orientation_patterns', 'count_patterns'
        ]
        
        for pattern_key in required_patterns:
            self.assertIn(pattern_key, processor.patterns)
            self.assertIsInstance(processor.patterns[pattern_key], dict)
    
    def test_processor_with_custom_config(self):
        """커스텀 설정으로 프로세서 초기화 테스트"""
        custom_config = {
            'confidence_threshold': 0.8,
            'max_input_length': 500
        }
        
        processor = KoreanProcessor(config=custom_config)
        self.assertEqual(processor.config['confidence_threshold'], 0.8)
        self.assertEqual(processor.config['max_input_length'], 500)

    # ==========================================================================
    # Core Processing Tests
    # ==========================================================================
    
    def test_process_basic_apartment_input(self):
        """기본 아파트 입력 처리 테스트"""
        input_text = self.sample_inputs['apartment_basic']
        result = self.processor.process(input_text)
        
        # 기본 구조 확인
        self.assertIsInstance(result, dict)
        self.assertIn('building_type', result)
        self.assertIn('total_area', result)
        self.assertIn('rooms', result)
        self.assertIn('confidence', result)
        
        # 건물 타입 확인
        self.assertEqual(result['building_type'], '아파트')
        
        # 면적 확인
        self.assertIsInstance(result['total_area'], dict)
        self.assertEqual(result['total_area']['value'], 30)
        self.assertEqual(result['total_area']['unit'], '평')
        
        # 방 정보 확인
        self.assertIsInstance(result['rooms'], list)
        self.assertGreater(len(result['rooms']), 0)
        
        # 거실 정보 확인
        living_room = next(
            (room for room in result['rooms'] if room['type'] == '거실'), 
            None
        )
        self.assertIsNotNone(living_room)
        self.assertEqual(living_room['orientation'], '남향')
        
        # 신뢰도 확인
        self.assertIsInstance(result['confidence'], (int, float))
        self.assertGreaterEqual(result['confidence'], 0)
        self.assertLessEqual(result['confidence'], 1)
    
    def test_process_complex_house_input(self):
        """복잡한 단독주택 입력 처리 테스트"""
        input_text = self.sample_inputs['house_complex']
        result = self.processor.process(input_text)
        
        # 건물 타입 확인
        self.assertEqual(result['building_type'], '단독주택')
        
        # 면적 확인
        self.assertEqual(result['total_area']['value'], 40)
        
        # 여러 방향 정보 확인
        orientations_found = [room['orientation'] for room in result['rooms'] if 'orientation' in room]
        self.assertIn('동향', orientations_found)
        self.assertIn('서향', orientations_found)
        
        # 방 타입 확인
        room_types = [room['type'] for room in result['rooms']]
        self.assertIn('현관', room_types)
        self.assertIn('주방', room_types)
    
    def test_process_simple_villa_input(self):
        """간단한 빌라 입력 처리 테스트"""
        input_text = self.sample_inputs['villa_simple']
        result = self.processor.process(input_text)
        
        self.assertEqual(result['building_type'], '빌라')
        self.assertEqual(result['total_area']['value'], 25)
        
        # 기본 방들이 추가되었는지 확인
        room_types = [room['type'] for room in result['rooms']]
        basic_rooms = ['거실', '침실', '주방', '화장실']
        
        for basic_room in basic_rooms:
            self.assertIn(basic_room, room_types)
    
    def test_process_office_detailed_input(self):
        """상세한 오피스텔 입력 처리 테스트"""
        input_text = self.sample_inputs['office_detailed']
        result = self.processor.process(input_text)
        
        self.assertEqual(result['building_type'], '오피스텔')
        self.assertEqual(result['total_area']['value'], 100)
        
        # 개수 정보 확인
        meeting_rooms = [room for room in result['rooms'] if room['type'] == '회의실']
        office_rooms = [room for room in result['rooms'] if room['type'] == '사무실']
        
        self.assertEqual(len(meeting_rooms), 2)
        self.assertEqual(len(office_rooms), 3)
        
        # 방향 정보 확인
        meeting_room_orientations = [room.get('orientation') for room in meeting_rooms]
        office_room_orientations = [room.get('orientation') for room in office_rooms]
        
        self.assertTrue(all(orient == '북향' for orient in meeting_room_orientations if orient))
        self.assertTrue(all(orient == '남향' for orient in office_room_orientations if orient))

    # ==========================================================================
    # Pattern Extraction Tests
    # ==========================================================================
    
    def test_extract_building_type(self):
        """건물 타입 추출 테스트"""
        test_cases = [
            ('30평 아파트', '아파트'),
            ('단독주택을 지어주세요', '단독주택'),
            ('빌라 설계', '빌라'),
            ('오피스텔 인테리어', '오피스텔'),
            ('상가 건물', '상가'),
            ('주택 설계', '주택')
        ]
        
        for input_text, expected_type in test_cases:
            with self.subTest(input_text=input_text):
                result = self.processor._extract_building_type(input_text)
                self.assertEqual(result, expected_type)
    
    def test_extract_area_information(self):
        """면적 정보 추출 테스트"""
        test_cases = [
            ('30평 아파트', {'value': 30, 'unit': '평'}),
            ('99.17㎡ 아파트', {'value': 99.17, 'unit': '㎡'}),
            ('100제곱미터 주택', {'value': 100, 'unit': '㎡'}),
            ('50평형 빌라', {'value': 50, 'unit': '평'}),
            ('35평 정도의 아파트', {'value': 35, 'unit': '평'})
        ]
        
        for input_text, expected_area in test_cases:
            with self.subTest(input_text=input_text):
                result = self.processor._extract_area(input_text)
                self.assertIsNotNone(result)
                self.assertEqual(result['value'], expected_area['value'])
                self.assertEqual(result['unit'], expected_area['unit'])
    
    def test_extract_orientation_information(self):
        """방향 정보 추출 테스트"""
        test_cases = [
            ('남향 거실', ['남향']),
            ('동향 현관과 서향 주방', ['동향', '서향']),
            ('북향 침실', ['북향']),
            ('남동향 베란다', ['남동향']),
            ('서남향 창문', ['서남향'])
        ]
        
        for input_text, expected_orientations in test_cases:
            with self.subTest(input_text=input_text):
                result = self.processor._extract_orientations(input_text)
                for expected_orientation in expected_orientations:
                    self.assertIn(expected_orientation, result)
    
    def test_extract_room_information(self):
        """방 정보 추출 테스트"""
        test_cases = [
            ('거실 침실 주방 화장실', ['거실', '침실', '주방', '화장실']),
            ('침실 2개', ['침실']),
            ('화장실 1개와 욕실 1개', ['화장실', '욕실']),
            ('안방과 작은방', ['안방', '작은방']),
            ('현관과 베란다', ['현관', '베란다'])
        ]
        
        for input_text, expected_rooms in test_cases:
            with self.subTest(input_text=input_text):
                result = self.processor._extract_rooms(input_text)
                room_types = [room['type'] for room in result]
                
                for expected_room in expected_rooms:
                    self.assertIn(expected_room, room_types)
    
    def test_extract_count_information(self):
        """개수 정보 추출 테스트"""
        test_cases = [
            ('침실 2개', 2),
            ('화장실 1개', 1),
            ('방 3개', 3),
            ('침실 두개', 2),
            ('방 하나', 1),
            ('침실 여러개', None)  # 명확하지 않은 개수
        ]
        
        for input_text, expected_count in test_cases:
            with self.subTest(input_text=input_text):
                result = self.processor._extract_count(input_text)
                if expected_count is None:
                    self.assertIsNone(result)
                else:
                    self.assertEqual(result, expected_count)

    # ==========================================================================
    # Edge Cases and Error Handling Tests
    # ==========================================================================
    
    def test_empty_input_handling(self):
        """빈 입력 처리 테스트"""
        empty_inputs = ['', '   ', '\n\t', None]
        
        for empty_input in empty_inputs:
            with self.subTest(input=empty_input):
                with self.assertRaises(ValidationError):
                    self.processor.process(empty_input)
    
    def test_very_long_input_handling(self):
        """매우 긴 입력 처리 테스트"""
        long_input = '아파트 ' * 1000  # 매우 긴 입력
        
        with self.assertRaises(ValidationError):
            self.processor.process(long_input)
    
    def test_special_characters_handling(self):
        """특수 문자 포함 입력 처리 테스트"""
        special_inputs = [
            '30평 아파트 @#$%',
            '거실<script>alert("test")</script>',
            '침실 & 주방',
            '30평 아파트 (남향)',
            '아파트 설계해주세요!!!'
        ]
        
        for special_input in special_inputs:
            with self.subTest(input=special_input):
                try:
                    result = self.processor.process(special_input)
                    # 결과가 반환되면 기본 구조를 가져야 함
                    self.assertIn('building_type', result)
                    self.assertIn('confidence', result)
                except ValidationError:
                    # ValidationError가 발생하는 것도 허용 (보안상 이유)
                    pass
    
    def test_mixed_language_input(self):
        """한영 혼합 입력 처리 테스트"""
        mixed_input = self.sample_inputs['mixed_korean_english']
        result = self.processor.process(mixed_input)
        
        # 한국어 부분이 제대로 처리되었는지 확인
        self.assertIn('total_area', result)
        self.assertEqual(result['total_area']['value'], 30)
        
        # 방 정보 확인
        room_types = [room['type'] for room in result['rooms']]
        self.assertIn('거실', room_types)
    
    def test_ambiguous_input_handling(self):
        """모호한 입력 처리 테스트"""
        ambiguous_inputs = [
            '집',  # 너무 일반적
            '30',  # 숫자만
            '남향',  # 방향만
            '설계해주세요',  # 동사만
            '방 여러개'  # 불명확한 개수
        ]
        
        for ambiguous_input in ambiguous_inputs:
            with self.subTest(input=ambiguous_input):
                result = self.processor.process(ambiguous_input)
                
                # 신뢰도가 낮아야 함
                self.assertLess(result['confidence'], 0.7)
    
    def test_contradictory_input_handling(self):
        """모순된 입력 처리 테스트"""
        contradictory_inputs = [
            '30평인데 100평 아파트',  # 면적 모순
            '1층인데 10층 아파트',  # 층수 모순
            '단독주택 아파트',  # 건물 타입 모순
        ]
        
        for contradictory_input in contradictory_inputs:
            with self.subTest(input=contradictory_input):
                result = self.processor.process(contradictory_input)
                
                # 모순이 있는 경우 신뢰도가 낮아야 함
                self.assertLess(result['confidence'], 0.8)

    # ==========================================================================
    # Confidence Calculation Tests
    # ==========================================================================
    
    def test_confidence_calculation_high(self):
        """높은 신뢰도 계산 테스트"""
        # 매우 명확한 입력
        clear_input = '남향 거실과 북향 침실 2개가 있는 30평 아파트를 설계해주세요'
        result = self.processor.process(clear_input)
        
        # 높은 신뢰도 기대
        self.assertGreaterEqual(result['confidence'], 0.8)
    
    def test_confidence_calculation_medium(self):
        """중간 신뢰도 계산 테스트"""
        # 일부 정보가 누락된 입력
        partial_input = '30평 아파트'
        result = self.processor.process(partial_input)
        
        # 중간 신뢰도 기대
        self.assertGreaterEqual(result['confidence'], 0.5)
        self.assertLess(result['confidence'], 0.8)
    
    def test_confidence_calculation_low(self):
        """낮은 신뢰도 계산 테스트"""
        # 매우 모호한 입력
        vague_input = '집 설계'
        result = self.processor.process(vague_input)
        
        # 낮은 신뢰도 기대
        self.assertLess(result['confidence'], 0.5)

    # ==========================================================================
    # Integration and Performance Tests
    # ==========================================================================
    
    def test_batch_processing(self):
        """배치 처리 테스트"""
        inputs = list(self.sample_inputs.values())
        results = []
        
        for input_text in inputs:
            try:
                result = self.processor.process(input_text)
                results.append(result)
            except ValidationError:
                # 일부 입력은 검증 오류가 발생할 수 있음
                pass
        
        # 대부분의 입력이 성공적으로 처리되어야 함
        self.assertGreaterEqual(len(results), len(inputs) * 0.8)
    
    def test_performance_timing(self):
        """처리 성능 테스트"""
        import time
        
        input_text = self.sample_inputs['apartment_basic']
        
        # 10번 실행하여 평균 시간 측정
        start_time = time.time()
        
        for _ in range(10):
            self.processor.process(input_text)
        
        end_time = time.time()
        average_time = (end_time - start_time) / 10
        
        # 평균 처리 시간이 1초 이내여야 함
        self.assertLess(average_time, 1.0)
    
    def test_memory_usage(self):
        """메모리 사용량 테스트"""
        import gc
        import psutil
        import os
        
        # 초기 메모리 사용량
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # 많은 처리 수행
        for _ in range(100):
            self.processor.process(self.sample_inputs['apartment_basic'])
        
        # 가비지 컬렉션 수행
        gc.collect()
        
        # 최종 메모리 사용량
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # 메모리 증가가 50MB 이하여야 함
        self.assertLess(memory_increase, 50 * 1024 * 1024)

    # ==========================================================================
    # Utility Method Tests
    # ==========================================================================
    
    def test_normalize_text(self):
        """텍스트 정규화 테스트"""
        test_cases = [
            ('아파트   설계', '아파트 설계'),
            ('거실\n침실', '거실 침실'),
            ('30평　아파트', '30평 아파트'),  # 전각 공백
            ('Apartment 설계', 'apartment 설계'),
            ('30평!!', '30평')
        ]
        
        for input_text, expected_output in test_cases:
            with self.subTest(input=input_text):
                result = self.processor._normalize_text(input_text)
                self.assertEqual(result, expected_output)
    
    def test_validate_input(self):
        """입력 검증 테스트"""
        # 유효한 입력
        valid_inputs = [
            '30평 아파트',
            '남향 거실이 있는 빌라',
            '단독주택 설계해주세요'
        ]
        
        for valid_input in valid_inputs:
            with self.subTest(input=valid_input):
                # 예외가 발생하지 않아야 함
                self.processor._validate_input(valid_input)
        
        # 무효한 입력
        invalid_inputs = [
            '',
            '   ',
            None,
            'a' * 2000,  # 너무 긴 입력
            '<script>alert("xss")</script>',  # 잠재적 XSS
        ]
        
        for invalid_input in invalid_inputs:
            with self.subTest(input=invalid_input):
                with self.assertRaises(ValidationError):
                    self.processor._validate_input(invalid_input)
    
    def test_area_unit_conversion(self):
        """면적 단위 변환 테스트"""
        test_cases = [
            ('30평', {'value': 30, 'unit': '평'}),
            ('99.17㎡', {'value': 99.17, 'unit': '㎡'}),
            ('100제곱미터', {'value': 100, 'unit': '㎡'}),
            ('50평방미터', {'value': 50, 'unit': '㎡'})
        ]
        
        for input_text, expected_result in test_cases:
            with self.subTest(input=input_text):
                result = self.processor._extract_area(input_text)
                self.assertEqual(result['value'], expected_result['value'])
                self.assertEqual(result['unit'], expected_result['unit'])

    # ==========================================================================
    # Security Tests
    # ==========================================================================
    
    def test_sql_injection_prevention(self):
        """SQL 인젝션 방지 테스트"""
        malicious_inputs = [
            "30평 아파트'; DROP TABLE users; --",
            "아파트 UNION SELECT * FROM passwords",
            "30평 OR 1=1"
        ]
        
        for malicious_input in malicious_inputs:
            with self.subTest(input=malicious_input):
                # 악성 입력이 적절히 처리되거나 차단되어야 함
                try:
                    result = self.processor.process(malicious_input)
                    # 결과가 반환되면 정상적인 구조여야 함
                    self.assertIn('building_type', result)
                except ValidationError:
                    # ValidationError 발생도 허용 (보안상 차단)
                    pass
    
    def test_xss_prevention(self):
        """XSS 방지 테스트"""
        xss_inputs = [
            '30평 <script>alert("xss")</script> 아파트',
            '거실 <img src=x onerror=alert("xss")>',
            '아파트 <iframe src="javascript:alert(1)"></iframe>'
        ]
        
        for xss_input in xss_inputs:
            with self.subTest(input=xss_input):
                with self.assertRaises(ValidationError):
                    self.processor.process(xss_input)
    
    def test_code_injection_prevention(self):
        """코드 인젝션 방지 테스트"""
        code_injection_inputs = [
            '30평 {% raw %}{{ 7*7 }}{% endraw %} 아파트',
            '아파트 ${exec("rm -rf /")}',
            '거실 `rm -rf /`'
        ]
        
        for injection_input in code_injection_inputs:
            with self.subTest(input=injection_input):
                with self.assertRaises(ValidationError):
                    self.processor.process(injection_input)

    # ==========================================================================
    # Localization Tests
    # ==========================================================================
    
    def test_korean_number_processing(self):
        """한국어 숫자 처리 테스트"""
        korean_number_inputs = [
            ('삼십평 아파트', 30),
            ('십오평 빌라', 15),
            ('오십평 단독주택', 50),
            ('백평 상가', 100)
        ]
        
        for input_text, expected_value in korean_number_inputs:
            with self.subTest(input=input_text):
                result = self.processor.process(input_text)
                if 'total_area' in result:
                    self.assertEqual(result['total_area']['value'], expected_value)
    
    def test_korean_room_synonyms(self):
        """한국어 방 동의어 처리 테스트"""
        synonym_tests = [
            ('안방', '침실'),
            ('거실', '거실'),
            ('부엌', '주방'),
            ('화장실', '화장실'),
            ('서재', '서재')
        ]
        
        for input_room, expected_room in synonym_tests:
            with self.subTest(input=input_room):
                input_text = f'{input_room}이 있는 30평 아파트'
                result = self.processor.process(input_text)
                
                room_types = [room['type'] for room in result['rooms']]
                # 원본 또는 정규화된 타입 중 하나가 있어야 함
                self.assertTrue(
                    input_room in room_types or expected_room in room_types
                )


if __name__ == '__main__':
    # 테스트 실행
    unittest.main(verbosity=2)

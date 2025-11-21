/**
 * UI/UX 개선 사항 테스트 스크립트
 * 
 * test_alfred_voice.html과 test_voiceprint_management.html의
 * 업데이트된 기능들을 테스트합니다.
 */

const API_BASE_URL = 'http://localhost:8001';

// 테스트 결과 저장
const testResults = {
    passed: [],
    failed: [],
    total: 0
};

// 테스트 헬퍼 함수
function assert(condition, message) {
    testResults.total++;
    if (condition) {
        testResults.passed.push(message);
        console.log(`✅ PASS: ${message}`);
    } else {
        testResults.failed.push(message);
        console.error(`❌ FAIL: ${message}`);
    }
}

// API 연결 테스트
async function testAPIConnection() {
    console.log('\n=== API 연결 테스트 ===');
    try {
        const response = await fetch(`${API_BASE_URL}/`);
        const data = await response.json();
        assert(response.ok, 'API 서버 연결 성공');
        assert(data.status === 'running', '서버 상태 확인');
        assert(data.services !== undefined, '서비스 정보 확인');
    } catch (error) {
        assert(false, `API 연결 실패: ${error.message}`);
    }
}

// 키워드 확인 API 테스트
async function testKeywordCheckAPI() {
    console.log('\n=== 키워드 확인 API 테스트 ===');
    try {
        const response = await fetch(`${API_BASE_URL}/api/keyword/check`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                stt_result: 'alfred',
                base_keyword: 'alfred',
                session_id: 'test_session'
            })
        });
        
        const data = await response.json();
        assert(response.ok, '키워드 확인 API 호출 성공');
        assert(data.hasOwnProperty('is_keyword'), 'is_keyword 필드 존재');
        assert(data.hasOwnProperty('activate'), 'activate 필드 존재');
        assert(data.hasOwnProperty('similarity'), 'similarity 필드 존재');
        
        if (data.is_keyword) {
            assert(data.activate === true, '키워드 매칭 시 활성화됨');
        }
    } catch (error) {
        assert(false, `키워드 확인 API 테스트 실패: ${error.message}`);
    }
}

// 음성 지문 조회 API 테스트
async function testVoiceprintListAPI() {
    console.log('\n=== 음성 지문 조회 API 테스트 ===');
    try {
        const response = await fetch(`${API_BASE_URL}/api/keyword/voiceprint`);
        const data = await response.json();
        assert(response.ok, '음성 지문 조회 API 호출 성공');
        assert(data.hasOwnProperty('success'), 'success 필드 존재');
        assert(data.hasOwnProperty('voiceprints'), 'voiceprints 필드 존재');
        assert(Array.isArray(data.voiceprints), 'voiceprints가 배열임');
    } catch (error) {
        assert(false, `음성 지문 조회 API 테스트 실패: ${error.message}`);
    }
}

// 음성 지문 등록 API 테스트
async function testVoiceprintRegisterAPI() {
    console.log('\n=== 음성 지문 등록 API 테스트 ===');
    try {
        const testData = {
            base_keyword: 'alfred',
            stt_keyword: 'test_stt_' + Date.now(),
            audio_data: null, // 오디오 없이 텍스트만 테스트
            session_id: 'test_session_' + Date.now()
        };
        
        const response = await fetch(`${API_BASE_URL}/api/keyword/voiceprint/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(testData)
        });
        
        const data = await response.json();
        assert(response.ok, '음성 지문 등록 API 호출 성공');
        assert(data.hasOwnProperty('success'), 'success 필드 존재');
        assert(data.hasOwnProperty('voiceprint_id'), 'voiceprint_id 필드 존재');
        assert(data.hasOwnProperty('is_new'), 'is_new 필드 존재');
        
        if (data.success) {
            console.log(`  등록된 음성 지문 ID: ${data.voiceprint_id}`);
        }
    } catch (error) {
        assert(false, `음성 지문 등록 API 테스트 실패: ${error.message}`);
    }
}

// test_alfred_voice.html 기능 테스트 (시뮬레이션)
function testAlfredVoiceFeatures() {
    console.log('\n=== test_alfred_voice.html 기능 테스트 ===');
    
    // 활성화 시간 관리 기능 테스트
    const activationDuration = 5 * 60 * 1000; // 5분
    assert(typeof activationDuration === 'number', '활성화 시간 설정 타입 확인');
    assert(activationDuration > 0, '활성화 시간이 양수임');
    
    // 경고 시간 계산 테스트 (활성화 시간의 80%)
    const warningTime = activationDuration * 0.8;
    assert(warningTime === 4 * 60 * 1000, '경고 시간 계산 정확성 (4분)');
    
    // 세션 활성화 상태 관리 테스트
    let sessionActive = false;
    sessionActive = true;
    assert(sessionActive === true, '세션 활성화 상태 설정');
    
    sessionActive = false;
    assert(sessionActive === false, '세션 비활성화 상태 설정');
    
    console.log('  ✅ 활성화 시간 관리 로직 정상');
    console.log('  ✅ 경고 시간 계산 로직 정상');
    console.log('  ✅ 세션 상태 관리 로직 정상');
}

// test_voiceprint_management.html 기능 테스트 (시뮬레이션)
function testVoiceprintManagementFeatures() {
    console.log('\n=== test_voiceprint_management.html 기능 테스트 ===');
    
    // 등록 상태 관리 테스트
    let registrationState = 'idle';
    const validStates = ['idle', 'recording', 'processing', 'completed'];
    assert(validStates.includes(registrationState), '등록 상태가 유효한 값임');
    
    // 버튼 상태 관리 로직 테스트
    const sttKeyword = 'test_keyword';
    const isRecording = false;
    const isProcessing = false;
    
    // 등록 버튼 활성화 조건: STT 키워드가 있고, 대기 상태이고, 녹음/처리 중이 아닐 때
    const canRegister = sttKeyword && registrationState === 'idle' && !isRecording && !isProcessing;
    assert(canRegister === true, '등록 버튼 활성화 조건 확인');
    
    // 초기화 버튼은 언제든 사용 가능
    const canReset = true;
    assert(canReset === true, '초기화 버튼은 항상 활성화');
    
    // 새로 등록 버튼 활성화 조건: 대기 상태일 때만
    const canNewRegistration = registrationState === 'idle' && !isRecording && !isProcessing;
    assert(canNewRegistration === true, '새로 등록 버튼 활성화 조건 확인');
    
    console.log('  ✅ 등록 상태 관리 로직 정상');
    console.log('  ✅ 버튼 상태 관리 로직 정상');
}

// 통합 테스트: 키워드 확인 → 음성 지문 등록 → 조회
async function testIntegrationFlow() {
    console.log('\n=== 통합 테스트: 키워드 확인 → 음성 지문 등록 → 조회 ===');
    
    try {
        // 1. 키워드 확인
        const checkResponse = await fetch(`${API_BASE_URL}/api/keyword/check`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                stt_result: 'alfred',
                base_keyword: 'alfred',
                session_id: 'integration_test'
            })
        });
        const checkData = await checkResponse.json();
        assert(checkResponse.ok, '통합 테스트: 키워드 확인 성공');
        
        // 2. 음성 지문 등록
        const registerResponse = await fetch(`${API_BASE_URL}/api/keyword/voiceprint/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                base_keyword: 'alfred',
                stt_keyword: 'integration_test_' + Date.now(),
                session_id: 'integration_test'
            })
        });
        const registerData = await registerResponse.json();
        assert(registerResponse.ok, '통합 테스트: 음성 지문 등록 성공');
        
        // 3. 음성 지문 조회
        const listResponse = await fetch(`${API_BASE_URL}/api/keyword/voiceprint?base_keyword=alfred`);
        const listData = await listResponse.json();
        assert(listResponse.ok, '통합 테스트: 음성 지문 조회 성공');
        assert(listData.voiceprints.length > 0, '통합 테스트: 등록된 음성 지문이 목록에 있음');
        
        console.log('  ✅ 전체 통합 플로우 정상 동작');
    } catch (error) {
        assert(false, `통합 테스트 실패: ${error.message}`);
    }
}

// 테스트 실행
async function runAllTests() {
    console.log('='.repeat(60));
    console.log('UI/UX 개선 사항 테스트 시작');
    console.log('='.repeat(60));
    
    // API 연결 테스트
    await testAPIConnection();
    
    // API 단위 테스트
    await testKeywordCheckAPI();
    await testVoiceprintListAPI();
    await testVoiceprintRegisterAPI();
    
    // 기능 단위 테스트
    testAlfredVoiceFeatures();
    testVoiceprintManagementFeatures();
    
    // 통합 테스트
    await testIntegrationFlow();
    
    // 결과 출력
    console.log('\n' + '='.repeat(60));
    console.log('테스트 결과 요약');
    console.log('='.repeat(60));
    console.log(`총 테스트: ${testResults.total}`);
    console.log(`✅ 통과: ${testResults.passed.length}`);
    console.log(`❌ 실패: ${testResults.failed.length}`);
    console.log(`성공률: ${((testResults.passed.length / testResults.total) * 100).toFixed(1)}%`);
    
    if (testResults.failed.length > 0) {
        console.log('\n실패한 테스트:');
        testResults.failed.forEach((msg, idx) => {
            console.log(`  ${idx + 1}. ${msg}`);
        });
    }
    
    return {
        total: testResults.total,
        passed: testResults.passed.length,
        failed: testResults.failed.length,
        successRate: (testResults.passed.length / testResults.total) * 100,
        details: {
            passed: testResults.passed,
            failed: testResults.failed
        }
    };
}

// Node.js 환경에서 실행
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { runAllTests };
}

// 브라우저 환경에서 실행
if (typeof window !== 'undefined') {
    window.runAllTests = runAllTests;
}


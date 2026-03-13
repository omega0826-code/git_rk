# OpenAPI 웹 애플리케이션 개발 가이드라인

**작성일**: 2026-01-14  
**목적**: 공공데이터 OpenAPI를 활용한 웹 애플리케이션 개발 시 참고할 수 있는 재사용 가능한 가이드라인

---

## 📋 목차

1. [개요](#개요)
2. [개발 환경 설정](#개발-환경-설정)
3. [핵심 패턴](#핵심-패턴)
4. [API 인증키 처리](#api-인증키-처리)
5. [대량 데이터 처리](#대량-데이터-처리)
6. [엑셀 다운로드 구현](#엑셀-다운로드-구현)
7. [에러 처리 베스트 프랙티스](#에러-처리-베스트-프랙티스)
8. [재사용 가능한 코드 템플릿](#재사용-가능한-코드-템플릿)

---

## 개요

이 가이드라인은 공공데이터포털(data.go.kr)의 OpenAPI를 활용하여 **서버 없이 브라우저에서 직접 실행 가능한** 웹 애플리케이션을 개발하는 방법을 제시합니다.

### 적용 대상

- 공공데이터포털 OpenAPI 서비스
- REST API 기반 서비스
- JSON 응답 형식 지원 서비스

### 기술 스택

- **HTML5**: 구조
- **CSS3**: 스타일링
- **JavaScript (ES6+)**: 로직
- **SheetJS (xlsx.js)**: 엑셀 처리
- **FileSaver.js**: 파일 다운로드
- **Bootstrap (선택)**: UI 프레임워크

---

## 개발 환경 설정

### 1. CORS 이슈 해결

공공데이터 OpenAPI는 CORS를 허용하지만, 로컬 파일(`file://`)에서는 차단됩니다.

**해결 방법**:

#### 방법 1: VS Code Live Server (권장)
```
1. VS Code 설치
2. Live Server 확장 설치
3. HTML 파일 우클릭 > "Open with Live Server"
```

#### 방법 2: Python 웹 서버
```bash
# Python 3
python -m http.server 8000

# 브라우저에서 접속
http://localhost:8000/파일명.html
```

#### 방법 3: Node.js http-server
```bash
npx http-server -p 8000
```

### 2. 필수 라이브러리 CDN

```html
<!-- Bootstrap CSS (선택) -->
<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css">

<!-- SheetJS for Excel -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.17.0/xlsx.core.min.js"></script>

<!-- FileSaver.js for file download -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/FileSaver.js/1.3.8/FileSaver.min.js"></script>
```

---

## 핵심 패턴

### 1. 기본 구조

```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>OpenAPI 활용 애플리케이션</title>
    <!-- 라이브러리 CDN -->
</head>
<body>
    <div class="container">
        <!-- I. API 인증키 입력 -->
        <div class="section">
            <input type="text" id="apiKey" placeholder="인증키 입력">
        </div>
        
        <!-- II. 검색 조건 입력 -->
        <div class="section">
            <!-- 검색 폼 -->
        </div>
        
        <!-- III. 검색 결과 -->
        <div class="section" id="resultSection">
            <!-- 결과 테이블 -->
        </div>
    </div>
    
    <script>
        // JavaScript 코드
    </script>
</body>
</html>
```

### 2. 전역 변수 패턴

```javascript
// ========================================
// 전역 변수
// ========================================
let currentData = [];           // 현재 페이지 데이터
let currentPage = 1;            // 현재 페이지 번호
let totalCount = 0;             // 전체 건수
let numOfRows = 50;             // 페이지당 결과 수

// 전체 다운로드 관련
let isDownloadingAll = false;   // 다운로드 진행 여부
let downloadCancelled = false;  // 취소 여부
let allDownloadedData = [];     // 수집된 전체 데이터
```

---

## API 인증키 처리

### 1. 인증키 타입 이해

공공데이터포털은 두 가지 형태의 인증키를 제공합니다:

- **인코딩 인증키**: `abc123%2Bdef456%3D%3D` (특수문자가 URL 인코딩됨)
- **디코딩 인증키**: `abc123+def456==` (원본 형태)

### 2. 권장 방법: 디코딩 인증키 사용

```javascript
// ✅ 권장: 디코딩 인증키를 사용하고 URLSearchParams가 자동 인코딩
const params = {
    ServiceKey: apiKey,  // 디코딩 인증키 입력
    pageNo: 1,
    numOfRows: 10,
    _type: 'json'
};

const queryString = new URLSearchParams(params).toString();
const url = `${BASE_URL}?${queryString}`;
```

### 3. HTML 주석에 안내 추가

```html
<!-- 
    ⚠️ API 인증키: 디코딩(Decoding) 인증키를 사용하세요
    
    공공데이터포털 > 마이페이지 > 인증키 발급현황
    "일반 인증키(Decoding)" 열의 값을 복사하여 사용
-->
```

---

## 대량 데이터 처리

### 1. 전체 데이터 다운로드 패턴

```javascript
/**
 * 전체 데이터 다운로드
 * 모든 페이지를 순회하며 데이터 수집
 */
async function downloadAllData() {
    if (totalCount === 0) {
        alert('검색 결과가 없습니다.');
        return;
    }

    // 확인 메시지
    const confirmed = confirm(
        `전체 ${totalCount.toLocaleString()}건의 데이터를 다운로드하시겠습니까?`
    );
    if (!confirmed) return;

    // 초기화
    isDownloadingAll = true;
    downloadCancelled = false;
    allDownloadedData = [];

    // 진행 상태 모달 표시
    showProgressModal();

    try {
        const startTime = Date.now();
        const totalPages = Math.ceil(totalCount / numOfRows);

        // 모든 페이지 순회
        for (let pageNo = 1; pageNo <= totalPages; pageNo++) {
            // 취소 확인
            if (downloadCancelled) {
                updateProgressText('다운로드가 취소되었습니다.');
                await sleep(1500);
                hideProgressModal();
                return;
            }

            // 진행률 업데이트
            const progress = (pageNo / totalPages) * 100;
            updateProgressBar(progress);
            updateProgressText(`페이지 ${pageNo}/${totalPages} 다운로드 중...`);

            // API 호출 (재시도 로직 포함)
            const params = buildSearchParams(pageNo);
            const data = await fetchWithRetry(params, 3);

            // 데이터 추가
            const body = data.response.body;
            let items = body.items?.item || [];
            if (!Array.isArray(items)) {
                items = [items];
            }
            allDownloadedData.push(...items);

            // API 호출 간격 (초당 요청 제한 고려)
            await sleep(100);
        }

        // 엑셀 저장
        saveAllDataToExcel(allDownloadedData);
        hideProgressModal();
        alert(`전체 ${allDownloadedData.length.toLocaleString()}건 다운로드 완료!`);

    } catch (error) {
        console.error('다운로드 오류:', error);
        hideProgressModal();
        alert(`오류 발생: ${error.message}`);
    } finally {
        isDownloadingAll = false;
    }
}
```

### 2. 재시도 로직 패턴

```javascript
/**
 * 재시도 로직이 포함된 API 호출
 * @param {Object} params - API 파라미터
 * @param {number} maxRetries - 최대 재시도 횟수
 */
async function fetchWithRetry(params, maxRetries = 3) {
    const BASE_URL = 'YOUR_API_BASE_URL';
    let lastError = null;

    for (let attempt = 0; attempt <= maxRetries; attempt++) {
        try {
            // 재시도 시 대기 (지수 백오프)
            if (attempt > 0) {
                const waitTime = 1000 * Math.pow(2, attempt - 1);
                console.log(`재시도 ${attempt}/${maxRetries}, ${waitTime}ms 대기...`);
                await sleep(waitTime);
            }

            // API 호출
            const queryString = new URLSearchParams(params).toString();
            const url = `${BASE_URL}?${queryString}`;

            // 타임아웃 설정
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 30000);

            const response = await fetch(url, {
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                throw new Error(`HTTP Error: ${response.status}`);
            }

            const data = await response.json();

            // API 응답 확인
            const header = data.response.header;
            if (header.resultCode !== '00') {
                throw new Error(`API Error [${header.resultCode}]: ${header.resultMsg}`);
            }

            return data;

        } catch (error) {
            lastError = error;
            
            if (error.name === 'AbortError') {
                console.error('API 호출 시간 초과');
            } else {
                console.error(`API 호출 오류 (${attempt + 1}/${maxRetries + 1}):`, error);
            }

            // 마지막 시도가 아니면 계속
            if (attempt < maxRetries) {
                continue;
            }
        }
    }

    throw lastError || new Error('API 호출 실패');
}

/**
 * 대기 함수
 */
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
```

### 3. 진행 상태 표시 패턴

#### HTML 구조
```html
<!-- 진행 상태 모달 -->
<div id="progressModal" class="progress-modal" style="display: none;">
    <div class="progress-modal-content">
        <h3>데이터 다운로드 중...</h3>
        <div class="progress-info">
            <div id="progressText">준비 중...</div>
            <div class="progress-bar-container">
                <div class="progress-bar" id="progressBar"></div>
            </div>
            <div id="progressDetails"></div>
        </div>
        <button class="btn btn-danger" onclick="cancelDownload()">취소</button>
    </div>
</div>
```

#### JavaScript 함수
```javascript
function showProgressModal() {
    document.getElementById('progressModal').style.display = 'flex';
    updateProgressBar(0);
}

function hideProgressModal() {
    document.getElementById('progressModal').style.display = 'none';
}

function updateProgressBar(percent) {
    const bar = document.getElementById('progressBar');
    bar.style.width = percent + '%';
    bar.textContent = Math.round(percent) + '%';
}

function updateProgressText(text) {
    document.getElementById('progressText').textContent = text;
}

function updateProgressDetails(text) {
    document.getElementById('progressDetails').textContent = text;
}
```

---

## 엑셀 다운로드 구현

### 1. 기본 패턴

```javascript
/**
 * 엑셀 다운로드
 * @param {Array} items - 다운로드할 데이터 배열
 */
function downloadExcel(items) {
    if (items.length === 0) {
        alert('다운로드할 데이터가 없습니다.');
        return;
    }

    // 엑셀 데이터 구성
    const excelData = items.map((item, index) => ({
        '번호': index + 1,
        '컬럼1': item.field1 || '',
        '컬럼2': item.field2 || '',
        '컬럼3': item.field3 || ''
        // 필요한 컬럼 추가
    }));

    // 워크북 생성
    const wb = XLSX.utils.book_new();
    const ws = XLSX.utils.json_to_sheet(excelData);

    // 열 너비 설정
    ws['!cols'] = [
        { wch: 8 },   // 번호
        { wch: 20 },  // 컬럼1
        { wch: 30 },  // 컬럼2
        { wch: 15 }   // 컬럼3
    ];

    XLSX.utils.book_append_sheet(wb, ws, '데이터');

    // 파일명 생성 (현재 날짜시간)
    const now = new Date();
    const fileName = `데이터_${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, '0')}${String(now.getDate()).padStart(2, '0')}_${String(now.getHours()).padStart(2, '0')}${String(now.getMinutes()).padStart(2, '0')}.xlsx`;

    // 다운로드
    const wbout = XLSX.write(wb, { bookType: 'xlsx', type: 'binary' });
    saveAs(new Blob([s2ab(wbout)], { type: "application/octet-stream" }), fileName);
}

/**
 * 문자열을 ArrayBuffer로 변환
 */
function s2ab(s) {
    const buf = new ArrayBuffer(s.length);
    const view = new Uint8Array(buf);
    for (let i = 0; i < s.length; i++) {
        view[i] = s.charCodeAt(i) & 0xFF;
    }
    return buf;
}
```

### 2. 날짜 포맷팅

```javascript
/**
 * 날짜 포맷팅 (YYYYMMDD -> YYYY-MM-DD)
 */
function formatDate(dateStr) {
    if (!dateStr || dateStr.length !== 8) return '-';
    return `${dateStr.substring(0, 4)}-${dateStr.substring(4, 6)}-${dateStr.substring(6, 8)}`;
}
```

---

## 에러 처리 베스트 프랙티스

### 1. API 에러 코드 처리

```javascript
/**
 * API 에러 처리
 */
function handleApiError(errorCode, errorMsg) {
    let message = `API 오류 [${errorCode}]: ${errorMsg}\n\n`;

    switch (errorCode) {
        case '3':
            message += '검색 결과가 없습니다. 검색 조건을 변경해 주세요.';
            break;
        case '22':
            message += '일일 트래픽 제한을 초과했습니다.';
            break;
        case '30':
            message += '등록되지 않은 인증키입니다. 인증키를 확인해 주세요.';
            break;
        case '31':
            message += '기한이 만료된 인증키입니다. 인증키를 재발급 받으세요.';
            break;
        default:
            message += '잠시 후 다시 시도해 주세요.';
    }

    alert(message);
}
```

### 2. 네트워크 에러 처리

```javascript
try {
    const response = await fetch(url);
    // ...
} catch (error) {
    if (error.name === 'AbortError') {
        alert('API 호출 시간 초과. 잠시 후 다시 시도해 주세요.');
    } else if (error.message.includes('NetworkError')) {
        alert('네트워크 연결 오류. 인터넷 연결을 확인하세요.');
    } else {
        alert(`오류 발생: ${error.message}`);
    }
}
```

### 3. 부분 데이터 저장 옵션

```javascript
catch (error) {
    console.error('다운로드 오류:', error);
    hideProgressModal();
    
    // 현재까지 수집된 데이터 저장 옵션
    if (allDownloadedData.length > 0) {
        const savePartial = confirm(
            `다운로드 중 오류가 발생했습니다.\n\n${error.message}\n\n현재까지 수집된 ${allDownloadedData.length}건의 데이터를 다운로드하시겠습니까?`
        );
        if (savePartial) {
            saveAllDataToExcel(allDownloadedData);
        }
    } else {
        alert(`오류 발생: ${error.message}`);
    }
}
```

---

## 재사용 가능한 코드 템플릿

### 1. 검색 파라미터 구성

```javascript
/**
 * 검색 파라미터 구성
 */
function buildSearchParams(pageNo = 1) {
    const apiKey = document.getElementById('apiKey').value.trim();
    const numOfRows = parseInt(document.getElementById('numOfRows').value);

    const params = {
        ServiceKey: apiKey,
        pageNo: pageNo,
        numOfRows: numOfRows,
        _type: 'json'
    };

    // 선택적 파라미터 추가
    const param1 = document.getElementById('param1').value;
    const param2 = document.getElementById('param2').value;

    if (param1) params.param1 = param1;
    if (param2) params.param2 = param2;

    return params;
}
```

### 2. 페이징 UI 업데이트

```javascript
/**
 * 페이징 업데이트
 */
function updatePagination() {
    const container = document.getElementById('paginationContainer');
    container.innerHTML = '';

    const totalPages = Math.ceil(totalCount / numOfRows);

    // 이전 버튼
    const prevBtn = document.createElement('button');
    prevBtn.className = 'pagination-btn';
    prevBtn.textContent = '« 이전';
    prevBtn.disabled = currentPage === 1;
    prevBtn.onclick = () => searchData(currentPage - 1);
    container.appendChild(prevBtn);

    // 페이지 번호 버튼
    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPages, currentPage + 2);

    for (let i = startPage; i <= endPage; i++) {
        const pageBtn = document.createElement('button');
        pageBtn.className = 'pagination-btn' + (i === currentPage ? ' active' : '');
        pageBtn.textContent = i;
        pageBtn.onclick = () => searchData(i);
        container.appendChild(pageBtn);
    }

    // 다음 버튼
    const nextBtn = document.createElement('button');
    nextBtn.className = 'pagination-btn';
    nextBtn.textContent = '다음 »';
    nextBtn.disabled = currentPage === totalPages;
    nextBtn.onclick = () => searchData(currentPage + 1);
    container.appendChild(nextBtn);
}
```

### 3. 로딩 표시

```javascript
/**
 * 로딩 표시
 */
function showLoading() {
    document.getElementById('loadingIndicator').classList.add('active');
}

/**
 * 로딩 숨김
 */
function hideLoading() {
    document.getElementById('loadingIndicator').classList.remove('active');
}
```

---

## 체크리스트

개발 완료 전 확인사항:

- [ ] API 인증키 입력 폼 구현
- [ ] 검색 조건 입력 폼 구현
- [ ] 단일 페이지 조회 기능
- [ ] 전체 데이터 다운로드 기능
- [ ] 재시도 로직 구현
- [ ] 진행 상태 표시
- [ ] 에러 처리
- [ ] 엑셀 다운로드
- [ ] 페이징 UI
- [ ] CORS 이슈 해결 방법 안내
- [ ] 인증키 발급 방법 안내
- [ ] 주석 추가
- [ ] 브라우저 테스트 (Chrome, Edge)

---

## 참고 자료

- [공공데이터포털](https://www.data.go.kr/)
- [SheetJS 문서](https://docs.sheetjs.com/)
- [FileSaver.js GitHub](https://github.com/eligrey/FileSaver.js/)
- [MDN Web Docs - Fetch API](https://developer.mozilla.org/ko/docs/Web/API/Fetch_API)
- [MDN Web Docs - AbortController](https://developer.mozilla.org/ko/docs/Web/API/AbortController)

---

## 라이선스

이 가이드라인은 자유롭게 사용, 수정, 배포할 수 있습니다.

---

**작성**: 2026-01-14  
**버전**: 1.0

const http = require('http');
const https = require('https');
const url = require('url');

const PORT = 8080;
const API_BASE_URL = 'http://apis.data.go.kr';

// CORS 헤더 추가
function addCorsHeaders(res) {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
}

// 프록시 서버
const server = http.createServer((req, res) => {
    addCorsHeaders(res);

    // OPTIONS 요청 처리 (CORS preflight)
    if (req.method === 'OPTIONS') {
        res.writeHead(200);
        res.end();
        return;
    }

    // API 요청만 프록시
    if (req.url.startsWith('/api/')) {
        const targetUrl = API_BASE_URL + req.url.substring(4);

        console.log(`[Proxy] ${req.method} ${targetUrl}`);

        const parsedUrl = url.parse(targetUrl);
        const options = {
            hostname: parsedUrl.hostname,
            port: parsedUrl.port || 80,
            path: parsedUrl.path,
            method: req.method,
            headers: {
                ...req.headers,
                host: parsedUrl.hostname
            }
        };

        const proxyReq = http.request(options, (proxyRes) => {
            res.writeHead(proxyRes.statusCode, proxyRes.headers);
            proxyRes.pipe(res);
        });

        proxyReq.on('error', (error) => {
            console.error('[Proxy Error]', error);
            res.writeHead(500);
            res.end('Proxy Error: ' + error.message);
        });

        req.pipe(proxyReq);
    } else {
        // 정적 파일 서빙
        const fs = require('fs');
        const path = require('path');

        let filePath = '.' + req.url;
        if (filePath === './') {
            filePath = './병원정보조회_웹앱_로컬용.html';
        }

        const extname = String(path.extname(filePath)).toLowerCase();
        const mimeTypes = {
            '.html': 'text/html',
            '.js': 'text/javascript',
            '.css': 'text/css',
            '.json': 'application/json',
            '.png': 'image/png',
            '.jpg': 'image/jpg',
            '.gif': 'image/gif',
            '.svg': 'image/svg+xml',
            '.wav': 'audio/wav',
            '.mp4': 'video/mp4',
            '.woff': 'application/font-woff',
            '.ttf': 'application/font-ttf',
            '.eot': 'application/vnd.ms-fontobject',
            '.otf': 'application/font-otf',
            '.wasm': 'application/wasm'
        };

        const contentType = mimeTypes[extname] || 'application/octet-stream';

        fs.readFile(filePath, (error, content) => {
            if (error) {
                if (error.code == 'ENOENT') {
                    res.writeHead(404);
                    res.end('File not found: ' + filePath);
                } else {
                    res.writeHead(500);
                    res.end('Server Error: ' + error.code);
                }
            } else {
                res.writeHead(200, { 'Content-Type': contentType });
                res.end(content, 'utf-8');
            }
        });
    }
});

server.listen(PORT, () => {
    console.log('='.repeat(60));
    console.log('병원정보조회 웹 애플리케이션 프록시 서버');
    console.log('='.repeat(60));
    console.log(`서버 실행 중: http://localhost:${PORT}`);
    console.log('');
    console.log('브라우저에서 다음 주소로 접속하세요:');
    console.log(`  http://localhost:${PORT}/병원정보조회_웹앱_로컬용.html`);
    console.log('');
    console.log('종료하려면 Ctrl+C를 누르세요.');
    console.log('='.repeat(60));
});

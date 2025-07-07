import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

// 성능 측정 (선택사항)
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// 웹 바이탈 성능 측정
function sendToAnalytics(metric: any) {
  // 실제 환경에서는 Google Analytics나 다른 분석 도구로 전송
  console.log('Web Vitals:', metric);
}

// Core Web Vitals 측정
getCLS(sendToAnalytics);
getFID(sendToAnalytics);
getFCP(sendToAnalytics);
getLCP(sendToAnalytics);
getTTFB(sendToAnalytics);
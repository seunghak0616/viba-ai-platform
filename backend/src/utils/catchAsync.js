/**
 * Async error catching utility
 * Express async/await 에러 처리를 위한 래퍼 함수
 */

/**
 * async 함수의 에러를 자동으로 catch하여 next()로 전달하는 래퍼
 * @param {Function} fn - async 함수
 * @returns {Function} Express 미들웨어 함수
 */
export const catchAsync = (fn) => {
  return (req, res, next) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
};

export default catchAsync;
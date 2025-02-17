/** axios 集中呼叫 Api 方法 */

import axios from "axios";
import router from "@/router"; // 確保可以跳轉頁面

const api = axios.create({
    baseURL: import.meta.env.VITE_API_PATH,
    headers: { "Content-Type": "application/json" },
    withCredentials: true
});

// 🔹 Request 攔截器（每次請求前）
api.interceptors.request.use(
    (config) => {
        const token = sessionStorage.getItem("access_token"); // ✅ 從 sessionStorage 取出 Token
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;  // ✅ 設定 Authorization
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// 🔹 Response 攔截器
api.interceptors.response.use(
    async (response) => {
        if (response.data.access_token) {
            sessionStorage.setItem("access_token", response.data.access_token);
        }
        return response;
    },
    (error) => {
        if (error.response) {
            const { status, config } = error.response;
            if (error.response.data.access_token) {
                sessionStorage.setItem("access_token", error.response.data.access_token);
            }
            // 只在「非登入 API」時才觸發登出
            if (status === 401 && config.url !== "/login" && data?.error?.includes("Token")) {
                sessionStorage.removeItem("access_token"); // 移除 Token
                router.push("/");  // 401 時自動跳轉到登入頁
            }
        }
        return Promise.reject(error);
    }
);

export default api;

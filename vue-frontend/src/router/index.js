import { createRouter, createWebHistory } from 'vue-router'
import axios from "@/utils/global/api"; // ✅ 確保 Axios 可用

/** 入口頁面 */
const Login = () => import('@/views/entry/Login.vue') // 登入

/** 系統頁面 */
const Home = () => import('@/views/system/Home.vue') // 首頁
const Setting = () => import('@/views/system/Setting.vue') // 編輯設定
const Reading = () => import('@/views/system/Reading.vue') // 閱讀模式
const AddEditResource = () => import('@/views/system/AddEditResource.vue') // 新增/編輯頁面
const TEST = () => import('@/views/system/TEST.vue') // 測試介面

const routes = [
    { path: '/', name: 'Login', component: Login },
    { path: '/home', name: 'Home', component: Home, meta: { requiresAuth: true } },
    { path: '/setting', name: 'Setting', component: Setting, meta: { requiresAuth: true } },
    { path: '/reading', name: 'Reading', component: Reading, meta: { requiresAuth: true } },
    { path: '/addEditResource', name: 'AddEditResource', component: AddEditResource, meta: { requiresAuth: true }},
    { path: '/TEST', name: 'TEST', component: TEST, meta: { requiresAuth: true }}
]

const router = createRouter({
    history: createWebHistory(),
    routes
});

// 全局導航守衛（確保未登入的使用者只能進入 `/login`）
router.beforeEach(async (to, from, next) => {
    if (to.meta.requiresAuth) {
        try {
            // 🔹 向後端發送 API，確認 Token 是否有效
            await axios.get("/checkToken"); // 這會自動帶上 Cookie，後端驗證 Token
            next(); // ✅ Token 有效，繼續導航
        } catch (error) {
            console.warn("未登入或 Token 過期，重新導向 Login");
            next({ path: '/' }); // ❌ Token 無效，導向登入頁
        }
    } else {
        next(); // 不需要登入的頁面，直接進入
    }
});

export default router;

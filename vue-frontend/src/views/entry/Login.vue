<template>
    <div class="nomal-background views-entry">
        <div class="container">
            <!-- 標題 -->
            <div class="text-center">
                <p class="omc-text xlarge mb-3">登入</p>
            </div>
            <div class="mb-2">
                <!-- 帳號 -->
                <div class="mb-3">
                    <FloatLabel variant="on">
                        <InputText id="account" v-model="account" @keyup.enter="login" :invalid="!accountInvalid && !account" class="w-100" />
                        <label for="account">帳號</label>
                    </FloatLabel>
                </div>
                <!-- 密碼 -->
                <div class="mb-3">
                    <FloatLabel variant="on">
                        <Password id="password" v-model="password" @keyup.enter="login" :invalid="!passwordInvalid && !password" :feedback="false" toggleMask />
                        <label for="password">密碼</label>
                    </FloatLabel>
                </div>

                <!-- 登入按鈕 -->
                <button class="omc-btn nomal p-2" @click="login">登入</button>
            </div>

            <!-- 錯誤訊息 -->
            <p v-if="errorMessage" class="omc-text attention">{{ errorMessage }}</p>
        </div>
    </div>
</template>

<script>
export default {
    data() {
        return {
            account: '',
            password: '',
            accountInvalid: true,
            passwordInvalid: true,
            errorMessage: ''
        }
    },
    created() {
        sessionStorage.removeItem("access_token");
    },
    methods: {
        async login() {
            if (!this.account) {
                this.accountInvalid = false;
                return;
            }
            if (!this.password) {
                this.passwordInvalid = false;
                return;
            }

            try {
                const response = await this.$axios.post("/login", {  
                    account: this.account,
                    password: this.password
                });

                console.log("登入成功:", response.data);

                // 跳轉到首頁
                this.$router.push("/home");

            } catch (error) {
                console.error("登入失敗:", error);
                this.errorMessage = error.response?.data?.error || "登入失敗，請重試";
            }
        }
    }
}
</script>

<template>
    <div class="nomal-background views-home">
        <!-- 標題 -->
        <div class="text-center">
            <p class="omc-text xxlarge p-3">互動式閱讀平台</p>
        </div>
        <!-- 選項 -->
        <div class="d-flex">
            <div class="home-btn" @click="goToPage('Setting')">
                <button class="icon">
                    <i class="bi bi-pencil-fill"></i>
                </button>
                <p class="text">編輯設<span>定</span></p>
            </div>
            <div class="home-btn" @click="goToPage('Reading')">
                <button class="icon">
                    <i class="bi bi-book-fill"></i>
                </button>
                <p class="text">閱讀模<span>式</span></p>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    methods: {
        goToPage(pageName) {
            this.$router.push({ name: pageName })
        }
    }
}
</script>

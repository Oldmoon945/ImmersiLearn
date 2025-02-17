<template>
    <div class="nomal-background views-addEditResource row">
        <!-- 左邊、下方區塊 -->
        <div :class="editMode ? 'col-9' : 'col-12'">
            <!-- 上方按鈕區塊 -->
            <div class="back-btn text-end">
                <i class="bi bi-x-lg omc-point omc-text xxlarge nomal bold pe-2" @click="goToPage('Setting')"></i>
            </div>
            <!-- 圖片區域 -->
            <div class="px-1 py-0 px-sm-3 py-sm-5">
                <div class="omc-container p-2 d-flex justify-content-center align-items-center" 
                    style="height: calc(100vh - 135px); overflow: hidden;" 
                    @click="editMode ? '' : triggerAction('uploadImg')"
                >
                    <div v-if="confirmCapturedImage" class="position-relative w-100 h-100 d-flex justify-content-center align-items-center">
                        <img 
                            ref="imageRef"
                            :src="confirmCapturedImage" 
                            class="position-absolute"
                            style="width: auto; height: auto; max-width: 100%; max-height: 100%; object-fit: contain; display: block;">
                        <!-- Canvas 疊加在圖片上 -->
                        <canvas 
                            ref="canvasRef" 
                            class="position-absolute"
                            @mousedown="startDrawing"
                            @mousemove="drawPreview"
                            @mouseup="finishDrawing">
                        </canvas>
                    </div>
                    <div v-else class="no-image text-center">
                        <div>
                            <i class="bi bi-images" style="font-size: 100px;"></i>
                            <p class="omc-text large">上傳圖片</p>
                        </div>
                    </div>
                </div>
            </div>
            <!-- 下方區塊 -->
            <div class="end-area d-flex" :style="editMode ? 'width: 73%' : 'width: 100%'">
                <button class="omc-btn nomal w-100 me-2 omc-text xxlarge" @click="triggerAction('saveResource')">儲存</button>
                <button v-if="editMode" class="omc-btn nomal w-100 omc-text xxlarge"  @click="triggerAction('changeMode', 'viewMode')">檢視模式</button>
                <button v-else class="omc-btn nomal w-100 omc-text xxlarge" @click="triggerAction('changeMode', 'editMode')">編輯模式</button>
            </div>
        </div>
        <!-- 右方編輯區域 -->
        <div class="edit-area omc-text" :class="editMode ? 'col-3' : 'col-0'" v-if="editMode">
            <div class="setting-area">
                <div class="d-flex mb-3">
                    <span>顏色：</span>
                    <input type="color" class="small-color-picker" v-model="editContent.color" :disabled='is_edit_setting'>
                </div>
                <div class="d-flex align-items-center mb-2">
                    <span style="min-width:4rem">模式：</span>
                    <Select v-model="editContent.triger" editable :options="triggerOptions" optionLabel="name" placeholder="選擇模式" class="w-full md:w-56" />
                </div>
                <FloatLabel variant="in" class="mb-2">
                    <label for="message">內容：</label>
                    <Textarea id="message" v-model="editContent.message" rows="5" class="w-100" />
                </FloatLabel>
            </div>
            <div>
                <button v-if="is_edit_setting" class="omc-btn success omc-text xxlarge" @click="triggerAction('confirmEditSetting')">變更</button>
                <button v-else class="omc-btn success omc-text xxlarge" @click="triggerAction('addSetting')">新增</button>
            </div>
            <hr>
            <div class="setting-list-area">
                <template v-for="item in setting_list" :key="item.id">
                    <div class="item mb-2" v-if="item.status != 'dele'">
                        
                        <div class="start" :style="{ background : item.color}" @click="triggerAction('editSetting', item)">
                            <span>{{ item.triger.name }} </span>
                        </div>
                        <div class="center" @click="triggerAction('editSetting', item)">{{ item.message }}</div>
                        
                        <div class="end" @click="triggerAction('deleteSetting', item.color)">
                            <i class="bi bi-trash3-fill omc-text attention omc-point"></i>
                        </div>
                </div>
                </template>
            </div>
            <button class="omc-btn attention omc-text xxlarge">刪除</button>
        </div>
    </div>
    <!-- 上傳圖片 Dialog -->
    <Dialog v-model:visible="dialog_uploadImg_show" modal header="上傳圖片" :style="{ width: isOpenCamera ? '50vw' : '25rem'}">
        <canvas ref="canvasElement" style="display: none;"></canvas>
        <div v-if="isOpenCamera" class="text-center">
            <div v-if="capturedImage" class="text-center">
                <div style="width:40vw ; justify-self: center;">
                    <img :src="capturedImage" alt="Captured Image" style="width: 100%; height: auto;">
                </div>
                <button class="omc-btn nomal px-3 w-100" @click="triggerAction('resetCapture')">重新拍攝</button>
            </div>
            <div v-else>
                <div style="width:40vw; justify-self: center;">
                    <video ref="videoElement" autoplay style="width: 100%; height: auto;"></video>    
                </div>
                <button class="omc-btn nomal px-3 w-100" @click="triggerAction('captureImg')">拍攝</button>
            </div>
        </div>
        <div v-else>
            <p class="mb-2">選擇上傳圖片方式</p>
            <div class="d-flex">
                <button class="omc-btn nomal me-2 p-3" @click="triggerAction('fileUpload')">
                    <i class="bi bi-image" style="font-size:80px"></i>
                    <p class="mt-2">檔案上傳</p>
                </button>
                <input type="file" id="fileUpload" ref="fileUpload" style="display: none;" @change="handleFileUpload">
                <button class="omc-btn nomal p-3" @click="cameraSwitch">
                    <i class="bi bi-camera" style="font-size:80px"></i>
                    <p class="mt-2">影像拍攝</p>
                </button>
            </div>
        </div>
        <template #footer>
            <div>
                <div v-if="isOpenCamera" class="d-flex">
                    <button v-if="capturedImage" class="omc-btn nomal px-3 me-2" @click="triggerAction('confirmImage')">確認</button>
                    <button class="omc-btn nomal px-3" @click="isOpenCamera = false">返回</button>
                </div>
                <button v-else class="omc-btn nomal px-3" @click="dialog_uploadImg_show = false">關閉</button>
            </div>
        </template>
    </Dialog>
    <!-- 儲存 Dialog -->
    <Dialog v-model:visible="dialog_save_show" modal header="儲存" :style="{ width:'50vw'}">
        <div>
            <p class="mb-2">說明 (上限255字):</p>
            <Textarea id="message" v-model="resourceData.description" rows="10" class="w-100" />
        </div>
        <template #footer>
            <div class="d-flex">
                <button class="omc-btn nomal px-3 me-2" @click="triggerAction('confirmSaveResource')">確認</button>
                <button class="omc-btn nomal px-3" @click="dialog_save_show = false">關閉</button>
            </div>
        </template>
    </Dialog>
</template>

<script>
export default {
    data() {
        return {
            editMode: false,
            triggerOptions: [
                { name: '停留', code: 'hover' },
                { name: '經過', code: 'course' }
            ],
            editContent: {
                color: '#ff0000',
                triger: null,
                message: '',
                mark: {
                    x: null,
                    y: null, 
                    width: null, 
                    height: null,
                    originalPictureWidth: 0, // 圖片原始寬度
                    originalPictureHeight: 0, // 圖片原始高度
                }
            },
            resourceData : {
                id: null,
                description: null,
                picture: null,
            },
            setting_list: [],
            is_edit_setting: false,

            // Dialog
            dialog_uploadImg_show: false,
            dialog_save_show: false,

            // camera
            videoStream: null, // 存儲相機串流
            isOpenCamera: false,
            isCapture: false,
            capturedImage: null,
            confirmCapturedImage: null,

            // draw picture
            isDrawing: false, // 是否正在繪製
            minMoveDistance: 5, // 最小移動距離，小於這個值不繪製
            drawParameter: {
                startX: 0, // 框選起點 X
                startY: 0, // 框選起點 Y
                currentX: 0, // 當前滑鼠 X 位置
                currentX: 0, // 當前滑鼠 Y 位置
                originalPictureWidth: 0, // 圖片原始寬度
                originalPictureHeight: 0, // 圖片原始高度
            }
        }
    },
    watch: {
        isOpenCamera(newVal) {
            if (!newVal) {
                this.stopCamera();
            }
        },
        dialog_uploadImg_show(newVal) {
            if (newVal) {
                if (this.confirmCapturedImage) {
                    this.capturedImage = this.confirmCapturedImage;
                }
            } else {
                this.stopCamera();
                this.isOpenCamera = false
                this.capturedImage = null;
            }
        }
    },
    created() {
        this.pageInit()
    },
    methods: {
        pageInit() {
            if (this.$route.query.ID) {
                this.getResourceData()
            }
            this.newSetting()
        },
        goToPage(pageName) {
            this.$router.push({ name: pageName })
        },
        async triggerAction(status, item) {
            if (status == 'changeMode') {
                if ( item == 'viewMode') {
                    this.newSetting()
                    this.adjustCanvasSize()
                    this.redrawBoxes()
                    this.editMode = false
                } else if ( item == 'editMode' ) {
                    if (!this.confirmCapturedImage) return this.sweetAlert('請先上傳圖片', 'error')
                    this.editMode = true
                    this.adjustCanvasSize()
                    this.redrawBoxes()
                }
            } else if (status == 'fileUpload') {
                this.$refs.fileUpload.click();
            } else if (status == 'confirmImage') {
                this.confirmCapturedImage = JSON.parse(JSON.stringify(this.capturedImage))
                this.dialog_uploadImg_show = false
                this.sweetAlert('成功', 'success')
            } else if (status == 'resetCapture') {
                this.capturedImage = null;
                this.cameraSwitch('resetCapture');
            } else if (status == 'captureImg') {
                this.isCapture = true;
                const video = this.$refs.videoElement;
                const canvas = this.$refs.canvasElement;
                const context = canvas.getContext("2d");

                // **強制 canvas 尺寸與 video 一致**
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;

                // 畫面裁切並填充至 canvas
                context.drawImage(video, 0, 0, canvas.width, canvas.height);

                // 轉換為 PNG Data URL
                this.capturedImage = canvas.toDataURL("image/png");

                // 停止攝影機
                this.stopCamera();
            } else if (status == 'addSetting') {
                if (!this.editContent.mark.width) return this.sweetAlert('請在圖像上繪製互動區域', 'error')
                if (this.editContent.message == '') return this.sweetAlert('請輸入內容', 'error')
                let addEditContent = {
                    color: this.editContent.color,
                    triger: this.editContent.triger,
                    message: this.editContent.message,
                    mark: this.editContent.mark,
                    status: 'add'
                }
                this.setting_list.push(addEditContent)
                this.newSetting()
            } else if (status == 'deleteSetting') {
                this.setting_list = this.setting_list.map(setting => {
                    if (item === setting.color) {
                        if (setting.status === 'org') {
                            return {...setting, status: 'dele'};
                        } else if (setting.status === 'add') {
                            return null;
                        }
                    }
                    return setting;
                }).filter(setting => setting !== null);
                this.redrawBoxes()
            } else if (status == 'uploadImg') {
                if (this.setting_list.length > 0) return
                this.dialog_uploadImg_show = true
            } else if (status == 'editSetting') {
                this.editContent = JSON.parse(JSON.stringify(item))
                this.redrawBoxes()
                this.is_edit_setting = true
            } else if (status == 'confirmEditSetting') {
                this.setting_list.forEach(item => {
                    if(item.color === this.editContent.color) {
                        item.triger = this.editContent.triger
                        item.message = this.editContent.message
                        item.triger = this.editContent.triger
                        item.mark= this.editContent.mark
                        item.status = 'edit'
                    }
                })
                this.is_edit_setting = false
                this.newSetting()
                this.redrawBoxes()
            } else if (status == 'saveResource') {
                if (!this.confirmCapturedImage) return this.sweetAlert('資料不齊全', 'error')
                this.dialog_save_show = true
            } else if (status == 'confirmSaveResource') {
                const data = {
                    action: this.$route.query.ID ? 'edit' : 'create',
                    head: {
                        id: this.$route.query.ID,
                        description: this.resourceData.description,
                    }
                }
                if (this.confirmCapturedImage !== this.resourceData.picture) {
                    data.head.picture = this.confirmCapturedImage
                    data.head.picture_small = await this.resizeImage(this.confirmCapturedImage)
                }
                if (data.action == 'create') { 
                    data.detail = this.setting_list
                } else {
                    data.detail = []
                    this.setting_list.forEach(item => {
                        if(item.status != 'org') {
                            data.detail.push(item)
                        }
                    })
                }
                this.saveResource(data)
            }
        },
        cameraSwitch(status) {
            if (this.confirmCapturedImage && status != 'resetCapture') {
                this.isOpenCamera = true
            } else {
                this.isOpenCamera = true
                this.openCamera()    
            }
        },
        async openCamera() {
            try {
                // 開啟相機
                this.videoStream = await navigator.mediaDevices.getUserMedia({
                    video: {
                        width: { ideal: 1920 }, // 設定期望的寬度
                        height: { ideal: 1080 }, // 設定期望的高度
                        //facingMode: "user" // 可選 "environment"（後置攝像頭）或 "user"（前置攝像頭）
                    }
                });
                this.$nextTick(() => {
                    if (this.$refs.videoElement) {
                        this.$refs.videoElement.srcObject = this.videoStream;
                    }
                });
            } catch (error) {
                console.error("相機開啟失敗:", error);
            }
        },
        stopCamera() {
            if (this.videoStream) {
                this.videoStream.getTracks().forEach((track) => track.stop());
                this.videoStream = null;
            }
        },
        handleFileUpload(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    const img = new Image();
                    img.onload = () => {
                        const canvas = this.$refs.canvasElement;
                        const ctx = canvas.getContext("2d");

                        // 設定 canvas 為圖片原尺寸
                        canvas.width = img.width;
                        canvas.height = img.height;

                        // 直接繪製圖片，無縮放
                        ctx.drawImage(img, 0, 0, img.width, img.height);

                        // 轉換為 PNG Data URL
                        this.confirmCapturedImage = canvas.toDataURL("image/png");

                        // 關閉上傳視窗
                        this.dialog_uploadImg_show = false;
                        this.sweetAlert('成功', 'success');
                    };
                    img.src = e.target.result;
                };
                reader.readAsDataURL(file);
            }
        },
        newSetting() {
            let color;
            do {
                color = `#${Math.floor(Math.random() * 16777215).toString(16).padStart(6, '0')}`;
            } while (this.setting_list.some(item => item.color === color));
            this.editContent = {
                color: color,
                triger: this.triggerOptions[0],
                message: '',
                mark: {
                    x: null,
                    y: null, 
                    width: null, 
                    height: null
                }
            }
        },
        async saveResource(data) {
            try {
                const response = await this.$axios.post("/saveResource", data);
                this.sweetAlert('資料儲存成功', 'success');
                // 跳轉到首頁
                this.goToPage('Setting')

            } catch (error) {
                this.sweetAlert('資料儲存失敗', 'error');
                console.error("error:", error);
            }
        },
        async getResourceData() {
            const data = {
                id: this.$route.query.ID
            }
            try {
                const response = await this.$axios.post("/getInteractiveResource", data);
                this.resourceData = {
                    id: response.data.result.head.id,
                    description: response.data.result.head.description,
                    picture: `data:image/png;base64,${response.data.result.head.picture}`
                }
                this.confirmCapturedImage = `data:image/png;base64,${response.data.result.head.picture}`
                this.setting_list = []
                response.data.result.detail.forEach(item => {
                    this.setting_list.push({
                        id: item.id,
                        color: item.lable_data.color,
                        triger: item.lable_data.triger,
                        message: item.lable_data.message,
                        mark: item.lable_data.mark,
                        status: 'org'
                    })
                })
                console.log(this.setting_list)
            } catch (error) {
                this.sweetAlert('資料抓取失敗', 'error');
            }
        },
        // ---------- 繪圖 ------------
        adjustCanvasSize() {
            // 讓 Canvas 跟圖片尺寸匹配
            this.$nextTick(() => {
                const img = this.$refs.imageRef;
                const canvas = this.$refs.canvasRef;
                if (img && canvas) {
                    canvas.width = img.clientWidth;
                    canvas.height = img.clientHeight;
                    this.redrawBoxes();
                }
            });
        },
        redrawBoxes(preview = false) {
            const canvas = this.$refs.canvasRef;
            const ctx = canvas.getContext("2d");
        
            // 清除畫布
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            this.setting_list.forEach(setting => {
                if (setting.status != 'dele') {
                    // 計算縮放比例
                    const scaleX = canvas.clientWidth / setting.mark.originalPictureWidth;
                    const scaleY = canvas.clientHeight / setting.mark.originalPictureHeight;
                    // 圖像樣式
                    ctx.strokeStyle = setting.color;
                    ctx.lineWidth = 5;
                    // 繪圖
                    ctx.strokeRect(setting.mark.x * scaleX , setting.mark.y * scaleY, setting.mark.width * scaleX, setting.mark.height * scaleY);
                }
            });

            // 畫出已標記的長方形
            ctx.strokeStyle = this.editContent.color;
            ctx.lineWidth = 5;
            ctx.strokeRect(this.editContent.mark.x, this.editContent.mark.y, this.editContent.mark.width, this.editContent.mark.height);

            // 如果是正在繪製的預覽框
            if (preview && this.isDrawing) {
                let x = Math.min(this.drawParameter.startX, this.drawParameter.currentX);
                let y = Math.min(this.drawParameter.startY, this.drawParameter.currentY);
                let width = Math.abs(this.drawParameter.currentX - this.drawParameter.startX);
                let height = Math.abs(this.drawParameter.currentY - this.drawParameter.startY);
                ctx.strokeRect(x, y, width, height);
            }
        },
        startDrawing(event) {
            if(!this.editMode) return
            this.isDrawing = true;
            const canvas = this.$refs.canvasRef;
            const rect = canvas.getBoundingClientRect();
            this.drawParameter.startX = event.clientX - rect.left;
            this.drawParameter.startY = event.clientY - rect.top;
            this.drawParameter.currentX = this.drawParameter.startX;
            this.drawParameter.currentY = this.drawParameter.startY;
        },
        drawPreview(event) {
            if(!this.editMode) return
            if (!this.isDrawing) return;

            const canvas = this.$refs.canvasRef;
            const rect = canvas.getBoundingClientRect();
            this.drawParameter.currentX = event.clientX - rect.left;
            this.drawParameter.currentY = event.clientY - rect.top;

            // 重新繪製
            this.redrawBoxes(true);
        },
        finishDrawing() {
            if(!this.editMode) return
            if (!this.isDrawing) return;
            this.isDrawing = false;

            // 計算長方形寬高
            let width = Math.abs(this.drawParameter.currentX - this.drawParameter.startX);
            let height = Math.abs(this.drawParameter.currentY - this.drawParameter.startY);

            // 確保有移動，否則不繪製
            if (width < this.minMoveDistance && height < this.minMoveDistance) return;

            // 確保從左上角到右下角畫
            let x = Math.min(this.drawParameter.startX, this.drawParameter.currentX);
            let y = Math.min(this.drawParameter.startY, this.drawParameter.currentY);

            const canvas = this.$refs.canvasRef;

            // 存入標記座標
            this.editContent.mark = {
                x: x,
                y: y,
                width: width,
                height: height,
                originalPictureWidth: canvas.clientWidth, // 圖片原始寬度
                originalPictureHeight: canvas.clientHeight, // 圖片原始高度
            }
            
            // 重新繪製
            this.redrawBoxes();
        },
        resizeImage(picture) {
            return new Promise((resolve) => {
                const img = new Image();
                img.onload = () => {
                    const canvas = document.createElement("canvas");
                    const ctx = canvas.getContext("2d");

                    // 設定目標大小
                    const targetWidth = 100;
                    const targetHeight = 100;
                    canvas.width = targetWidth;
                    canvas.height = targetHeight;

                    // 在 canvas 上繪製縮小的圖片
                    ctx.drawImage(img, 0, 0, targetWidth, targetHeight);

                    // 轉換為 base64
                    const resizedDataUrl = canvas.toDataURL("image/png");
                    resolve(resizedDataUrl);
                };
                img.src = picture;
            });
        }
    }
}
</script>

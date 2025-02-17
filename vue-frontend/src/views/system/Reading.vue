<template>
    <div class="nomal-background views-reading">
        <!-- 上方按鈕區塊 -->
        <div class="d-flex justify-content-between p-2">
            <!-- 左 -->
            <div>
                <i class="bi bi-eye omc-point omc-text xxlarge nomal " v-if="tabViewOpen" @click="triggerAction('tabViewOpen', false)"></i>
                <i class="bi bi-eye-slash omc-point omc-text xxlarge nomal " v-else @click="triggerAction('tabViewOpen', true)"></i>
            </div>
            <!-- 右 -->
            <div>
                <i class="bi bi-x-lg omc-point omc-text xxlarge nomal bold pe-2" @click="goToPage('Home')"></i>
            </div>
        </div>
        <!-- 中間區塊 -->
        <div class="px-2 py-0 px-sm-5 py-sm-2">
            <div class="omc-container p-2 d-flex justify-content-center align-items-center" style="height: calc(100vh - 140px)">
                <div v-if="videoStream" style="width:45vw; justify-self: center;">
                    <!-- 視訊流 -->
                    <video ref="videoElement" autoplay class="video-style"></video>
                    
                    <!-- 疊加 Canvas -->
                    <div v-show="tabViewOpen">
                        <!-- 教材圖片 -->
                        <canvas ref="canvasRef" class="canvas-style" style="opacity: 0.4"></canvas>
                    </div>
                    <div>
                        <!-- 框選範圍 -->
                        <canvas ref="canvasRef1" class="canvas-style"></canvas>
                        <!-- 手部座標 -->
                        <canvas ref="fingerCanvas" class="canvas-style"></canvas>
                    </div>
                </div>
                <div v-else class="no-camera omc-point" @click="openCamera">
                    <div class="text-center">
                        <i class="bi bi-camera-fill" style="font-size: 100px;"></i>
                        <p class="omc-text large">未連結攝影機</p>
                    </div>
                </div>
            </div>
        </div>
        <!-- 下方區塊 -->
        <div class="end-area row m-0">
            <div class="col-12 col-sm-9 mb-2 mb-sm-0 d-flex align-items-center">
                <p class="omc-text white xlarge" style="min-width:5rem">編號：</p>
                <InputText class="w-100" id="resourceId" v-model="resourceId" @keyup.enter="triggerAction('getResourceData')" />
            </div>
            <div class="col-12 col-sm-3 d-flex">
                <button class="omc-btn nomal omc-text xlarge me-2" style="min-width:5rem" @click="triggerAction('getResourceData')">確 認</button>
                <button class="omc-btn nomal omc-text" style="width: fit-content; min-width:3rem">
                    <img :src="mobbytw_qrcode"/>
                </button>
            </div>
        </div>
    </div>
</template>

<script>
import { HandLandmarker, FilesetResolver } from "@mediapipe/tasks-vision";

export default {
    data() {
        return {
            tabViewOpen: true,
            resourceId: null,
            resourceData: null,
            markResources: [],
            currentFingerTrigerStatus: {
                startTime: null,
                elapsedTime: 0,
                newAreaIndex: null,
                inAreaIndex: null,
                message: null,
                triger: null,
                speak: false
            },
            // camera
            videoStream: null, // 存儲相機串流

            // hand
            handLandmarker: null,
            fingerX: 0,
            fingerY: 0,
        }
    },
    created() {
        this.pageInit();
    },
    methods: {
        async pageInit() {
            this.openCamera();
            await this.initHandDetection();
        },
        goToPage(pageName) {
            this.stopCamera()
            this.$router.push({ name: pageName })
        },
        triggerAction(status, item) {
            if (status == 'getResourceData') {
                if(this.resourceId == '') return this.sweetAlert('請輸入教材編號', 'error')
                this.getResourceData()
            } else if (status == 'tabViewOpen') {
                if (this.resourceData)  {
                    if (item) {
                        this.tabViewOpen = item
                        this.drawCanvas()
                    } else {
                        this.tabViewOpen = item
                        this.drawCanvas()
                    }
                }
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
        async getResourceData() {
            const data = {
                id: this.resourceId
            }
            try {
                const response = await this.$axios.post("/getInteractiveResource", data);
                this.resourceData = {
                    picture: `data:image/png;base64,${response.data.result.head.picture}`,
                    setting_list: []
                }
                response.data.result.detail.forEach(item => {
                    this.resourceData.setting_list.push({
                        id: item.id,
                        color: item.lable_data.color,
                        triger: item.lable_data.triger,
                        message: item.lable_data.message,
                        mark: item.lable_data.mark,
                    })
                })
                // 等待 DOM 更新後再執行 drawCanvas()
                this.$nextTick(() => {
                    this.drawCanvas();
                    this.EnableHandTracking();
                });
                // this.sweetAlert('資料載入成功，請將影像對準標記', 'success');
            } catch (error) {
                this.sweetAlert('查無教材資料', 'error');
            }
        },
        drawCanvas() {
            const canvas = this.$refs.canvasRef;
            const canvas1 = this.$refs.canvasRef1;
            
            const video = this.$refs.videoElement;

            if (!canvas1 || !canvas || !video) return;
            if (!this.resourceData || !this.resourceData.picture) {
                console.warn("resourceData.picture 不存在，無法繪製 Canvas");
                return;
            }

            const ctx = canvas.getContext("2d");
            const ctx1 = canvas1.getContext("2d");
            const img = new Image();

            img.onload = () => {
                // 取得 video 顯示的實際大小
                const videoWidth = video.clientWidth;
                const videoHeight = video.clientHeight;
                
                // 計算圖片縮放比例
                const widthRatio = videoWidth / img.width;
                const heightRatio = videoHeight / img.height;
                const scaleRatio = Math.min(widthRatio, heightRatio); // 確保不超過 video

                // 設定 Canvas 大小（同比縮放）
                canvas.width = img.width * scaleRatio;
                canvas.height = img.height * scaleRatio;
                canvas1.width = img.width * scaleRatio;
                canvas1.height = img.height * scaleRatio;

                // 取得 video 在畫面上的位置與大小
                const videoRect = video.getBoundingClientRect(); 
                canvas.style.top = `${((videoHeight / 2) - (canvas.height / 2)) + videoRect.top}px`;
                canvas.style.left = `${((videoWidth / 2) - (canvas.width / 2)) + videoRect.left}px`;
                canvas1.style.top = `${((videoHeight / 2) - (canvas.height / 2)) + videoRect.top}px`;
                canvas1.style.left = `${((videoWidth / 2) - (canvas.width / 2)) + videoRect.left}px`;

                // 清空畫布
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.clearRect(0, 0, canvas1.width, canvas1.height);
                                ctx.clearRect(0, 0, canvas1.width, canvas1.height);

                // 繪製圖片（同比縮放）
                ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

                
                // 繪製標記區塊
                this.markResources = []
                this.resourceData.setting_list.forEach((setting) => {
                    const { x, y, width, height, originalPictureWidth, originalPictureHeight } = setting.mark;
                    const color = setting.color;

                    // 防止 `originalPictureWidth` 和 `originalPictureHeight` 為 `undefined`
                    const imageWidth = originalPictureWidth || img.width;
                    const imageHeight = originalPictureHeight || img.height;

                    // 計算標記的縮放比例
                    const scaleX = canvas.width / imageWidth;
                    const scaleY = canvas.height / imageHeight;

                    // 縮放標記座標
                    const scaledX = x * scaleX;
                    const scaledY = y * scaleY;
                    const scaledWidth = width * scaleX;
                    const scaledHeight = height * scaleY;

                    // 設定標記樣式
                    ctx1.strokeStyle = color;
                    ctx1.lineWidth = 5;
                    ctx1.strokeRect(scaledX, scaledY, scaledWidth, scaledHeight);
        
                    // 紀錄標記資訊
                    this.markResources.push({
                            id: setting.id,
                            message: setting.message,
                            triger: setting.triger.code,
                            mark: {
                                left: scaledX,
                                right: scaledX + scaledWidth,
                                top: scaledY,
                                bottom: scaledY + scaledHeight,
                            }
                        }
                    )
                });
            };
            // 設定圖片來源
            img.src = this.resourceData.picture;
        },
        async initHandDetection() {
            try {
                const vision = await FilesetResolver.forVisionTasks(
                "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.0/wasm"
                );

                console.log("✅ WASM 加載成功！");

                this.handLandmarker = await HandLandmarker.createFromOptions(vision, {
                baseOptions: {
                    modelAssetPath: "/models/hand_landmarker.task",
                },
                runningMode: "IMAGE", // 先設 IMAGE，後面再改成 VIDEO
                numHands: 1,
                });

                console.log("✅ MediaPipe Hands 模型載入成功！");
            } catch (error) {
                console.error("❌ MediaPipe 初始化失敗:", error);
            }
        },
        async EnableHandTracking() {
            await this.handLandmarker.setOptions({ runningMode: "VIDEO" });
            this.detectHand();
        },
        async detectHand() {
            const video = this.$refs.videoElement;
            if (!this.handLandmarker || !video) return;

            try {
                const results = await this.handLandmarker.detectForVideo(
                    video, performance.now()
                );

                if (results.landmarks.length > 0) {
                const indexFingerTip = results.landmarks[0][8]; // 食指指尖
                this.fingerX = indexFingerTip.x * video.clientWidth;
                this.fingerY = indexFingerTip.y * video.clientHeight;
    
                this.fingerTrigger()
                this.drawFinger();
                }
            } catch (error) {
                console.error("❌ 手勢偵測錯誤:", error);
            }

            requestAnimationFrame(this.detectHand);
        },
        drawFinger() {
            const canvas = this.$refs.fingerCanvas;
            const video = this.$refs.videoElement;
            const ctx = canvas.getContext("2d");
 
            const videoRect = video.getBoundingClientRect(); 
            canvas.style.top = `${videoRect.top}px`;
            canvas.style.left = `${videoRect.left}px`;

            canvas.width = video.clientWidth;
            canvas.height = video.clientHeight;
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            ctx.beginPath();
            ctx.arc(this.fingerX, this.fingerY, 2, 0, 2 * Math.PI);
            ctx.fillStyle = "red";
            ctx.fill();
        },
        fingerTrigger() {
            this.currentFingerTrigerStatus.newAreaIndex = null
            this.markResources.some(rect => {
                    if (this.fingerX >= rect.mark.left && this.fingerX <= rect.mark.right &&
                    this.fingerY >= rect.mark.top && this.fingerY <= rect.mark.bottom) {
                        this.currentFingerTrigerStatus.newAreaIndex = rect.id
                        this.currentFingerTrigerStatus.message = rect.message
                        this.currentFingerTrigerStatus.triger = rect.triger
                        return
                    } 
                }
            )
            if (this.currentFingerTrigerStatus.newAreaIndex !== null) {
                if (this.currentFingerTrigerStatus.inAreaIndex !== this.currentFingerTrigerStatus.newAreaIndex) {
                    this.currentFingerTrigerStatus.startTime = Date.now();
                    this.currentFingerTrigerStatus.inAreaIndex = this.currentFingerTrigerStatus.newAreaIndex
                    this.currentFingerTrigerStatus.speak = false
                    // console.log(`進入區域 ${this.currentFingerTrigerStatus.inAreaIndex}`);
                } else {
                    // 持續計算停留秒數
                    this.currentFingerTrigerStatus.elapsedTime = (Date.now() - this.currentFingerTrigerStatus.startTime) / 1000
                    // console.log(`在區域 ${this.currentFingerTrigerStatus.inAreaIndex} 停留 ${this.currentFingerTrigerStatus.elapsedTime.toFixed(2)} 秒`);
                    this.speak()
                }
            } else {
                // 離開區域，重新計時
                if (this.currentFingerTrigerStatus.inAreaIndex !== null) {
                    // console.log(`離開區域 ${this.currentFingerTrigerStatus.inAreaIndex + 1}，總共停留 ${this.currentFingerTrigerStatus.elapsedTime.toFixed(2)} 秒`);
                    this.currentFingerTrigerStatus.startTime = null
                    this.currentFingerTrigerStatus.elapsedTime = 0
                    this.currentFingerTrigerStatus.inAreaIndex = null
                    this.currentFingerTrigerStatus.message = null
                    this.currentFingerTrigerStatus.triger = null
                    this.currentFingerTrigerStatus.speak = false
                }
            }  
            
        },
        speak() {
            if (this.currentFingerTrigerStatus.elapsedTime >= 0 && !this.currentFingerTrigerStatus.speak) {
                if ((this.currentFingerTrigerStatus.triger === 'hover' && this.currentFingerTrigerStatus.elapsedTime > 1) || this.currentFingerTrigerStatus.triger == 'course') {
                    speechSynthesis.cancel();
                    
                    let voices = speechSynthesis.getVoices();
                    const utterance = new SpeechSynthesisUtterance(this.currentFingerTrigerStatus.message);
                    const voice = voices.find(v => v.name === 'Microsoft Yating - Chinese (Traditional, Taiwan)');
                
                    if (voice) {
                        utterance.voice = voice; // 設定語音
                    }

                    utterance.lang = "zh-TW"; // 設定語言 (可省略，因為語音庫本身有語言)
                    utterance.rate = 1; // 設定語速
                    speechSynthesis.speak(utterance);
                    this.currentFingerTrigerStatus.speak = true
                }
            }
        }
    }
}
</script>

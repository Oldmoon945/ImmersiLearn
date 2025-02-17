<template>
    <div class="nomal-background">
        <!-- 上方按鈕區塊 -->
        <div class="d-flex justify-content-between p-2">
            <!-- 左 -->
            <div class="d-flex">
                <div class="m-1">
                    <button class="omc-btn nomal p-2" @click="triggerAction('create')">
                        <i class="bi bi-plus-circle-fill"></i>
                         新增
                    </button>
                </div>
                <div class="m-1">
                    <button class="omc-btn nomal p-2" @click="triggerAction('edit')">
                        <i class="bi bi-pencil-square"></i>
                        編輯
                    </button>
                </div>
                <div class="m-1">
                    <button class="omc-btn nomal p-2" @click="triggerAction('delete')">
                        <i class="bi bi-trash-fill"></i>
                        刪除
                    </button>
                </div>
                <div class="m-1">
                    <button class="omc-btn nomal p-2" @click="showPrintOptions = !showPrintOptions">
                        <i class="bi bi-printer-fill"></i>
                        教材列印分享
                        <i class="bi bi-chevron-down"></i>
                    </button>
                     <div v-if="showPrintOptions" class="omc-dropdown-menu">
                        <ul>
                            <li v-for="option in printOptions" :key="option.code" @click="triggerAction(option.code)">
                                {{ option.name }}
                            </li>
                        </ul>
                    </div>
                </div>
            </div>
            <!-- 右 -->
            <div>
                <i class="bi bi-x-lg omc-point omc-text xlarge nomal bold me-2" @click="goToPage('Home')"></i>
            </div>
        </div>
        <!-- 下方區塊 -->
        <div class="mx-2">
            <DataTable 
                v-model:filters="filters"
                v-model:selection="selectedItem"
                :value="tableData"
                paginator 
                :rows="10"
                :rowsPerPageOptions="[5, 10, 20, 50]"
                dataKey="id" 
                filterDisplay="row" 
                :loading="loading"
                :globalFilterFields="['id', 'description', 'picture', 'create_at']"
                sortField="create_at" 
                :sortOrder="-1"
                tableStyle="min-height: 80vh"
                scrollable scrollHeight="80vh"
            >
                <template #empty>查無資料</template>
                <template #loading>資料載入中</template>
                <Column selectionMode="multiple" style="width:1rem"></Column>
                <Column field="id" header="編號" :showFilterMenu="false" sortable style="width:6rem">
                    <template #body="{ data }">
                        {{ data.id }}
                    </template>
                    <template #filter="{filterModel, filterCallback }">
                        <InputText v-model="filterModel.value" type="text" @input="filterCallback()" placeholder="" style="width:4rem" />
                    </template>
                </Column>
                <Column field="description" header="說明" :showFilterMenu="false" sortable>
                    <template #body="{ data }">
                        {{ data.description }}
                    </template>
                    <template #filter="{filterModel, filterCallback }">
                        <InputText class="w-100" v-model="filterModel.value" type="text" @input="filterCallback()" placeholder="" />
                    </template>
                </Column>
                <Column field="picture_small" header="縮圖" :showFilterMenu="false" sortable style="width:5rem">
                    <template #body="{ data }">
                        <img :src="data.picture_small" class="w-24 rounded" />
                    </template>
                </Column>
                <Column field="create_at" header="建立日期" :showFilterMenu="false" sortable style="width:12rem">
                    <template #body="{ data }">
                        {{ data.create_at }}
                    </template>
                    <template #filter="{filterModel, filterCallback }">
                        <InputText class="w-100" v-model="filterModel.value" type="text" @input="filterCallback()" placeholder="" />
                    </template>
                </Column>
            </DataTable>
        </div>
    </div>
    <!-- 刪除 Dialog -->
    <Dialog v-model:visible="dialog_delete_show" modal header="刪除" :style="{ width:'50vw'}">
        <div>
            <p class="mb-2">確定刪除以下資料?</p>
            <div>
                <DataTable :value="selectedItem" dataKey="id">
                    <Column field="id" header="編號" style="width:3rem"/>
                    <Column field="description" header="說明" style="width:15rem"/>
                    <Column field="picture_small" header="縮圖" style="width:5rem">
                        <template #body="{ data }">
                            <img :src="data.picture_small" class="w-24 rounded" />
                        </template>
                    </Column>
                </DataTable>
            </div>
        </div>
        <template #footer>
            <div class="d-flex">
                <button class="omc-btn nomal px-3 me-2" @click="triggerAction('confirmDelete')">確定</button>
                <button class="omc-btn nomal px-3" @click="dialog_delete_show = false">關閉</button>
            </div>
        </template>
    </Dialog>
    <!-- 列印 QRCode Dialog -->
    <Dialog v-model:visible="dialog_printQRcode_show" modal header="列印 QRCode" :style="{ width:'50vw'}">
        <div>
            <div class="mb-2">
                <span>
                    <span style="min-width:4rem">尺寸：</span>
                    <Select v-model="selectedQRCodeSize" editable :options="printQRCodeSizeOptions" optionLabel="name" placeholder="選擇尺寸" class="w-full md:w-56">
                        <p>{{selectedQRCodeSize.name}}</p>
                    </Select>
                </span>
            </div>
            <p class="mb-2">確定要列印以下資料</p>
            <div>
                <DataTable :value="selectedItem" dataKey="id">
                    <Column field="id" header="編號" style="width:3rem"/>
                    <Column field="description" header="說明" style="width:15rem"/>
                    <Column field="picture_small" header="縮圖" style="width:5rem">
                        <template #body="{ data }">
                            <img :src="data.picture_small" class="w-24 rounded" />
                        </template>
                    </Column>
                </DataTable>
            </div>
        </div>
        <template #footer>
            <div class="d-flex">
                <button class="omc-btn nomal px-3 me-2" @click="triggerAction('confirmPrintQRCode')">確定</button>
                <button class="omc-btn nomal px-3" @click="dialog_printQRcode_show = false">關閉</button>
            </div>
        </template>
    </Dialog>
    <!-- 教材分享列印 Dialog -->
    <Dialog v-model:visible="dialog_printShare_show" modal header="教材分享列印" :style="{ width:'50vw'}">
        <div>
            <div v-if="!printShareSecondPage_show">
                <p class="mb-2">請問以下是您要分享的教材嗎</p>
                <div>
                    <DataTable :value="selectedItem" dataKey="id">
                        <Column field="id" header="編號" style="width:3rem"/>
                        <Column field="description" header="說明" style="width:15rem"/>
                        <Column field="picture_small" header="縮圖" style="width:5rem">
                            <template #body="{ data }">
                                <img :src="data.picture_small" class="w-24 rounded" />
                            </template>
                        </Column>
                    </DataTable>
                </div>
            </div>
            <div v-else>
                <p>選擇欲分享的對象，並點擊確認分享。</p>
            </div>
        </div>
        <template #footer>
            <div v-if="!printShareSecondPage_show" class="d-flex">
                <button class="omc-btn nomal px-3 me-2" @click="printShareSecondPage_show = true">確定</button>
                <button class="omc-btn nomal px-3" @click="dialog_printShare_show = false">關閉</button>
            </div>
            <div v-else class="d-flex">
                <button class="omc-btn nomal px-3 me-2" @click="triggerAction('confirmPrintShare')">確定</button>
                <button class="omc-btn nomal px-3" @click="dialog_printShare_show = false">關閉</button>
            </div>
        </template>
    </Dialog>
</template>

<script>
import { FilterMatchMode } from '@primevue/core/api';
export default {
    data() {
        return {
            showPrintOptions: false,
            printOptions : [
                { name: "QR CODE 列印", code: "printQRCode" },
                { name: "教材分享列印", code: "printShare" },
            ],
            selectedQRCodeSize: null,
            printQRCodeSizeOptions: [
                { name: "大", code: "size1" },
                { name: "中", code: "size2" },
                { name: "小", code: "size3" },
            ],
            printShareSecondPage_show: false,
            // Dialog
            dialog_delete_show: false,
            dialog_printQRcode_show: false,
            dialog_printShare_show: false,

            // table
            tableData: null,
            loading: true,
            filters: {
                id: { value: null, matchMode: FilterMatchMode.CONTAINS },
                description: { value: null, matchMode: FilterMatchMode.CONTAINS },
                create_at: { value: null, matchMode: FilterMatchMode.CONTAINS }
            },
            selectedItem: []
        }
    },
    created() {
        this.pageInit()
    },
    methods: {
        pageInit() {
            this.getInteractiveResourceslist();
        },
        goToPage(pageName, query) {
            this.$router.push({ name: pageName, query: query })
        },
        triggerAction(status) {
            if (status === 'create') {
                this.goToPage('AddEditResource');
            } else if (status === 'edit') {
                if (this.selectedItem.length !== 1 ) return this.sweetAlert('請選擇一筆教材', 'error') 
                this.goToPage('AddEditResource', { ID: this.selectedItem[0].id })
            } else if (status === 'delete') {
                if (this.selectedItem.length === 0) return this.sweetAlert('請選擇欲刪除的教材', 'error')
                this.dialog_delete_show = true
            } else if (status === 'confirmDelete') {
                const data = {
                    ids: []
                }
                this.selectedItem.forEach(item => {
                    data.ids.push(item.id)
                });
                this.$axios.delete("/deleteInteractiveResource", {data})
                .then(response => {
                    console.log(response.data);
                    this.sweetAlert('成功', 'success')
                    this.selectedItem = []
                    this.dialog_delete_show = false
                    this.getInteractiveResourceslist();
                })
                .catch(error => {
                    console.error(error);
                    this.sweetAlert('失敗', 'error')
                });
            } else if (status === 'printQRCode') {
                if (this.selectedItem.length === 0) return this.sweetAlert('請選擇欲列印的教材', 'error')
                this.showPrintOptions = false
                this.selectedQRCodeSize = this.printQRCodeSizeOptions[0]
                this.dialog_printQRcode_show = true
            } else if (status === 'confirmPrintQRCode') {

            } else if (status === 'printShare') {
                if (this.selectedItem.length === 0) return this.sweetAlert('請選擇欲分享列印的教材', 'error')
                this.showPrintOptions = false
                this.printShareSecondPage_show = false
                this.dialog_printShare_show = true
                
            } else {
                console.warn("未知的動作:", status);
            }
        },
        async getInteractiveResourceslist() {
            try {
                const response = await this.$axios.get("/getInteractiveResourceslist");             
                this.tableData = response.data.result.map((item) => { 
                        return { 
                            ...item , 
                            create_at: this.$dayjs(item.create_at).format('YYYY-MM-DD HH:mm'),
                            picture_small: item.picture_small ? `data:image/png;base64,${item.picture_small}` : null
                        }
                    }
                )
                this.loading = false;
            } catch (error) {
                console.error("error:", error);
            }
        },
    }
}
</script>

import { createApp } from 'vue'
import App from './App.vue'
import router from './router' 

import '@/assets/design/font/_font.scss'

/** 引入外部套件 */
import dayjs from "dayjs";
// PrimeVue
import PrimeVue from 'primevue/config' 
import Lara from '@primevue/themes/lara'
import FloatLabel from 'primevue/floatlabel';
import InputText from 'primevue/inputtext';
import Password from 'primevue/password';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Select from 'primevue/select';
import Textarea from 'primevue/textarea';
import Dialog from 'primevue/dialog';
import Toast from 'primevue/toast';
import Dropdown from 'primevue/dropdown';


// Bootstrap
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';
import 'bootstrap-icons/font/bootstrap-icons.min.css'
// SweetAlert
import Swal from 'sweetalert2'


/** 引入內部套件 */
import { Design } from "@/utils/global/design.js";
import { sweetAlert } from "@/utils/global/sweetAlert.js"
import api from "@/utils/global/api.js";
import '@/assets/scss/all.scss'

const app = createApp(App)
/** component */
app.component('FloatLabel', FloatLabel );
app.component('InputText', InputText );
app.component('Password', Password );
app.component('DataTable', DataTable );
app.component('Column', Column );
app.component('Select', Select );
app.component('Textarea', Textarea );
app.component('Dialog', Dialog );
app.component('Toast', Toast );
app.component('Dropdown', Dropdown );

/** mixin */
app.mixin(Design);
app.mixin(sweetAlert);

app.config.globalProperties.$axios = api;
app.config.globalProperties.$dayjs = dayjs;

app.use(router)
app.use(PrimeVue, {theme:{ preset: Lara }})

app.mount('#app')

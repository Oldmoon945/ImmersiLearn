<script setup>
import { ref } from 'vue'

defineProps({
  msg: String,
})

const count = ref(0)
</script>

<template>
  <div>
    <h1>用戶列表</h1>
    <ul>
      <li v-for="user in users" :key="user.id">{{ user.name }}</li>
    </ul>
    <input v-model="newUser" placeholder="新增用戶" />
    <button @click="addUser">新增</button>
  </div>
</template>

<script>
import { ref, onMounted } from "vue";
import axios from "axios";

export default {
  data() {
    return {
      users:''
    }
  },
  mounted() {
    this.getUser()
  },
  methods: {
    addUser() {
      alert('測試')
    },
    getUser() {
      axios.get("http://127.0.0.1:5000/api/users")
      .then(res => {
        console.log(res.data);  // 檢查回應數據
        this.users = res.data;
      })
      .catch(error => {
        console.error("Error fetching users:", error);
      });
    }
  }
};
</script>

<style scoped>
.read-the-docs {
  color: #888;
}
</style>

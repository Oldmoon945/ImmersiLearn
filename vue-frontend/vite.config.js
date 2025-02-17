import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// 修改路徑
import path from "path"

// 全局引入插件
import inject from '@rollup/plugin-inject'

export default defineConfig((config) => {
  const plugins = [vue()]

    // 全局引入插件
    plugins.push(inject({
      $: "jquery",  // 这里会自动载入 node_modules 中的 jquery
      jQuery: "jquery",
      "windows.jQuery": "jquery"
    }))

  return {
    base: "./",
    plugins: plugins,
    // 讓專案中，引入檔案可以用符號指向
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "./src"),
        "~": path.resolve(__dirname, "./node_modules"),
      },
      // extensions: ['.mjs', '.js', '.ts', '.jsx', '.tsx', '.json', '.vue'],
    },
  }
})
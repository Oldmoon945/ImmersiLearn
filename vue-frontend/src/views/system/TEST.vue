<template>
  <div>
    <textarea v-model="text" placeholder="輸入要說的文字"></textarea>
    
    <select v-model="selectedVoice">
      <option v-for="voice in voices" :key="voice.name" :value="voice.name">
        {{ voice.name }} ({{ voice.lang }})
      </option>
    </select>
    {{selectedVoice}}
    <button @click="speak">說話</button>
  </div>
</template>

<script>
export default {
  data() {
    return {
      text: "你好，這是 Vue 語音合成示範！",
      voices: [],
    };
  },

  methods: {
    speak() {
      this.voices = speechSynthesis.getVoices();
      if (!this.text.trim()) return;
      const utterance = new SpeechSynthesisUtterance(this.text);
      const voice = this.voices.find(v => v.name === 'Microsoft Yating - Chinese (Traditional, Taiwan)');
      
      if (voice) {
        utterance.voice = voice; // 設定語音
      }

      utterance.lang = "zh-TW"; // 設定語言 (可省略，因為語音庫本身有語言)
      utterance.rate = 2; // 設定語速
      speechSynthesis.speak(utterance);
    }
  }
};
</script>

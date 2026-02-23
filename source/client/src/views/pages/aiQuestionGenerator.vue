<template>
  <div style="padding: 20px">
    <AIQuestionGenerator />
  </div>
</template>

<script>
import AIQuestionGenerator from '../../components/AIQuestionGenerator.vue'

export default {
  name: 'aiQuestionGeneratorPage',
  components: { AIQuestionGenerator }
}
</script>

<style scoped>
div {
  background: linear-gradient(135deg, #f0f9ff 0%, #fff 100%);
  min-height: 100vh;
  animation: fadeInUp 0.6s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>



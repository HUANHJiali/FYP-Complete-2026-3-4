<template>
  <div class="theme-switcher">
    <Dropdown trigger="click" @on-click="handleThemeChange">
      <Button type="text" class="theme-btn">
        <Icon :type="currentTheme === 'dark' ? 'md-moon' : 'md-sunny'" size="20" />
        <span class="theme-text">{{ currentTheme === 'dark' ? '深色' : '浅色' }}</span>
      </Button>
      <template #list>
        <DropdownMenu>
          <DropdownItem name="light" :selected="currentTheme === 'light'">
            <Icon type="md-sunny" /> 浅色模式
          </DropdownItem>
          <DropdownItem name="dark" :selected="currentTheme === 'dark'">
            <Icon type="md-moon" /> 深色模式
          </DropdownItem>
          <DropdownItem divided name="settings">
            <Icon type="md-settings" /> 主题设置
          </DropdownItem>
        </DropdownMenu>
      </template>
    </Dropdown>

    <!-- 主题设置模态框 -->
    <Modal
      v-model="showSettings"
      title="主题设置"
      width="500"
      @on-ok="saveThemeSettings"
      @on-cancel="showSettings = false"
    >
      <Form :model="themeSettings" label-position="left" :label-width="100">
        <FormItem label="主题模式">
          <RadioGroup v-model="themeSettings.theme">
            <Radio label="light">
              <Icon type="md-sunny" /> 浅色
            </Radio>
            <Radio label="dark">
              <Icon type="md-moon" /> 深色
            </Radio>
          </RadioGroup>
        </FormItem>

        <FormItem label="主题色">
          <div class="color-picker">
            <div
              v-for="color in colorOptions"
              :key="color"
              class="color-item"
              :class="{ active: themeSettings.primaryColor === color }"
              :style="{ backgroundColor: color }"
              @click="themeSettings.primaryColor = color"
            />
          </div>
        </FormItem>

        <FormItem label="字体大小">
          <RadioGroup v-model="themeSettings.fontSize">
            <Radio label="small">小</Radio>
            <Radio label="medium">中</Radio>
            <Radio label="large">大</Radio>
          </RadioGroup>
        </FormItem>

        <FormItem label="侧边栏折叠">
          <i-switch v-model="themeSettings.sidebarCollapsed" />
        </FormItem>

        <FormItem label="显示动画">
          <i-switch v-model="themeSettings.showAnimations" />
        </FormItem>

        <FormItem label="紧凑模式">
          <i-switch v-model="themeSettings.compactMode" />
        </FormItem>
      </Form>

      <div slot="footer">
        <Button @click="resetThemeSettings">重置</Button>
        <Button type="primary" @click="saveThemeSettings">保存</Button>
      </div>
    </Modal>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'

export default {
  name: 'ThemeSwitcher',
  data() {
    return {
      showSettings: false,
      colorOptions: [
        '#2d8cf0', '#19be6b', '#ff9900', '#ed4014',
        '#9b59b6', '#1abc9c', '#3498db', '#e74c3c'
      ],
      themeSettings: {
        theme: 'light',
        primaryColor: '#2d8cf0',
        fontSize: 'medium',
        sidebarCollapsed: false,
        showAnimations: true,
        compactMode: false
      }
    }
  },
  computed: {
    ...mapState('theme', ['currentTheme', 'primaryColor'])
  },
  mounted() {
    this.loadThemeSettings()
  },
  methods: {
    ...mapActions('theme', ['setTheme', 'loadTheme', 'saveTheme', 'resetTheme']),

    handleThemeChange(name) {
      if (name === 'settings') {
        this.showSettings = true
      } else {
        this.setTheme(name)
        this.applyTheme(name)
      }
    },

    async loadThemeSettings() {
      try {
        const userId = localStorage.getItem('userId')
        if (!userId) return

        const resp = await fetch(`/api/theme/get/?userId=${userId}`)
        const data = await resp.json()

        if (data.code === 0) {
          this.themeSettings = { ...data.data }
          this.setTheme(data.data.theme)
          this.applyTheme(data.data.theme)
        }
      } catch (e) {
        console.error('加载主题设置失败', e)
      }
    },

    async saveThemeSettings() {
      try {
        const userId = localStorage.getItem('userId')
        const formData = new FormData()
        formData.append('userId', userId)
        Object.keys(this.themeSettings).forEach(key => {
          formData.append(key, this.themeSettings[key])
        })

        const resp = await fetch('/api/theme/save/', {
          method: 'POST',
          body: formData
        })
        const data = await resp.json()

        if (data.code === 0) {
          this.setTheme(this.themeSettings.theme)
          this.applyTheme(this.themeSettings.theme)
          this.$Message.success('主题设置已保存')
          this.showSettings = false
        } else {
          this.$Message.error(data.msg || '保存失败')
        }
      } catch (e) {
        console.error('保存主题设置失败', e)
        this.$Message.error('保存失败')
      }
    },

    async resetThemeSettings() {
      try {
        const userId = localStorage.getItem('userId')
        const formData = new FormData()
        formData.append('userId', userId)

        const resp = await fetch('/api/theme/reset/', {
          method: 'POST',
          body: formData
        })
        const data = await resp.json()

        if (data.code === 0) {
          this.themeSettings = {
            theme: 'light',
            primaryColor: '#2d8cf0',
            fontSize: 'medium',
            sidebarCollapsed: false,
            showAnimations: true,
            compactMode: false
          }
          this.setTheme('light')
          this.applyTheme('light')
          this.$Message.success('主题设置已重置')
        }
      } catch (e) {
        console.error('重置主题设置失败', e)
        this.$Message.error('重置失败')
      }
    },

    applyTheme(theme) {
      // 应用主题到body
      document.body.setAttribute('data-theme', theme)

      // 更新CSS变量
      if (theme === 'dark') {
        document.documentElement.style.setProperty('--bg-color', '#1a1a2e')
        document.documentElement.style.setProperty('--text-color', '#e2e8f0')
        document.documentElement.style.setProperty('--card-bg', '#16213e')
        document.documentElement.style.setProperty('--border-color', '#2d3748')
      } else {
        document.documentElement.style.setProperty('--bg-color', '#f5f7f9')
        document.documentElement.style.setProperty('--text-color', '#515a6e')
        document.documentElement.style.setProperty('--card-bg', '#ffffff')
        document.documentElement.style.setProperty('--border-color', '#e8eaec')
      }
    }
  }
}
</script>

<style scoped>
.theme-switcher {
  display: inline-block;
}

.theme-btn {
  color: inherit;
  display: flex;
  align-items: center;
  gap: 5px;
}

.theme-text {
  font-size: 14px;
}

.color-picker {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.color-item {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.3s ease;
}

.color-item:hover {
  transform: scale(1.1);
}

.color-item.active {
  border-color: #2d8cf0;
  box-shadow: 0 0 0 2px rgba(45, 140, 240, 0.3);
}
</style>

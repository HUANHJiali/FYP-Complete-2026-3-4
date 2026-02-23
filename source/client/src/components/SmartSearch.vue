<template>
    <div class="smart-search">
        <div class="search-input-container">
            <div class="search-input-wrapper">
                <Icon type="ios-search" class="search-icon" />
                <input 
                    v-model="searchQuery"
                    @input="handleSearch"
                    @focus="showSuggestions = true"
                    @blur="handleBlur"
                    type="text"
                    class="search-input"
                    :placeholder="placeholder"
                />
                <button 
                    v-if="searchQuery"
                    @click="clearSearch"
                    class="clear-btn"
                >
                    <Icon type="ios-close" />
                </button>
            </div>
            
            <div class="search-filters">
                <Select 
                    v-model="selectedFilter" 
                    class="filter-select"
                    placeholder="筛选类型"
                >
                    <Option value="all">全部</Option>
                    <Option value="students">学生</Option>
                    <Option value="exams">考试</Option>
                    <Option value="teachers">教师</Option>
                </Select>
            </div>
        </div>
        
        <transition name="suggestions">
            <div v-if="showSuggestions && suggestions.length > 0" class="suggestions-dropdown">
                <div 
                    v-for="suggestion in suggestions" 
                    :key="suggestion.id"
                    @click="selectSuggestion(suggestion)"
                    class="suggestion-item"
                >
                    <div class="suggestion-icon">
                        <Icon :type="suggestion.icon" />
                    </div>
                    <div class="suggestion-content">
                        <div class="suggestion-title">{{ suggestion.title }}</div>
                        <div class="suggestion-subtitle">{{ suggestion.subtitle }}</div>
                    </div>
                    <div class="suggestion-type">{{ suggestion.type }}</div>
                </div>
            </div>
        </transition>
        
        <div v-if="recentSearches.length > 0 && !searchQuery" class="recent-searches">
            <div class="recent-header">
                <span>最近搜索</span>
                <button @click="clearRecent" class="clear-recent">清空</button>
            </div>
            <div class="recent-list">
                <div 
                    v-for="recent in recentSearches" 
                    :key="recent"
                    @click="selectRecent(recent)"
                    class="recent-item"
                >
                    <Icon type="ios-time" />
                    <span>{{ recent }}</span>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'SmartSearch',
    props: {
        placeholder: {
            type: String,
            default: '搜索...'
        }
    },
    data() {
        return {
            searchQuery: '',
            selectedFilter: 'all',
            showSuggestions: false,
            suggestions: [],
            recentSearches: []
        }
    },
    mounted() {
        this.loadRecentSearches()
    },
    methods: {
        handleSearch() {
            if (this.searchQuery.length < 2) {
                this.suggestions = []
                return
            }
            
            // 模拟搜索建议
            this.suggestions = [
                {
                    id: 1,
                    title: '张三',
                    subtitle: '计算机科学 - 2021级',
                    type: '学生',
                    icon: 'ios-person'
                },
                {
                    id: 2,
                    title: '数学期末考试',
                    subtitle: '2024年春季学期',
                    type: '考试',
                    icon: 'ios-document'
                },
                {
                    id: 3,
                    title: '李老师',
                    subtitle: '数学系',
                    type: '教师',
                    icon: 'ios-person'
                }
            ].filter(item => 
                item.title.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
                item.subtitle.toLowerCase().includes(this.searchQuery.toLowerCase())
            )
        },
        
        selectSuggestion(suggestion) {
            this.searchQuery = suggestion.title
            this.showSuggestions = false
            this.addToRecent(suggestion.title)
            this.$emit('select', suggestion)
        },
        
        selectRecent(recent) {
            this.searchQuery = recent
            this.$emit('search', recent)
        },
        
        clearSearch() {
            this.searchQuery = ''
            this.suggestions = []
            this.$emit('clear')
        },
        
        handleBlur() {
            setTimeout(() => {
                this.showSuggestions = false
            }, 200)
        },
        
        addToRecent(search) {
            if (!this.recentSearches.includes(search)) {
                this.recentSearches.unshift(search)
                if (this.recentSearches.length > 5) {
                    this.recentSearches.pop()
                }
                this.saveRecentSearches()
            }
        },
        
        clearRecent() {
            this.recentSearches = []
            this.saveRecentSearches()
        },
        
        saveRecentSearches() {
            localStorage.setItem('recentSearches', JSON.stringify(this.recentSearches))
        },
        
        loadRecentSearches() {
            const saved = localStorage.getItem('recentSearches')
            if (saved) {
                this.recentSearches = JSON.parse(saved)
            }
        }
    }
}
</script>

<style scoped>
.smart-search {
    position: relative;
    width: 100%;
    max-width: 600px;
}

.search-input-container {
    display: flex;
    gap: 10px;
    align-items: center;
}

.search-input-wrapper {
    position: relative;
    flex: 1;
}

.search-icon {
    position: absolute;
    left: 15px;
    top: 50%;
    transform: translateY(-50%);
    color: #999;
    font-size: 16px;
    z-index: 2;
}

.search-input {
    width: 100%;
    height: 45px;
    padding: 0 45px 0 45px;
    border: 2px solid #e8eaec;
    border-radius: 25px;
    font-size: 14px;
    transition: all 0.3s ease;
    background: #fff;
}

.search-input:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.clear-btn {
    position: absolute;
    right: 15px;
    top: 50%;
    transform: translateY(-50%);
    background: none;
    border: none;
    color: #999;
    cursor: pointer;
    padding: 5px;
    border-radius: 50%;
    transition: all 0.3s ease;
}

.clear-btn:hover {
    background: #f0f0f0;
    color: #666;
}

.filter-select {
    width: 120px;
}

.suggestions-dropdown {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.15);
    margin-top: 10px;
    z-index: 1000;
    max-height: 300px;
    overflow-y: auto;
}

.suggestion-item {
    display: flex;
    align-items: center;
    gap: 15px;
    padding: 15px;
    cursor: pointer;
    transition: all 0.3s ease;
    border-bottom: 1px solid #f0f0f0;
}

.suggestion-item:last-child {
    border-bottom: none;
}

.suggestion-item:hover {
    background: #f8f9fa;
}

.suggestion-icon {
    width: 35px;
    height: 35px;
    border-radius: 8px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-size: 16px;
}

.suggestion-content {
    flex: 1;
}

.suggestion-title {
    font-size: 14px;
    font-weight: 500;
    color: #333;
    margin-bottom: 3px;
}

.suggestion-subtitle {
    font-size: 12px;
    color: #666;
}

.suggestion-type {
    font-size: 11px;
    color: #999;
    background: #f0f0f0;
    padding: 3px 8px;
    border-radius: 10px;
}

.recent-searches {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.15);
    margin-top: 10px;
    z-index: 1000;
    padding: 15px;
}

.recent-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
    font-size: 12px;
    color: #666;
}

.clear-recent {
    background: none;
    border: none;
    color: #667eea;
    cursor: pointer;
    font-size: 12px;
}

.recent-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.recent-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 12px;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s ease;
    color: #666;
    font-size: 13px;
}

.recent-item:hover {
    background: #f8f9fa;
    color: #333;
}

/* 动画效果 */
.suggestions-enter-active,
.suggestions-leave-active {
    transition: all 0.3s ease;
}

.suggestions-enter-from,
.suggestions-leave-to {
    opacity: 0;
    transform: translateY(-10px);
}

/* 响应式设计 */
@media (max-width: 768px) {
    .search-input-container {
        flex-direction: column;
        gap: 10px;
    }
    
    .filter-select {
        width: 100%;
    }
    
    .search-input {
        height: 40px;
        font-size: 13px;
    }
}
</style>

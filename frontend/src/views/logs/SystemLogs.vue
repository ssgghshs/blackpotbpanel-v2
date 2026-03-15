<template>
  <a-card class="logs-container">
    <template #title>
      <div class="card-header">
        <span class="title">{{ t('systemLogs') }}</span>
        <!-- 将自动刷新开关放在左侧 -->
        <div class="auto-refresh">
          <a-switch 
            v-model="autoRefreshEnabled" 
            @change="toggleAutoRefresh"
            :checked-text="t('autoRefreshOn')"
            :unchecked-text="t('autoRefreshOff')"
          />
        </div>
        <!-- 将文件选择表单和清理日志按钮放在右侧 -->
        <div class="header-form">
          <a-form :model="formState" layout="inline">
            <a-form-item :label="t('logDate') + ':'" class="form-item-inline">
              <a-select 
                v-model="formState.selectedFile" 
                :placeholder="t('selectLogFile')" 
                @change="loadLogContent"
                :style="{ width: isMobile ? '160px' : '200px' }"
              >
                <a-option 
                  v-for="file in logFiles" 
                  :key="file" 
                  :value="file"
                  :class="{ 'log-file-option': isAdmin }"
                >
                  <div class="log-file-option-content">
                    <span>{{ formatLogFileName(file) }}</span>
                    <div class="file-actions">
                      <icon-download 
                        class="export-icon" 
                        @click.stop="handleExportLogFile(file)"
                        :title="t('exportLogFile')"
                      />
                      <icon-delete 
                        v-if="isAdmin && !isTodayLogFile(file)" 
                        class="delete-icon" 
                        @click.stop="showDeleteLogFileModal(file)"
                        :title="t('deleteLogFile')"
                      />
                    </div>
                  </div>
                </a-option>
              </a-select>
            </a-form-item>
          </a-form>
          <!-- 导出和清理日志按钮 -->
          <div class="action-buttons">
            <!-- 导出当前日志文件按钮 -->
            <a-button 
              v-if="formState.selectedFile" 
              type="outline" 
              size="small" 
              @click="handleExportLogFile(formState.selectedFile)"
            >
              {{ t('exportLog') }}
            </a-button>
            <!-- 清理日志按钮 - 仅管理员可见 -->
            <a-button 
              v-if="isAdmin" 
              type="outline"
              status="danger" 
              size="small" 
              @click="showClearLogsModal"
            >
              {{ t('clearLogs') }}
            </a-button>
          </div>
        </div>
      </div>
    </template>

    <!-- 内容区域 -->
    <div class="content-area">
      <!-- 日志内容显示 -->
      <a-card v-if="logContent" class="log-content-card">
        <pre class="log-content" ref="logContentRef"><span v-html="formatLogContent(logContent)"></span></pre>
      </a-card>
      <a-empty v-else>
        <template #description>
          <span>{{ t('noLogContent') }}</span>
        </template>
      </a-empty>
    </div>
    
    <!-- 清理日志确认对话框 -->
    <a-modal 
      v-model:visible="clearLogsModalVisible" 
      :title="t('clearLogsConfirmTitle')" 
      @ok="handleClearLogs" 
      @cancel="cancelClearLogs"
      :ok-text="t('confirm')"
      :cancel-text="t('cancel')"
    >
      <p>{{ t('clearLogsConfirmMessage') }}</p>
    </a-modal>
    
    <!-- 删除指定日志文件确认对话框 -->
    <a-modal 
      v-model:visible="deleteLogFileModalVisible" 
      :title="t('deleteLogFileConfirmTitle')" 
      @ok="handleDeleteLogFile" 
      @cancel="cancelDeleteLogFile"
      :ok-text="t('confirm')"
      :cancel-text="t('cancel')"
    >
      <p>{{ t('deleteLogFileConfirmMessage', { filename: formatLogFileName(selectedLogFile) }) }}</p>
    </a-modal>
  </a-card>
</template>

<script setup>
import { reactive, onMounted, onUnmounted, ref, nextTick } from 'vue'
import { t } from '../../utils/locale'
import { Message, Modal } from '@arco-design/web-vue'
import { getLogFiles, getLogContent, clearLogs as clearLogsApi, clearLogFile as clearLogFileApi, exportLogFile } from '../../api/log'
import { isAdmin } from '../../stores/user'
import { IconDelete, IconDownload } from '@arco-design/web-vue/es/icon'

// 移动端检测
const isMobile = ref(window.innerWidth <= 768);

const checkIsMobile = () => {
  isMobile.value = window.innerWidth <= 768;
};

// 监听窗口大小变化
onMounted(() => {
  window.addEventListener('resize', checkIsMobile);
});

onUnmounted(() => {
  window.removeEventListener('resize', checkIsMobile);
});

const formState = reactive({
  selectedFile: ''
})

const logFiles = ref([])
const logContent = ref('')
const logContentRef = ref(null)
const autoRefreshEnabled = ref(true) // 默认开启自动刷新
const refreshInterval = ref(null)
const clearLogsModalVisible = ref(false) // 清理日志确认对话框可见性
const deleteLogFileModalVisible = ref(false) // 删除指定日志文件确认对话框可见性
const selectedLogFile = ref('') // 要删除的日志文件名
const pageVisibilityHandler = ref(null) // 页面可见性处理器

// ANSI 颜色代码映射
const ansiColorMap = {
  '30': '#000000', // 黑色
  '31': '#FF0000', // 红色
  '32': '#00FF00', // 绿色
  '33': '#FFFF00', // 黄色
  '34': '#0000FF', // 蓝色
  '35': '#FF00FF', // 紫色
  '36': '#00FFFF', // 青色
  '37': '#FFFFFF', // 白色
  '90': '#808080', // 灰色
  '91': '#FF8080', // 浅红色
  '92': '#80FF80', // 浅绿色
  '93': '#FFFF80', // 浅黄色
  '94': '#8080FF', // 浅蓝色
  '95': '#FF80FF', // 浅紫色
  '96': '#80FFFF', // 浅青色
  '97': '#FFFFFF'  // 亮白色
};

// 格式化日志内容，解析 ANSI 颜色代码
const formatLogContent = (content) => {
  if (!content) return '';
  
  // 限制日志内容长度，防止渲染过大的内容导致卡顿
  const maxLength = 50000; // 限制为50000个字符
  let processedContent = content;
  if (content.length > maxLength) {
    processedContent = content.substring(content.length - maxLength);
  }
  
  // 替换 ANSI 颜色代码为 HTML 标签
  let formattedContent = processedContent;
  
  // 匹配 ANSI 颜色代码模式 (优化正则表达式性能)
  formattedContent = formattedContent.replace(/\u001b\[(\d+)m(.*?)\u001b\[0m/g, (match, colorCode, text) => {
    const color = ansiColorMap[colorCode];
    if (color) {
      return `<span style="color: ${color};">${text}</span>`;
    }
    return text;
  });
  
  // 处理粗体文本
  formattedContent = formattedContent.replace(/\u001b\[1m(.*?)\u001b\[0m/g, '<strong>$1</strong>');
  
  // 如果原始内容被截断，添加提示信息
  if (content.length > maxLength) {
    return `<span style="color: #FFA500;">[log content truncated, only showing latest part]</span>\n${formattedContent}`;
  }
  
  return formattedContent;
};

// 格式化日志文件名，只显示日期部分
const formatLogFileName = (filename) => {
  // 假设文件名格式为 app_YYYY-MM-DD.log
  const dateMatch = filename.match(/app_(\d{4}-\d{2}-\d{2})\.log/);
  if (dateMatch && dateMatch[1]) {
    return dateMatch[1]; // 只返回日期部分 YYYY-MM-DD
  }
  // 如果不匹配格式，返回原文件名
  return filename;
};

// 获取今天的日期，用于识别当日日志文件
const getTodayLogFileName = () => {
  const today = new Date().toISOString().split('T')[0];
  return `app_${today}.log`;
};

// 判断是否为当日日志文件
const isTodayLogFile = (filename) => {
  return filename === getTodayLogFileName();
};

// 获取日志文件列表
const fetchLogFiles = async () => {
  try {
    const files = await getLogFiles()
    logFiles.value = files
    
    // 默认选择最新的日志文件
    if (files.length > 0) {
      formState.selectedFile = files[0]
      await loadLogContent(files[0])
    }
  } catch (error) {
    console.error(t.value('getLogFilesFailed'), error)
    Message.error(`${t.value('getLogFilesFailed')}: ${error.message || t.value('unknownError')}`)
  }
}

// 加载日志内容并滚动到底部
const loadLogContent = async (filename) => {
  try {
    if (!filename) return
    
    const response = await getLogContent(filename)
    logContent.value = response.content
    
    // 在DOM更新后滚动到底部
    await nextTick()
    scrollToBottom()
  } catch (error) {
    console.error(t.value('getLogContentFailed'), error)
    Message.error(`${t.value('getLogContentFailed')}: ${error.message || t.value('unknownError')}`)
    logContent.value = ''
  }
}

// 滚动到底部
const scrollToBottom = () => {
  if (logContentRef.value) {
    logContentRef.value.scrollTop = logContentRef.value.scrollHeight
  }
}

// 页面可见性处理函数
const handleVisibilityChange = () => {
  if (document.hidden) {
    // 页面隐藏时，停止自动刷新
    if (refreshInterval.value) {
      clearInterval(refreshInterval.value)
      refreshInterval.value = null
    }
  } else {
    // 页面显示时，如果启用了自动刷新则重新启动
    if (autoRefreshEnabled.value && !refreshInterval.value) {
      toggleAutoRefresh()
    }
  }
}

// 切换自动刷新
const toggleAutoRefresh = () => {
  // 清除现有的定时器
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
    refreshInterval.value = null
  }
  
  if (autoRefreshEnabled.value) {
    // 启动自动刷新，每5秒刷新一次
    refreshInterval.value = setInterval(() => {
      if (formState.selectedFile && !document.hidden) {
        loadLogContent(formState.selectedFile)
      }
    }, 5000)
  }
}

// 显示清理日志确认对话框
const showClearLogsModal = () => {
  clearLogsModalVisible.value = true
}

// 取消清理日志
const cancelClearLogs = () => {
  clearLogsModalVisible.value = false
}

// 清理日志
const handleClearLogs = async () => {
  try {
    const response = await clearLogsApi()
    // 使用后端返回的消息，因为它包含了更详细的信息（包括当日日志未被清理的提示）
    Message.success(response.message || t.value('clearLogsSuccess'))
    
    // 关闭对话框
    clearLogsModalVisible.value = false
    
    // 重新获取日志文件列表
    await fetchLogFiles()
    
    // 清空当前日志内容
    logContent.value = ''
  } catch (error) {
    console.error(t.value('clearLogsFailed'), error)
    Message.error(`${t.value('clearLogsFailed')}: ${error.message || t.value('unknownError')}`)
    
    // 关闭对话框
    clearLogsModalVisible.value = false
  }
}

// 显示删除指定日志文件确认对话框
const showDeleteLogFileModal = (filename) => {
  selectedLogFile.value = filename
  deleteLogFileModalVisible.value = true
}

// 取消删除指定日志文件
const cancelDeleteLogFile = () => {
  deleteLogFileModalVisible.value = false
  selectedLogFile.value = ''
}

// 删除指定日志文件
const handleDeleteLogFile = async () => {
  try {
    const response = await clearLogFileApi(selectedLogFile.value)
    Message.success(response.message || t.value('deleteLogFileSuccess'))
    
    // 关闭对话框
    deleteLogFileModalVisible.value = false
    selectedLogFile.value = ''
    
    // 重新获取日志文件列表
    await fetchLogFiles()
    
    // 如果删除的是当前选中的文件，清空日志内容
    if (formState.selectedFile === selectedLogFile.value) {
      logContent.value = ''
      formState.selectedFile = ''
    }
  } catch (error) {
    console.error(t.value('deleteLogFileFailed'), error)
    Message.error(`${t.value('deleteLogFileFailed')}: ${error.message || t.value('unknownError')}`)
    
    // 关闭对话框
    deleteLogFileModalVisible.value = false
    selectedLogFile.value = ''
  }
}

// 导出日志文件
const handleExportLogFile = async (filename) => {
  try {
    if (!filename) {
      Message.warning(t.value('pleaseSelectLogFile'))
      return
    }

    // 禁止导出当日日志文件
    if (isTodayLogFile(filename)) {
      Message.warning(t.value('cannotExportTodayFile'))
      return
    }

    // 显示加载提示
    const loading = Message.loading(t.value('exportingLogFile'))

    const response = await exportLogFile(filename)

    // 创建下载链接
    const blob = new Blob([response], { type: 'application/octet-stream' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()

    // 清理
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    // 关闭加载提示并显示成功消息
    loading.close()
    Message.success(t.value('exportLogFileSuccess'))

  } catch (error) {
    console.error(t.value('exportLogFileFailed'), error)
    Message.error(`${t.value('exportLogFileFailed')}: ${error.message || t.value('unknownError')}`)
  }
}

// 组件挂载时获取日志文件列表并启动自动刷新
onMounted(() => {
  fetchLogFiles().then(() => {
    // 默认启动自动刷新
    toggleAutoRefresh()
  })
  
  // 添加页面可见性监听器
  pageVisibilityHandler.value = handleVisibilityChange
  document.addEventListener('visibilitychange', pageVisibilityHandler.value)
})

// 组件卸载时清理定时器和事件监听器
onUnmounted(() => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
  }
  
  // 移除页面可见性监听器
  if (pageVisibilityHandler.value) {
    document.removeEventListener('visibilitychange', pageVisibilityHandler.value)
  }
})
</script>

<style scoped>
.logs-container {
  padding: 20px;
  overflow-x: hidden; /* 隐藏水平滚动条 */
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 15px;
  font-size: 1.3em;
  padding: 20px 20px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  flex-wrap: wrap; /* 允许换行 */
}

.title {
  margin: 0;
  padding: 0;
  white-space: nowrap;
}

/* 自动刷新开关样式 */
.auto-refresh {
  display: flex;
  align-items: center;
  gap: 5px;
  margin-right: auto; /* 将开关推到左侧 */
}

/* 表单和清理按钮在标题行的样式 */
.header-form {
  display: flex;
  align-items: center;
  gap: 10px; /* 减小间距 */
  flex-shrink: 0; /* 防止压缩 */
}

.action-buttons {
  display: flex;
  align-items: center;
  gap: 8px;
}

:deep(.form-item-inline) {
  margin-bottom: 0;
}

:deep(.form-item-inline .arco-form-item-label) {
  text-align: left;
  padding-right: 10px;
  white-space: nowrap;
  align-self: center;
}

:deep(.arco-select-view) {
  align-self: center;
  width: 200px;
}

.content-area {
  margin-top: 20px;
}

.log-content-card {
  margin-top: 20px;
}

.log-content {
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 16px; /* 从14px调整为16px，进一步增大字体 */
  line-height: 1.4;
  margin: 0;
  padding: 15px;
  background-color: #000000; /* 黑色背景 */
  color: #ffffff; /* 白色字体 */
  border-radius: 4px;
  max-height: 600px;
  overflow-y: auto;
}

/* 日志文件选项样式 */
.log-file-option-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.file-actions {
  display: flex;
  align-items: center;
  gap: 4px;
}

.export-icon {
  color: #1890ff;
  cursor: pointer;
  font-size: 14px;
}

.export-icon:hover {
  color: #40a9ff;
}

.delete-icon {
  color: #ff4d4f;
  cursor: pointer;
  font-size: 14px;
}

.delete-icon:hover {
  color: #ff7875;
}

/* 移动端日志内容适配 */
@media (max-width: 768px) {
  .log-content {
    font-size: 15px; /* 移动端字体稍小 */
    padding: 10px;
    max-height: 400px;
  }
}

@media (max-width: 480px) {
  .log-content {
    font-size: 14px; /* 小屏幕设备字体最小 */
    padding: 8px;
    max-height: 300px;
  }
}

/* 响应式设计 - 中等屏幕 */
@media (max-width: 768px) {
  .logs-container {
    padding: 10px;
  }
  
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
    padding: 15px;
  }
  
  .auto-refresh {
    margin-right: 0;
  }
  
  .header-form {
    width: 100%;
    justify-content: space-between;
  }
  
  :deep(.arco-select-view) {
    width: 120px;
  }
  
  :deep(.arco-button) {
    font-size: 12px;
    padding: 0 12px;
  }
}

/* 响应式设计 - 小屏幕 */
@media (max-width: 480px) {
  .card-header {
    gap: 8px;
    padding: 12px;
  }
  
  .header-form {
    gap: 8px;
    width: 100%;
  }
  
  :deep(.form-item-inline) {
    width: 100%;
  }
  
  :deep(.arco-select-view) {
    width: 100%;
  }
  
  .action-buttons {
    width: 100%;
    justify-content: flex-end;
  }
  
  :deep(.arco-button) {
    font-size: 11px;
    padding: 0 10px;
  }
  
  .title {
    font-size: 1.1em;
  }
}
</style>

<!-- 使用非scoped样式确保在所有主题下保持一致 -->
<style>
/* 确保卡片容器在所有主题下保持白色背景 */
.logs-container :deep(.arco-card) {
  background: #ffffff !important;
  border: 1px solid #ebebeb !important;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05) !important;
}

/* 确保表单标签在所有主题下保持黑色文字 */
.logs-container :deep(.arco-form-item-label) {
  color: #333 !important;
}

/* 确保选择框在所有主题下保持白色背景 */
.logs-container :deep(.arco-select-view) {
  background-color: #ffffff !important;
  border-color: #ebebeb !important;
  color: #333 !important;
}

.logs-container :deep(.arco-select-view:hover) {
  background-color: #ffffff !important;
  border-color: #cccccc !important;
}

.logs-container :deep(.arco-select-view:focus) {
  background-color: #ffffff !important;
  border-color: #3c7eff !important;
  box-shadow: 0 0 0 2px rgba(64, 132, 255, 0.2) !important;
}

.logs-container :deep(.arco-select-view-single .arco-select-view-input) {
  color: #333 !important;
}

.logs-container :deep(.arco-select-view-single .arco-select-view-input::placeholder) {
  color: #999 !important;
}

/* 移动端全局样式适配 */
@media (max-width: 768px) {
  .logs-container :deep(.arco-card) {
    box-shadow: none !important;
  }
  
  .logs-container :deep(.arco-form-item-label) {
    font-size: 12px;
  }
  
  .logs-container :deep(.arco-select-view) {
    font-size: 12px;
  }
}

@media (max-width: 480px) {
  .logs-container :deep(.arco-card) {
    border: none !important;
    border-radius: 0 !important;
  }
  
  .logs-container :deep(.arco-form-item-label) {
    font-size: 11px;
  }
  
  .logs-container :deep(.arco-select-view) {
    font-size: 11px;
  }
}
</style>
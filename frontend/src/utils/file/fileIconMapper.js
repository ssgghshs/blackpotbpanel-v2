import { 
  IconFolder, 
  IconFile,
  IconMosaic,
  IconCodeSquare,
  IconCode,
  IconCodeBlock
} from '@arco-design/web-vue/es/icon';
import * as AntdIcons from '@ant-design/icons-vue';

/**
 * 获取文件图标组件
 * @param {Object} record - 文件记录对象
 * @param {boolean} record.is_directory - 是否为目录
 * @param {string} record.filename - 文件名
 * @returns {Component} 图标组件
 */
export const getFileIcon = (record) => {
  // 添加对 record 和 filename 的检查
  if (!record) {
    return IconFile;
  }
  
  if (record.is_directory) {
    return IconFolder;
  }
  
  // 确保 filename 存在且为字符串
  const fileName = record.filename && typeof record.filename === 'string' 
    ? record.filename.toLowerCase() 
    : '';

  // 压缩文件
  if (fileName.endsWith('.zip') || fileName.endsWith('.tar.gz') || fileName.endsWith('.tar') || 
      fileName.endsWith('.gz') || fileName.endsWith('.rar') || fileName.endsWith('.7z') || 
      fileName.endsWith('.tar.bz2') || fileName.endsWith('.tar.xz') || fileName.endsWith('.tgz')) {
    return AntdIcons.FileZipOutlined;
  }
  
  // 图片文件
  if (fileName.endsWith('.jpg') || fileName.endsWith('.jpeg')) {
    return AntdIcons.FileJpgOutlined;
  }
  
  if (fileName.endsWith('.png') || fileName.endsWith('.gif') || fileName.endsWith('.bmp') || 
      fileName.endsWith('.webp') || fileName.endsWith('.svg') || fileName.endsWith('.ico')) {
    return IconMosaic;
  }
  
  // 文档文件
  if (fileName.endsWith('.pdf')) {
    return AntdIcons.FilePdfOutlined;
  }
  
  if (fileName.endsWith('.doc') || fileName.endsWith('.docx')) {
    return AntdIcons.FileWordOutlined;
  }
  
  if (fileName.endsWith('.xls') || fileName.endsWith('.xlsx')) {
    return AntdIcons.FileExcelOutlined;
  }
  
  if (fileName.endsWith('.ppt') || fileName.endsWith('.pptx')) {
    return AntdIcons.FilePptOutlined;
  }
  
  // 代码文件
  if (fileName.endsWith('.js') || fileName.endsWith('.ts') || fileName.endsWith('.jsx') || fileName.endsWith('.tsx') ||
      fileName.endsWith('.java') || fileName.endsWith('.c') || fileName.endsWith('.cpp') || fileName.endsWith('.h') ||
      fileName.endsWith('.php') || fileName.endsWith('.rb') || fileName.endsWith('.go') || fileName.endsWith('.rs') ||
      fileName.endsWith('.pl') || fileName.endsWith('.lua') || fileName.endsWith('.tcl') || fileName.endsWith('.sql') ||
      fileName.endsWith('.py') || fileName.endsWith('.sh') || fileName.endsWith('.bat') || fileName.endsWith('.ps1') ||
      fileName.endsWith('.cs') || fileName.endsWith('.swift') || fileName.endsWith('.kt') || fileName.endsWith('.dart') || 
      fileName.endsWith('.r') || fileName.endsWith('.scala') || fileName.endsWith('.groovy')) {
    return IconCodeSquare;
  }
  
  // HTML和XML文件
  if (fileName.endsWith('.html') || fileName.endsWith('.htm') || fileName.endsWith('.xml') || fileName.endsWith('.vue')) {
    return IconCode;
  }
  
  if (fileName.endsWith('.json')) {
    return IconCodeBlock;
  }
  
  // 音频文件
  if (fileName.endsWith('.mp3') || fileName.endsWith('.wav') || fileName.endsWith('.flac') || 
      fileName.endsWith('.aac') || fileName.endsWith('.ogg')) {
    return AntdIcons.AudioOutlined;
  }
  
  // 视频文件
  if (fileName.endsWith('.mp4') || fileName.endsWith('.avi') || fileName.endsWith('.mkv') || 
      fileName.endsWith('.mov') || fileName.endsWith('.wmv') || fileName.endsWith('.flv')) {
    return AntdIcons.VideoCameraOutlined;
  }
  
  // 文本文件
  if (fileName.endsWith('.txt') || fileName.endsWith('.md') || fileName.endsWith('.log') || 
      fileName.endsWith('.conf') || fileName.endsWith('.cfg') || fileName.endsWith('.ini') ||
      fileName.endsWith('.yaml') || fileName.endsWith('.yml') || fileName.endsWith('.csv') || fileName.endsWith('.css')) {
    return AntdIcons.FileTextOutlined;
  }
  
  // 脚本文件（没有后缀的可执行文件）
  if (!fileName.includes('.')) {
    const executableScripts = [
      'install', 'configure', 'make', 'build', 'run', 'start', 'stop', 
      'restart', 'setup', 'init', 'deploy', 'test', 'clean', 'compile',
      'update', 'upgrade', 'backup', 'restore', 'migrate', 'generate',
      'create', 'delete', 'sync', 'watch', 'serve', 'dev', 'prod',
      'debug', 'release', 'package', 'publish', 'unpublish', 'login',
      'logout', 'register', 'reset', 'verify', 'import', 'export'
    ];
    
    if (executableScripts.includes(fileName)) {
      return AntdIcons.FileTextOutlined;
    }
    
    return AntdIcons.FileTextOutlined;
  }
  
  return IconFile;
};

/**
 * 获取文件图标颜色
 * @param {Object} record - 文件记录对象
 * @param {boolean} record.is_directory - 是否为目录
 * @param {string} record.filename - 文件名
 * @returns {string} 颜色值
 */
export const getFileIconColor = (record) => {
  // 添加对 record 的检查
  if (!record) {
    return '#9E9E9E';
  }
  
  if (record.is_directory) {
    return '#FFB300';
  }
  
  // 确保 filename 存在且为字符串
  const fileName = record.filename && typeof record.filename === 'string' 
    ? record.filename.toLowerCase() 
    : '';
  
  // 代码或文本文件
  if (fileName.endsWith('.js') || fileName.endsWith('.ts') || fileName.endsWith('.jsx') || fileName.endsWith('.tsx') ||
      fileName.endsWith('.java') || fileName.endsWith('.c') || fileName.endsWith('.cpp') || fileName.endsWith('.h') ||
      fileName.endsWith('.php') || fileName.endsWith('.rb') || fileName.endsWith('.go') || fileName.endsWith('.rs') ||
      fileName.endsWith('.pl') || fileName.endsWith('.lua') || fileName.endsWith('.tcl') || fileName.endsWith('.sql') ||
      fileName.endsWith('.py') || fileName.endsWith('.sh') || fileName.endsWith('.bat') || fileName.endsWith('.ps1') ||
      fileName.endsWith('.cs') || fileName.endsWith('.swift') || fileName.endsWith('.kt') || fileName.endsWith('.dart') || 
      fileName.endsWith('.r') || fileName.endsWith('.scala') || fileName.endsWith('.groovy') ||
      fileName.endsWith('.txt') || fileName.endsWith('.md') || fileName.endsWith('.log') || 
      fileName.endsWith('.conf') || fileName.endsWith('.cfg') || fileName.endsWith('.ini') ||
      fileName.endsWith('.yaml') || fileName.endsWith('.yml') || fileName.endsWith('.csv') || fileName.endsWith('.css') ||
      fileName.endsWith('.json') || fileName.endsWith('.env') || fileName.endsWith('.config') || fileName.endsWith('.vue')) {
    return '#9E9E9E';
  }
  
  // HTML和XML文件
  if (fileName.endsWith('.html') || fileName.endsWith('.htm') || fileName.endsWith('.xml')) {
    return '#4CAF50';
  }
  
  // 图片文件
  if (fileName.endsWith('.jpg') || fileName.endsWith('.jpeg') || fileName.endsWith('.png') || 
      fileName.endsWith('.gif') || fileName.endsWith('.bmp') || fileName.endsWith('.webp') || 
      fileName.endsWith('.svg') || fileName.endsWith('.ico')) {
    return '#2196F3';
  }
  
  // 压缩文件
  if (fileName.endsWith('.zip') || fileName.endsWith('.tar.gz') || fileName.endsWith('.tar') || 
      fileName.endsWith('.gz') || fileName.endsWith('.rar') || fileName.endsWith('.7z') || fileName.endsWith('.tgz')) {
    return '#FF9800';
  }
  
  // 文档文件
  if (fileName.endsWith('.pdf') || fileName.endsWith('.doc') || fileName.endsWith('.docx') ||
      fileName.endsWith('.xls') || fileName.endsWith('.xlsx') || fileName.endsWith('.ppt') || 
      fileName.endsWith('.pptx')) {
    return '#F44336';
  }
  
  // 音频文件
  if (fileName.endsWith('.mp3') || fileName.endsWith('.wav') || fileName.endsWith('.flac') || 
      fileName.endsWith('.aac') || fileName.endsWith('.ogg')) {
    return '#9C27B0';
  }
  
  // 视频文件
  if (fileName.endsWith('.mp4') || fileName.endsWith('.avi') || fileName.endsWith('.mkv') || 
      fileName.endsWith('.mov') || fileName.endsWith('.wmv') || fileName.endsWith('.flv')) {
    return '#E91E63';
  }
  
  // 脚本文件（没有后缀的可执行文件）
  if (!fileName.includes('.')) {
    const executableScripts = [
      'install', 'configure', 'make', 'build', 'run', 'start', 'stop', 
      'restart', 'setup', 'init', 'deploy', 'test', 'clean', 'compile',
      'update', 'upgrade', 'backup', 'restore', 'migrate', 'generate',
      'create', 'delete', 'sync', 'watch', 'serve', 'dev', 'prod',
      'debug', 'release', 'package', 'publish', 'unpublish', 'login',
      'logout', 'register', 'reset', 'verify', 'import', 'export'
    ];
    
    if (executableScripts.includes(fileName)) {
      return '#9E9E9E';
    }
    
    return '#9E9E9E';
  }
  
  return '#9E9E9E';
};

/**
 * 检查文件是否为图片格式
 * @param {string} filename - 文件名
 * @returns {boolean}
 */
export const isImageFile = (filename) => {
  if (!filename || typeof filename !== 'string') {
    return false;
  }
  
  const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.ico'];
  const lowerFilename = filename.toLowerCase();
  return imageExtensions.some(ext => lowerFilename.endsWith(ext));
};

/**
 * 检查文件是否为压缩文件
 * @param {string} filename - 文件名
 * @returns {boolean}
 */
export const isCompressedFile = (filename) => {
  if (!filename || typeof filename !== 'string') {
    return false;
  }
  
  const compressedExtensions = ['.zip', '.tar', '.tar.gz', '.gz', '.rar', '.7z', '.tgz'];
  const lowerFilename = filename.toLowerCase();
  return compressedExtensions.some(ext => lowerFilename.endsWith(ext));
};

/**
 * 检查文件是否可以打开编辑
 * @param {string} filename - 文件名
 * @returns {boolean}
 */
export const canOpenFile = (filename) => {
  if (!filename || typeof filename !== 'string') {
    return false;
  }
  
  return true;
};
import request from '../utils/request'

// Firewall API

// 获取防火墙统计信息


// 进程相关API

// 获取进程列表
export function processesGet(params) {
    return request({
        url: '/service/processes',
        method: 'get',
        params
    })
}

// 获取进程详情
export function processGetDetail(pid) {
    return request({
        url: `/service/process/${pid}`,
        method: 'get'
    })
}

// 终止进程
export function processTerminate(pid) {
    return request({
        url: `/service/process/${pid}/terminate`,
        method: 'post'
    })
}

// 获取网络连接列表
export function networkGetConnections(params) {
    return request({
        url: '/service/network/connections',
        method: 'get',
        params
    })
}

// 获取系统信息，包括DNS地址、内存信息、Swap信息、时区、当前时间和主机名
export function systemInfoGet() {
    return request({
        url: '/service/info',
        method: 'get'
    })
}
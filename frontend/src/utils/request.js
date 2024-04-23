import axios from 'axios';

const request = axios.create({
    baseURL: 'http://127.0.0.1:5000/',
    timeout: 210000
})

request.interceptors.request.use(config => {
    // 只有在不是 'multipart/form-data' 的情况下才设置 'Content-Type' 为 'application/json'
    if (!config.headers['Content-Type'] || config.headers['Content-Type'].indexOf('multipart/form-data') === -1) {
        config.headers['Content-Type'] = 'application/json;charset=UTF-8';
    }
    return config;
}, error => {
    return Promise.reject(error);
});


request.interceptors.response.use(
    response => {
        let res = response.data;
        if (typeof res === 'string') {
            res = res ? JSON.parse(res) : res;
        }
        return res;
    },
    error => {
        console.log('err', error);
        return Promise.reject(error);
    }
)

export default request;

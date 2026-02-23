// 将num左补0为len长度的字符串
export function lpadNum(num, len) {
    return num.toString().padStart(len, "0");
}

// 将传入的Date格式化为"yyyy-MM-dd HH:mm:ss"
export function formatDate(d) {
    if (!(d instanceof Date) || isNaN(d.getTime())) {
        console.error("Invalid Date:", d);
        return "Invalid Date";
    }

    const year = d.getFullYear();
    const month = lpadNum(d.getMonth() + 1, 2);
    const day = lpadNum(d.getDate(), 2);
    const hours = lpadNum(d.getHours(), 2);
    const minutes = lpadNum(d.getMinutes(), 2);
    const seconds = lpadNum(d.getSeconds(), 2);

    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}

// 字符串转换为时间
export function parseDate(str) {
    if (typeof str !== "string") {
        console.error("Invalid Date String:", str);
        return new Date(NaN);
    }
    const date = new Date(str.replace(/-/g, "/"));
    if (isNaN(date.getTime())) {
        console.error("Invalid Date String:", str);
        return new Date(NaN);
    }
    return date;
}

// 获取指定时间的对象
export function getDateObj(d) {
    if (!(d instanceof Date) || isNaN(d.getTime())) {
        console.error("Invalid Date Object:", d);
        return null;
    }
    return {
        year: d.getFullYear(),
        month: d.getMonth() + 1,
        day: d.getDate(),
        hour: d.getHours(),
        minute: d.getMinutes(),
        second: d.getSeconds(),
    };
}

// 比较两个数字的大小
export function contrastNums(num1, num2) {
    return num1 < num2 ? -1 : num1 > num2 ? 1 : 0;
}

// 指定时间和当前时间对比
export function contrastNow(str) {
    const time1 = getDateObj(parseDate(str));
    const time2 = getDateObj(new Date());

    if (!time1 || !time2) {
        console.error("Invalid Date Comparison");
        return null;
    }

    const keys = ["year", "month", "day", "hour", "minute"];
    for (const key of keys) {
        const comparison = contrastNums(time1[key], time2[key]);
        if (comparison !== 0) return comparison;
    }
    return 0;
}

// 倒计时
export function countDown(startTime, endTime) {
    const startDate = parseDate(startTime);
    const endDate = parseDate(endTime);

    if (isNaN(startDate.getTime()) || isNaN(endDate.getTime())) {
        console.error("Invalid Start or End Time:", startTime, endTime);
        return null;
    }

    const diff = Math.max(0, endDate - startDate); // 确保不为负值
    return {
        h: Math.floor(diff / 1000 / 60 / 60),
        m: Math.floor((diff / 1000 / 60) % 60),
        s: Math.floor((diff / 1000) % 60),
    };
}

// 格式化倒计时
export function formatCountDown(h, m, s) {
    return `${lpadNum(h, 2)}:${lpadNum(m, 2)}:${lpadNum(s, 2)}`;
}

// 判断倒计时是否达到
export function contrastCountDown(h, m, s) {
    return h === 0 && m === 0 && s === 0;
}

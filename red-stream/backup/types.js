// Type Guards
export function isGetStreamMessagesArgs(obj) {
    return typeof obj === 'object' &&
        obj !== null &&
        'stream' in obj &&
        typeof obj.stream === 'string';
}
export function isAddStreamMessageArgs(obj) {
    return typeof obj === 'object' &&
        obj !== null &&
        'stream' in obj &&
        typeof obj.stream === 'string' &&
        'message' in obj &&
        typeof obj.message === 'object';
}
export function isListStreamsArgs(obj) {
    return typeof obj === 'object' &&
        obj !== null &&
        (!('pattern' in obj) || typeof obj.pattern === 'string');
}

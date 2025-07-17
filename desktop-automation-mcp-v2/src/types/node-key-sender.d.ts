declare module 'node-key-sender' {
    interface KeySender {
        sendKey(key: string): Promise<void>;
        sendKeys(keys: string[]): Promise<void>;
        sendText(text: string): Promise<void>;
    }
    const keySender: KeySender;
    export default keySender;
}
import { createParamDecorator, type ExecutionContext } from "@nestjs/common";

export class ClientInfo {
    public ipAddress!: string;
    public userAgent!: string;
}

export const Client = createParamDecorator(
    (data: keyof ClientInfo | undefined, context: ExecutionContext) => {
    const request = context.switchToHttp().getRequest();

    const ipAddress =
        request.ip ||
        request.socket?.remoteAddress ||
        "";

    const userAgent = request.get("user-agent") || "";

    const clientInfo = new ClientInfo();

    clientInfo.ipAddress = ipAddress;
    clientInfo.userAgent = userAgent;

    return data ? clientInfo[data] : clientInfo;
});

import {
    type ArgumentsHost,
    Catch,
    type ExceptionFilter,
    HttpException,
    HttpStatus
} from "@nestjs/common";

import { STATUS_CODES } from "node:http";

@Catch()
export class GlobalExceptionFilter implements ExceptionFilter {
    public catch(exception: unknown, host: ArgumentsHost): void {
        console.error(exception);
        const ctx = host.switchToHttp();

        const response = ctx.getResponse();

        let status = HttpStatus.INTERNAL_SERVER_ERROR;

        let message = "Internal server error.";

        if (exception instanceof HttpException) {
            status = exception.getStatus();

            const exceptionResponse = exception.getResponse();

            if (typeof exceptionResponse === "string") {
                message = exceptionResponse;
            } else if (
                typeof exceptionResponse === "object" &&
                exceptionResponse !== null
            ) {
                const body = exceptionResponse as any;

                if (typeof body.message === "string") {
                    message = body.message;
                } else if (Array.isArray(body.message)) {
                    message = body.message.join(", ");
                }
            }
        }

        response.status(status).json({
            status,
            error: STATUS_CODES[status] ?? "Error",
            message
        });

    }
}


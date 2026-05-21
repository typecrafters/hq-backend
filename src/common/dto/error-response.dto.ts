import { AppResponse } from "./app-response.dto";

export class ErrorResponse extends AppResponse {
    public error!: string;

    constructor(status?: number) {
        super(status);
    }

    public static BadRequest(): ErrorResponse {
        return new ErrorResponse(400);
    }

    public static NotFound(): ErrorResponse {
        return new ErrorResponse(404);
    }

    public static NotAcceptable(): ErrorResponse {
        return new ErrorResponse(406);
    }

    public static Gone(): ErrorResponse {
        return new ErrorResponse(410);
    }

    public static UnsupportedMediaType(): ErrorResponse {
        return new ErrorResponse(415);
    }

    public static UnprocessableContent(): ErrorResponse {
        return new ErrorResponse(422);
    }

    public static InternalServerError(): ErrorResponse {
        return new ErrorResponse(500);
    }
}
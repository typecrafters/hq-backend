import { IsInt, IsNotEmpty, IsString, Max, Min } from "class-validator";

export class ErrorResponse {
    @Min(100)
    @Max(599)
    @IsNotEmpty()
    @IsInt()
    public status!: number;

    @IsString()
    @IsNotEmpty()
    public message!: string;

    @IsString()
    @IsNotEmpty()
    public error!: string;

    constructor(status?: number) {
        if (status) this.status = status;
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
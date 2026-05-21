import { AppResponse } from "./app-response.dto";
import type { ResponseMetadata } from "./response-metadata.dto";

export class ListResponse<T> extends AppResponse {
    public data!: Array<T>;
    public meta?: ResponseMetadata;

    constructor(status?: number) {
        super(status);
    }

    public static OK<T>(): ListResponse<T> {
        return new ListResponse(200);
    }

    public static Created<T>(): ListResponse<T> {
        return new ListResponse(201);
    }

    public static Accepted<T>(): ListResponse<T> {
        return new ListResponse(202);
    }
}
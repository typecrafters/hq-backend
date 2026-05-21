import { AppResponse } from "./app-response.dto";
import type { ResponseMetadata } from "./response-metadata.dto";


export class ItemResponse<T> extends AppResponse {
    public data!: T;
    public meta?: ResponseMetadata;

    constructor(status?: number) {
        super(status);
    }

    public static OK<T>(): ItemResponse<T> {
        return new ItemResponse(200);
    }

    public static Created<T>(): ItemResponse<T> {
        return new ItemResponse(201);
    }

    public static Accepted<T>(): ItemResponse<T> {
        return new ItemResponse(202);
    }
}
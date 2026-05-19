import { IsInt, IsNotEmpty, IsOptional, IsString, Max, Min, ValidateNested } from "class-validator";
import type { ResponseMetadata } from "./response-metadata.dto";
import { Type } from "class-transformer";

export class ListResponse<T> {
    @Min(100)
    @Max(599)
    @IsNotEmpty()
    @IsInt()
    public status!: number;

    @IsString()
    @IsNotEmpty()
    public message!: string;

    @ValidateNested({ each: true })
    @IsNotEmpty()
    public data!: Array<T>;

    @ValidateNested()
    @Type(() => Object)
    @IsOptional()
    public meta?: ResponseMetadata;

    constructor(status?: number) {
        if (status) this.status = status;
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